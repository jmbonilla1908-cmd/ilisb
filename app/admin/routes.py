from flask import render_template, redirect, url_for, flash, request, make_response
from flask_login import login_user, logout_user, current_user
from werkzeug.exceptions import NotFound
from app import db
from app.admin import bp
from app.admin.decorators import admin_required, superuser_required
from app.admin.forms import AdminLoginForm, DocenteForm, AlumnoForm, GrupoForm, CursoForm
from app.admin.models import User
from app.cursos.models import Curso, Docente, Grupo
from app.auth.models import Alumno
import secrets
from datetime import datetime
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
        user.last_login = datetime.utcnow()
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
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', 
                         title='Gestión de Usuarios', 
                         users=users)


@bp.route('/cursos')
@admin_required
def cursos():
    """Muestra la lista de cursos para administración."""
    cursos = Curso.query.order_by(Curso.nombre).all()
    return render_template(
        'admin/admin_lista_cursos.html',
        title='Gestión de Cursos',
        cursos=cursos
    )

@bp.route('/curso/nuevo', methods=['GET', 'POST'])
@admin_required
def nuevo_curso():
    """Crear un nuevo curso."""
    form = CursoForm()
    if form.validate_on_submit():
        curso = Curso()
        form.populate_obj(curso)
        # Generar slug a partir del nombre
        curso.slug = slugify(curso.nombre)
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
    curso = Curso.query.filter_by(slug=slug).first_or_404()
    form = CursoForm(obj=curso)
    
    if form.validate_on_submit():
        # Rellena el objeto 'curso' con los datos validados del formulario
        original_slug = curso.slug
        form.populate_obj(curso)
        # Si el nombre cambia, actualizamos el slug
        curso.slug = slugify(curso.nombre)
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
    alumnos = Alumno.query.order_by(
        Alumno.nombres, Alumno.apellidos
    ).all()
    return render_template('admin/alumnos.html',
                           title='Gestión de Alumnos',
                           alumnos=alumnos)


@bp.route('/docentes')
@admin_required
def docentes():
    """Gestión de docentes"""
    docentes = Docente.query.order_by(
        Docente.nombre
    ).all()
    return render_template('admin/docentes.html',
                           title='Gestión de Docentes',
                           docentes=docentes)


@bp.route('/grupos')
@admin_required
def grupos():
    """Gestión de grupos"""
    grupos = Grupo.query.order_by(Grupo.id).all()
    return render_template('admin/grupos.html',
                           title='Gestión de Grupos',
                           grupos=grupos)


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
    # Pasamos el email original al formulario para la validación de unicidad
    form = AlumnoForm(obj=alumno, original_email=alumno.email.lower())
    
    if form.validate_on_submit():
        # Rellenamos el objeto alumno existente con los nuevos datos
        form.populate_obj(alumno)
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

@bp.route('/grupo/nuevo', methods=['GET', 'POST'])
@admin_required
def nuevo_grupo():
    form = GrupoForm()
    if form.validate_on_submit():
        grupo = Grupo()
        form.populate_obj(grupo)
        try:
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
    grupo = Grupo.query.get_or_404(grupo_id)
    form = GrupoForm(obj=grupo)
    if form.validate_on_submit():
        form.populate_obj(grupo)
        try:
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
