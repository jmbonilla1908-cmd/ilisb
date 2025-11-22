import json
import click
from app import db
from app.admin import bp
from app.cursos.models import Curso, Modulo, ItemTemario, Grupo, Horario, PaisHorario

@bp.cli.command('migrar-temario')
def migrar_temario_json():
    """
    Lee el campo `temario` (JSON) de cada curso y lo migra a las nuevas
    tablas `Modulo` y `ItemTemario`.
    """
    print("Iniciando migración de datos de temarios...")
    
    # Obtenemos todos los cursos que tienen algo en el campo temario
    cursos_con_temario = Curso.query.filter(Curso.temario != None, Curso.temario != '').all()
    
    if not cursos_con_temario:
        print("No se encontraron cursos con datos en el campo 'temario' para migrar.")
        return

    for curso in cursos_con_temario:
        click.echo(f"Procesando curso: '{curso.nombre}' (ID: {curso.id})")
        
        # Si el curso ya tiene módulos, asumimos que ya fue migrado y lo saltamos.
        if curso.modulos.count() > 0:
            click.secho("  -> Ya tiene módulos, saltando.", fg='yellow')
            continue

        try:
            temario_json = json.loads(curso.temario)
            for i, modulo_data in enumerate(temario_json):
                nuevo_modulo = Modulo(curso_id=curso.id, titulo=modulo_data.get('titulo', 'Sin Título'), orden=i)
                db.session.add(nuevo_modulo)
                db.session.flush()
                for j, item_contenido in enumerate(modulo_data.get('item', [])):
                    nuevo_item = ItemTemario(modulo_id=nuevo_modulo.id, contenido=item_contenido, orden=j)
                    db.session.add(nuevo_item)
            click.secho(f"  -> Migración exitosa para el curso {curso.id}.", fg='green')
        except (json.JSONDecodeError, TypeError) as e:
            click.secho(f"  -> ERROR: No se pudo procesar el JSON para el curso {curso.id}. Error: {e}", fg='red')

    db.session.commit()
    click.secho("\n¡Migración de datos de temarios completada!", fg='blue', bold=True)


@bp.cli.command('migrar-horarios')
def migrar_horarios_json():
    """
    Lee el campo `horario_descripcion` (JSON) de cada grupo y lo migra
    a las nuevas tablas `Horario` y `PaisHorario`.
    """
    click.secho("Iniciando migración de datos de horarios...", fg='cyan')

    grupos_con_json = Grupo.query.filter(Grupo.horario_descripcion.isnot(None)).all()

    if not grupos_con_json:
        click.secho("No se encontraron grupos con datos en 'horario_descripcion' para migrar.", fg='yellow')
        return

    for grupo in grupos_con_json:
        click.echo(f"Procesando Grupo ID: {grupo.id}")

        if not grupo.horario_descripcion or not grupo.horario_descripcion.strip().startswith('['):
            click.secho(f"  -> Saltando: La descripción no parece ser un JSON.", fg='yellow')
            continue

        try:
            horarios_data = json.loads(grupo.horario_descripcion)
            
            Horario.query.filter_by(grupo_id=grupo.id).delete()
            db.session.flush()

            for horario_data in horarios_data:
                nuevo_horario = Horario(
                    grupo_id=grupo.id,
                    horainicio=horario_data.get('horainicio', 'N/A'),
                    horafin=horario_data.get('horafin', 'N/A')
                )
                db.session.add(nuevo_horario)
                db.session.flush()
                for pais_nombre in horario_data.get('paises', []):
                    PaisHorario(horario_id=nuevo_horario.id, nombre=pais_nombre)
            click.secho(f"  -> Migración exitosa para el Grupo {grupo.id}.", fg='green')
        except (json.JSONDecodeError, TypeError) as e:
            click.secho(f"  -> ERROR: No se pudo procesar el JSON para el Grupo {grupo.id}. Error: {e}", fg='red')

    db.session.commit()
    click.secho("\n¡Migración de datos de horarios completada!", fg='blue', bold=True)


@bp.cli.command('limpiar-horarios-json')
def limpiar_horarios_json():
    """
    Limpia el campo `horario_descripcion` de los grupos que contienen el
    antiguo formato JSON, una vez que los datos han sido migrados.
    """
    click.secho("Iniciando limpieza de campos JSON de horarios...", fg='cyan')
    
    grupos_a_limpiar = Grupo.query.filter(Grupo.horario_descripcion.isnot(None)).all()
    count = 0

    if not grupos_a_limpiar:
        click.secho("No se encontraron grupos con datos en 'horario_descripcion' para limpiar.", fg='yellow')
        return

    for grupo in grupos_a_limpiar:
        if grupo.horario_descripcion and grupo.horario_descripcion.strip().startswith('['):
            try:
                json.loads(grupo.horario_descripcion) # Confirma que es JSON antes de borrar
                grupo.horario_descripcion = "" # Vaciamos el campo
                count += 1
                click.secho(f"  -> Limpiando JSON del Grupo ID {grupo.id}.", fg='green')
            except (json.JSONDecodeError, TypeError):
                continue # Si no es un JSON válido, lo ignoramos
    
    db.session.commit()
    click.secho(f"\n¡Limpieza completada! Se actualizaron {count} grupos.", fg='blue', bold=True)


@bp.cli.command('limpiar-temario-json')
def limpiar_temario_json():
    """
    Limpia el campo `temario` de los cursos que contienen el
    antiguo formato JSON, una vez que los datos han sido migrados.
    """
    click.secho("Iniciando limpieza de campos JSON de temarios...", fg='cyan')
    
    cursos_a_limpiar = Curso.query.filter(Curso.temario.isnot(None), Curso.temario != '').all()
    count = 0

    if not cursos_a_limpiar:
        click.secho("No se encontraron cursos con datos en 'temario' para limpiar.", fg='yellow')
        return

    for curso in cursos_a_limpiar:
        # Doble chequeo de seguridad: solo limpiar si el curso tiene módulos estructurados
        # y el campo temario parece ser un JSON.
        if curso.modulos and curso.temario.strip().startswith('['):
            try:
                json.loads(curso.temario) # Confirma que es JSON antes de borrar
                curso.temario = "" # Vaciamos el campo
                count += 1
                click.secho(f"  -> Limpiando JSON del Curso ID {curso.id} ({curso.nombre}).", fg='green')
            except (json.JSONDecodeError, TypeError):
                continue # Si no es un JSON válido, lo ignoramos
    
    db.session.commit()
    click.secho(f"\n¡Limpieza completada! Se actualizaron {count} cursos.", fg='blue', bold=True)