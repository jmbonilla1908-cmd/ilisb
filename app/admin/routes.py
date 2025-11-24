from flask import render_template, redirect, url_for, flash, request, make_response
from flask_login import login_user, logout_user, current_user
from werkzeug.exceptions import NotFound
from werkzeug.utils import secure_filename
from app import db
from app.admin import bp
from app.admin.decorators import admin_required, superuser_required # type: ignore
from app.admin.forms import AdminLoginForm, DocenteForm, AlumnoForm, GrupoForm, CursoForm, AdminUserForm, ModuloForm, ItemTemarioForm, HorarioForm, PaisHorarioForm, DeleteForm
from app.admin.models import User
from app.cursos.models import Curso, Docente, Grupo, Modulo, ItemTemario, Horario, PaisHorario
from app.auth.models import Alumno, AlumnoMembresia, Membresia
import secrets
import os
from datetime import datetime, timezone
from slugify import slugify


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login específico para administradores"""
    if current_user.is_authenticated and current_user.get_id().startswith('admin_'):
        return redirect(url_for('admin.dashboard'))
    
    form = AdminLoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Usuario o contraseña inválidos', 'danger')
            return render_template(
                'admin/login.html', title='Admin Login', form=form
            ), 422
        
        if not user.is_active:
            flash('Su cuenta está desactivada', 'danger')
            return render_template(
                'admin/login.html', title='Admin Login', form=form
            ), 422

        login_user(user, remember=form.remember_me.data)
        # Actualizar último login
        from datetime import datetime
        user.last_login = datetime.now(timezone.utc)
        db.session.commit()
        
        flash(f'Bienvenido, {user.full_name}', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/login.html', title='Admin Login', form=form)


@bp.route('/')
@admin_required
def index():
    """Ruta raíz del admin que redirige al dashboard"""
    return redirect(url_for('admin.dashboard'))


@bp.route('/logout')
@admin_required
def logout():
    """Logout específico para administradores"""
    logout_user()
    flash('Sesión de administrador cerrada', 'info')
    return redirect(url_for('core.index'))


@bp.route('/dashboard')
@admin_required
def dashboard():
    """Panel de administración principal"""
    # Obtener estadísticas básicas
    total_users = User.query.count()
    total_cursos = Curso.query.count()
    
    stats = {
        'total_users': total_users,
        'total_cursos': total_cursos,
        'admin_user': current_user
    }
    
    return render_template('admin/dashboard.html', 
                         title='Panel de Administración', 
                         stats=stats)


@bp.route('/users')
@admin_required  
def users():
    """Gestión de usuarios administradores"""
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.id.asc()).paginate(
        page=page, per_page=15, error_out=False
    )
    return render_template('admin/users.html', 
                         title='Gestión de Usuarios', pagination=pagination)

@bp.route('/user/nuevo', methods=['GET', 'POST'])
@superuser_required
def nuevo_usuario():
    """Crear un nuevo usuario administrador."""
    form = AdminUserForm()
    if form.validate_on_submit():
        # Dividimos el nombre completo en nombre y apellido
        full_name_parts = form.full_name.data.split(' ', 1)
        first_name = full_name_parts[0]
        last_name = full_name_parts[1] if len(full_name_parts) > 1 else ''

        user = User(
            username=form.username.data,
            first_name=first_name,
            last_name=last_name,
            email=form.email.data,
            is_active=form.is_active.data,
            is_superuser=form.is_superuser.data
        )
        user.set_password(form.password.data)
        try:
            db.session.add(user)
            db.session.commit()
            flash(f'Usuario administrador "{user.username}" creado exitosamente.', 'success')
            return redirect(url_for('admin.users'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear el usuario: {e}', 'danger')
    return render_template('admin/form_user.html', title='Nuevo Administrador', form=form)

@bp.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
@superuser_required
def editar_usuario(user_id):
    """Editar un usuario administrador."""
    user = User.query.get_or_404(user_id)
    # Pasamos el objeto original para que el validador de unicidad funcione correctamente
    form = AdminUserForm(obj=user, original_username=user.username, original_email=user.email)

    if form.validate_on_submit():
        # Dividimos el nombre completo en nombre y apellido
        full_name_parts = form.full_name.data.split(' ', 1)
        user.first_name = full_name_parts[0]
        user.last_name = full_name_parts[1] if len(full_name_parts) > 1 else ''

        user.username = form.username.data
        user.email = form.email.data
        user.is_active = form.is_active.data
        
        # Solo un superadmin puede cambiar el status de superadmin
        # y no puede quitarse el superadmin a sí mismo
        if current_user.is_superuser and current_user.id != user.id:
            user.is_superuser = form.is_superuser.data

        # Actualizar contraseña solo si se proporciona una nueva
        if form.password.data:
            user.set_password(form.password.data)
        
        try:
            db.session.commit()
            flash(f'Usuario "{user.username}" actualizado exitosamente.', 'success')
            return redirect(url_for('admin.users'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el usuario: {e}', 'danger')

    return render_template('admin/form_user.html', title=f'Editar: {user.username}', form=form, user=user)

@bp.route('/user/<int:user_id>/delete', methods=['POST'])
@superuser_required
def eliminar_usuario(user_id):
    """Eliminar un usuario administrador."""
    if user_id == current_user.id:
        flash('No puedes eliminar tu propia cuenta.', 'danger')
        return redirect(url_for('admin.users'))
        
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(f'Usuario "{user.username}" eliminado exitosamente.', 'success')
    return redirect(url_for('admin.users'))

@bp.route('/cursos')
@admin_required
def cursos():
    """Muestra la lista de cursos para administración."""
    page = request.args.get('page', 1, type=int)
    pagination = Curso.query.order_by(Curso.id.asc()).paginate(
        page=page, per_page=15, error_out=False
    )
    return render_template(
        'admin/cursos.html', title='Gestión de Cursos', pagination=pagination
    )

@bp.route('/curso/nuevo', methods=['GET', 'POST'])
@admin_required
def nuevo_curso():
    """Crear un nuevo curso."""
    form = CursoForm()
    if form.validate_on_submit():
        # Procesamiento de la imagen del banner
        banner_filename = None
        if form.banner.data:
            f = form.banner.data
            # Generar un nombre de archivo seguro y único
            filename_base = secure_filename(slugify(form.nombre.data))
            filename_ext = os.path.splitext(f.filename)[1]
            banner_filename = f"{filename_base}_{secrets.token_hex(4)}{filename_ext}"
            
            # Guardar el archivo
            upload_path = os.path.join(os.getcwd(), 'app', 'static', 'img', 'cursos', banner_filename)
            f.save(upload_path)

        # Creamos el curso con los campos principales
        curso = Curso(
            nombre=form.nombre.data,
            duracion=form.duracion.data,
            texto_corto=form.texto_corto.data,
            descripcion=form.descripcion.data,
            footer=form.footer.data
        )
        # Generar slug a partir del nombre
        curso.slug = slugify(curso.nombre)
        if banner_filename:
            curso.banner = banner_filename
        
        # Añadimos los módulos y sus ítems
        for i, modulo_form in enumerate(form.modulos):
            modulo = Modulo(titulo=modulo_form.titulo.data, orden=i, curso=curso)
            for j, item_form in enumerate(modulo_form.items):
                ItemTemario(contenido=item_form.contenido.data, orden=j, modulo=modulo)

        try:
            db.session.add(curso)
            db.session.commit()
            flash(f'Curso "{curso.nombre}" creado exitosamente.', 'success')
            return redirect(url_for('admin.cursos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear el curso: {e}', 'danger')
    
    return render_template('admin/form_curso.html',
                           title='Nuevo Curso',
                           form=form)

@bp.route('/curso/<slug>')
@admin_required
def admin_detalle_curso(slug):
    """Muestra detalle de un curso específico para administración."""
    curso = Curso.query.filter_by(slug=slug).first()
    if curso is None:
        raise NotFound()
    # Por ahora, usamos la misma plantilla de detalle,
    # pero podrías crear una específica
    return render_template(
        'cursos/detalle_curso.html',
        title=f'Admin: {curso.nombre}',
        curso=curso
    )


@bp.route('/curso/<slug>/edit', methods=['GET', 'POST'])
@admin_required
def editar_curso(slug):
    """Editar un curso específico"""
    curso = Curso.query.options(
        db.joinedload(Curso.modulos).joinedload(Modulo.items)
    ).filter_by(slug=slug).first_or_404()

    # Si el formulario no se está enviando, lo pre-poblamos con los datos de la BD
    if not request.form:
        form = CursoForm(obj=curso)
        # Si el curso no tiene módulos, añadimos uno vacío para que la plantilla lo renderice.
        if not form.modulos.entries:
            form.modulos.append_entry()
    else:
        form = CursoForm()

    if form.validate_on_submit():
        # Rellena el objeto 'curso' con los datos validados del formulario
        # Procesamiento de la imagen del banner si se sube una nueva
        if form.banner.data:
            f = form.banner.data
            filename_base = secure_filename(slugify(form.nombre.data))
            filename_ext = os.path.splitext(f.filename)[1]
            banner_filename = f"{filename_base}_{secrets.token_hex(4)}{filename_ext}"
            
            upload_path = os.path.join(os.getcwd(), 'app', 'static', 'img', 'cursos', banner_filename)
            f.save(upload_path)
            
            # Aquí podrías añadir lógica para borrar la imagen antigua si lo deseas
            curso.banner = banner_filename

        # Actualizamos los campos principales
        curso.nombre = form.nombre.data
        curso.duracion = form.duracion.data
        curso.texto_corto = form.texto_corto.data
        curso.descripcion = form.descripcion.data
        curso.footer = form.footer.data
        # Si el nombre cambia, actualizamos el slug
        curso.slug = slugify(curso.nombre)

        # Eliminamos los módulos antiguos para reemplazarlos con los nuevos
        for modulo in curso.modulos:
            db.session.delete(modulo)
        db.session.flush()

        # Añadimos los módulos y sus ítems desde el formulario
        for i, modulo_form in enumerate(form.modulos):
            modulo = Modulo(titulo=modulo_form.titulo.data, orden=i, curso=curso)
            db.session.add(modulo)
            for j, item_form in enumerate(modulo_form.items):
                item = ItemTemario(contenido=item_form.contenido.data, orden=j, modulo=modulo)
                db.session.add(item)
        try:
            db.session.commit()
            flash(f'Curso "{curso.nombre}" actualizado exitosamente', 'success')
            # Redirigir al nuevo slug si cambió
            return redirect(url_for('admin.editar_curso', slug=curso.slug))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar curso: {str(e)}', 'danger')
    
    return render_template('admin/form_curso.html',
                           title=f'Editar: {curso.nombre}',
                           curso=curso,
                           form=form)


@bp.route('/alumnos')
@admin_required
def alumnos():
    """Gestión de alumnos"""
    page = request.args.get('page', 1, type=int)
    
    # 1. Obtenemos la paginación de alumnos de forma simple.
    pagination = Alumno.query.order_by(
        Alumno.id.asc() # Mantenemos asc, ya estaba correcto
    ).paginate(page=page, per_page=15, error_out=False)

    # 2. (nota) no necesitamos filtrar por los IDs de la página para
    #    obtener las fechas; calculamos el mapeo a partir de toda la tabla.

    # 3. Hacemos una segunda consulta para obtener la primera fecha de cada uno de esos alumnos.
    # Obtenemos la fecha de inicio más reciente (`max`) de las membresías
    # asociadas a los alumnos de la página actual. Esto devuelve el valor
    # `fecha_inicio` tal cual (no la fecha de fin ni otro campo).
    # Obtenemos la fecha de inicio (MAX) por alumno para TODO el conjunto
    # de membresías en la base de datos. Esto asegura que si un alumno tiene
    # registros en `alumno_membresia`, su `fecha_inicio` estará disponible
    # en la plantilla aunque la paginación muestre una página distinta.
    fechas_registro_query = db.session.query(
        AlumnoMembresia.alumno_id,
        db.func.min(AlumnoMembresia.fecha_inicio)
    ).group_by(AlumnoMembresia.alumno_id).all()
    mapa_de_fechas_inicio = dict(fechas_registro_query)


    # --- CÁLCULO DE ESTADÍSTICAS TOTALES ---
    # Contamos todos los alumnos con correo verificado
    activos_count = Alumno.query.filter_by(correo_verificado=True).count()

    # Contamos los IDs de alumnos distintos que tienen al menos una membresía activa
    miembros_activos_count = db.session.query(AlumnoMembresia.alumno_id).filter(
        AlumnoMembresia.revertido == False,
        AlumnoMembresia.fecha_fin >= datetime.now(timezone.utc)
    ).distinct().count()
    
    delete_form = DeleteForm()

    return render_template('admin/alumnos.html',
                           title='Gestión de Alumnos',
                           pagination=pagination,
                           mapa_de_fechas_inicio=mapa_de_fechas_inicio,
                           activos_count=activos_count,
                           miembros_activos_count=miembros_activos_count,
                           delete_form=delete_form)


@bp.route('/docentes')
@admin_required
def docentes():
    """Gestión de docentes"""
    page = request.args.get('page', 1, type=int)
    pagination = Docente.query.order_by(Docente.id.asc()).paginate( # Mantenemos asc, ya estaba correcto
        page=page, per_page=15, error_out=False
    )
    return render_template('admin/docentes.html',
                           title='Gestión de Docentes',
                           pagination=pagination)


@bp.route('/grupos')
@admin_required
def grupos():
    """Gestión de grupos"""
    page = request.args.get('page', 1, type=int)
    pagination = Grupo.query.order_by(Grupo.id.asc()).paginate( # Mantenemos asc, ya estaba correcto
        page=page, per_page=15, error_out=False
    )
    return render_template('admin/grupos.html',
                           title='Gestión de Grupos',
                           pagination=pagination)


@bp.route('/alumno/<int:alumno_id>/toggle-verificacion', methods=['POST'])
@admin_required
def toggle_verificacion_alumno(alumno_id):
    """Alternar estado de verificación de un alumno"""
    alumno = Alumno.query.get_or_404(alumno_id)
    alumno.correo_verificado = not alumno.correo_verificado
    
    try:
        db.session.commit()
        estado = "verificado" if alumno.correo_verificado else "no verificado"
        flash(f'Alumno {alumno.nombres} {alumno.apellidos} marcado como {estado}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar alumno: {str(e)}', 'danger')
    
    return redirect(url_for('admin.alumnos'))


@bp.route('/docente/<int:docente_id>/toggle-activo', methods=['POST'])
@admin_required
def toggle_activo_docente(docente_id):
    """Alternar estado activo de un docente"""
    docente = Docente.query.get_or_404(docente_id)
    # Asumiendo que existe un campo activo, si no, agregaremos lógica diferente
    try:
        # Por ahora solo mostrar que la ruta funciona
        flash(f'Función de edición ejecutada para docente: {docente.nombre}', 'info')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('admin.docentes'))


@bp.route('/grupo/<int:grupo_id>/toggle-visible', methods=['POST'])
@admin_required
def toggle_visible_grupo(grupo_id):
    """Alternar visibilidad de un grupo"""
    grupo = Grupo.query.get_or_404(grupo_id)
    grupo.visible = not grupo.visible
    
    try:
        db.session.commit()
        estado = "visible" if grupo.visible else "oculto"
        flash(f'Grupo ID {grupo.id} marcado como {estado}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar grupo: {str(e)}', 'danger')
    
    return redirect(url_for('admin.grupos'))

@bp.route('/docente/nuevo', methods=['GET', 'POST'])
@admin_required
def nuevo_docente():
    form = DocenteForm()
    if form.validate_on_submit():
        docente = Docente()
        form.populate_obj(docente)
        try:
            db.session.add(docente)
            db.session.commit()
            flash('Docente creado exitosamente.', 'success')
            return redirect(url_for('admin.docentes'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear docente: {e}', 'danger')
    return render_template('admin/form_docente.html', 
                           title='Nuevo Docente', 
                           form=form)

@bp.route('/docente/<int:docente_id>/editar', methods=['GET', 'POST'])
@admin_required
def editar_docente(docente_id):
    docente = Docente.query.get_or_404(docente_id)
    form = DocenteForm(obj=docente)
    if form.validate_on_submit():
        form.populate_obj(docente)
        try:
            db.session.commit()
            flash('Docente actualizado exitosamente.', 'success')
            return redirect(url_for('admin.docentes'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar docente: {e}', 'danger')
    return render_template('admin/form_docente.html', 
                           title='Editar Docente', 
                           form=form, 
                           docente=docente)

@bp.route('/docente/<int:docente_id>/eliminar', methods=['POST'])
@admin_required
def eliminar_docente(docente_id):
    docente = Docente.query.get_or_404(docente_id)
    try:
        db.session.delete(docente)
        db.session.commit()
        flash('Docente eliminado', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar docente: {e}', 'danger')
    return redirect(url_for('admin.docentes'))

@bp.route('/alumno/nuevo', methods=['GET', 'POST'])
@admin_required
def nuevo_alumno():
    form = AlumnoForm()
    if form.validate_on_submit():
        alumno = Alumno()
        # Rellenamos el objeto alumno con los datos validados del formulario
        form.populate_obj(alumno)
        
        # Generamos una contraseña segura si no se proporcionó una
        password = form.password.data or secrets.token_urlsafe(8)
        alumno.set_password(password)
        
        try:
            db.session.add(alumno)
            db.session.commit()
            flash(f'Alumno creado exitosamente. Password: {password}', 'success')
            return redirect(url_for('admin.alumnos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear alumno: {e}', 'danger')
            
    return render_template('admin/form_alumno.html', 
                           title='Nuevo Alumno', 
                           form=form)

@bp.route('/alumno/<int:alumno_id>/editar', methods=['GET', 'POST'])
@admin_required
def editar_alumno(alumno_id):
    alumno = Alumno.query.get_or_404(alumno_id)
    form = AlumnoForm(obj=alumno, original_email=alumno.email.lower(), alumno_obj=alumno)
    
    if form.validate_on_submit():
        alumno.nombres = form.nombres.data
        alumno.apellidos = form.apellidos.data
        alumno.email = form.email.data
        alumno.imagen = form.imagen.data
        
        # --- LÓGICA DE MEMBRESÍA UNIFICADA ---
        membresia_manual_activa = alumno.membresias.join(Membresia).filter(Membresia.nombre == 'Manual Admin').first()
        quiere_ser_miembro = form.es_miembro.data

        if quiere_ser_miembro and not membresia_manual_activa:
            # El admin quiere AÑADIR una membresía manual y no existe una.
            membresia_manual_tipo = Membresia.query.filter_by(nombre='Manual Admin').first()
            if membresia_manual_tipo:
                print(f"Concediendo membresía manual al alumno ID {alumno.id}")
                nueva_membresia = AlumnoMembresia(
                    alumno_id=alumno.id,
                    membresia_id=membresia_manual_tipo.id,
                    fecha_inicio=datetime.now(timezone.utc),
                    fecha_fin=datetime(2999, 12, 31), # Una fecha muy lejana
                    id_pago='ADMIN_GRANT',
                    monto=0
                )
                db.session.add(nueva_membresia)
        elif not quiere_ser_miembro and membresia_manual_activa:
            # El admin quiere QUITAR una membresía manual y sí existe una.
            if membresia_manual_activa:
                print(f"Revocando membresía manual del alumno ID {alumno.id}")
                db.session.delete(membresia_manual_activa)
        
        if form.password.data:
            alumno.set_password(form.password.data)
            
        try:
            db.session.commit()
            flash('Alumno actualizado exitosamente.', 'success')
            return redirect(url_for('admin.alumnos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar alumno: {e}', 'danger')

            
    return render_template('admin/form_alumno.html', 
                           title='Editar Alumno', 
                           form=form, 
                           alumno=alumno)

@bp.route('/alumno/<int:alumno_id>/eliminar', methods=['POST'])
@admin_required
def eliminar_alumno(alumno_id):
    alumno = Alumno.query.get_or_404(alumno_id)
    try:
        db.session.delete(alumno)
        db.session.commit()
        flash('Alumno eliminado', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar alumno: {e}', 'danger')
    return redirect(url_for('admin.alumnos'))

@bp.route('/alumno/<int:alumno_id>/cursos')
@admin_required
def cursos_alumno(alumno_id):
    """Muestra los cursos en los que está inscrito un alumno."""
    alumno = Alumno.query.get_or_404(alumno_id)
    # La relación 'grupos_asociados' nos da los objetos AlumnoGrupo
    # A través de ellos, podemos llegar al Grupo y luego al Curso.
    inscripciones = alumno.grupos_asociados
    return render_template('admin/cursos_alumno.html', 
                           title=f"Cursos de {alumno.nombres}",
                           alumno=alumno,
                           inscripciones=inscripciones)

@bp.route('/grupo/nuevo', methods=['GET', 'POST'])
@admin_required
def nuevo_grupo():
    form = GrupoForm()
    if form.validate_on_submit():
        grupo = Grupo()
        # Populamos los campos principales, excluyendo la lista de horarios
        form.populate_obj(grupo, exclude=['horarios'])
        try:
            # Añadimos los horarios y países
            for horario_form in form.horarios:
                horario = Horario(horainicio=horario_form.horainicio.data, horafin=horario_form.horafin.data, grupo=grupo)
                for pais_form in horario_form.paises:
                    PaisHorario(nombre=pais_form.nombre.data, horario=horario)

            db.session.add(grupo)
            db.session.commit()
            flash('Grupo creado exitosamente.', 'success')
            return redirect(url_for('admin.grupos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear grupo: {e}', 'danger')
    return render_template('admin/form_grupo.html', 
                           title='Nuevo Grupo', 
                           form=form)

@bp.route('/grupo/<int:grupo_id>/editar', methods=['GET', 'POST'])
@admin_required
def editar_grupo(grupo_id):
    grupo = Grupo.query.options(
        db.joinedload(Grupo.horarios).joinedload(Horario.paises)
    ).get_or_404(grupo_id)

    # Si el formulario no se está enviando (petición GET), lo pre-poblamos con los datos de la BD.
    if not request.form:
        form = GrupoForm(obj=grupo)
    else:
        # Si se está enviando (petición POST), lo creamos a partir de los datos del request.
        form = GrupoForm(request.form)

    # --- Lógica para añadir/eliminar dinámicamente SIN JAVASCRIPT ---
    action = request.form.get('action')
    if action:
        if action == 'add_horario':
            form.horarios.append_entry()
        elif action.startswith('remove_horario_'):
            index = int(action.split('_')[-1])
            if 0 <= index < len(form.horarios.entries):
                del form.horarios.entries[index]
        elif action.startswith('add_pais_'):
            horario_index = int(action.split('_')[-1])
            if 0 <= horario_index < len(form.horarios.entries):
                form.horarios[horario_index].paises.append_entry()
        elif action.startswith('remove_pais_'):
            horario_index, pais_index = map(int, action.split('_')[-2:])
            if 0 <= horario_index < len(form.horarios.entries) and \
               0 <= pais_index < len(form.horarios[horario_index].paises.entries):
                del form.horarios[horario_index].paises.entries[pais_index]
        
        # Devolvemos la plantilla con el formulario modificado, sin validar ni guardar
        return render_template('admin/form_grupo.html', title='Editar Grupo', form=form, grupo=grupo)
    # --- Fin de la lógica dinámica ---

    if form.validate_on_submit():
        try:
            # Populamos los campos principales, excluyendo la lista de horarios
            form.populate_obj(grupo, exclude=['horarios'])

            # Eliminamos los horarios antiguos para reemplazarlos
            for horario in grupo.horarios:
                db.session.delete(horario)
            db.session.flush()

            # Añadimos los nuevos horarios y países desde el formulario
            for horario_data in form.horarios.data:
                if horario_data['horainicio'] and horario_data['horafin']: # Solo guardar si hay datos
                    horario = Horario(horainicio=horario_data['horainicio'], horafin=horario_data['horafin'], grupo=grupo)
                    db.session.add(horario)
                    for pais_data in horario_data['paises']:
                        if pais_data['nombre']:
                            PaisHorario(nombre=pais_data['nombre'], horario=horario)

            db.session.commit()
            flash('Grupo actualizado exitosamente.', 'success')
            return redirect(url_for('admin.grupos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar grupo: {e}', 'danger')
    return render_template('admin/form_grupo.html', 
                           title='Editar Grupo', 
                           form=form, 
                           grupo=grupo)

@bp.route('/grupo/<int:grupo_id>/eliminar', methods=['POST'])
@admin_required
def eliminar_grupo(grupo_id):
    grupo = Grupo.query.get_or_404(grupo_id)
    try:
        db.session.delete(grupo)
        db.session.commit()
        flash('Grupo eliminado', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar grupo: {e}', 'danger')
    return redirect(url_for('admin.grupos'))
