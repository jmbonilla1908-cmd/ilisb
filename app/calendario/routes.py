import calendar
from datetime import datetime
from flask import render_template, request, url_for
from . import bp
from app.cursos.models import Grupo, Sesion, Curso, db
from sqlalchemy import func

class CustomHTMLCalendar(calendar.HTMLCalendar):
    def __init__(self, year, month, eventos, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.year = year
        self.month = month
        self.eventos = eventos  # {day: {'url': '...', 'title': '...'}}

    def formatday(self, day, weekday):
        if day == 0:
            return '<td class="noday">&nbsp;</td>'
        
        today = datetime.today()
        css_class = self.cssclasses[weekday]
        
        # Resaltar el día actual
        if self.year == today.year and self.month == today.month and day == today.day:
            css_class += ' table-info'

        if day in self.eventos:
            css_class += ' table-primary'
            return (f'<td class="{css_class}">'
                    f'<a href="{self.eventos[day]["url"]}" '
                    f'hx-boost="true" '
                    f'title="{self.eventos[day]["title"]}" class="text-decoration-none d-block">{day}</a></td>')
        
        return f'<td class="{css_class}">{day}</td>'

    def formatmonthname(self, theyear, themonth, withyear=True):
        """
        Sobrescribimos este método para que no genere ninguna cabecera de mes,
        ya que la manejamos en la plantilla de Jinja.
        """
        return ''

    def formatweekheader(self):
        """
        Sobrescribimos este método para usar las abreviaciones en español.
        """
        dias_semana = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"]
        s = ''.join(f'<th class="{self.cssclasses[i]}">{dias_semana[i]}</th>' for i in self.iterweekdays())
        return f'<tr>{s}</tr>'

    def formatmonth(self, theyear, themonth, withyear=True):
        cal = super().formatmonth(theyear, themonth, withyear)
        cal = cal.replace('<table border="0" cellpadding="0" cellspacing="0" class="month">',
                          '<table class="table table-bordered table-sm text-center" style="font-size: 0.8rem;">')
        return cal

@bp.route('/')
def mostrar_calendario():
    today = datetime.today()
    year = request.args.get('year', today.year, type=int)
    month = request.args.get('month', today.month, type=int)

    # Nombres de los meses en español
    meses = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    month_name = meses[month]

    # Consultar eventos (inicio de cursos) para el mes y año dados
    start_of_month = datetime(year, month, 1)
    if month == 12:
        end_of_month = datetime(year + 1, 1, 1)
    else:
        end_of_month = datetime(year, month + 1, 1)

    # Subconsulta para encontrar la primera fecha de sesión para cada grupo
    first_session_sq = db.session.query(
        Sesion.id_grupo,
        func.min(Sesion.__table__.c.fechasesion).label('start_date')
    ).group_by(Sesion.id_grupo).subquery()

    # Consulta principal que une Grupo, Curso y la subconsulta de la primera sesión
    grupos_con_fecha = db.session.query(Grupo, first_session_sq.c.start_date).join(
        first_session_sq, Grupo.id == first_session_sq.c.id_grupo
    ).join(Curso).filter(
        first_session_sq.c.start_date >= start_of_month,
        first_session_sq.c.start_date < end_of_month,
        Grupo.visible == True
    ).all()

    eventos = {
        fecha_inicio.day: {'title': grupo.curso.nombre, 'url': url_for('cursos.detalle_curso', slug=grupo.curso.slug)}
        for grupo, fecha_inicio in grupos_con_fecha
    }

    cal = CustomHTMLCalendar(year, month, eventos, firstweekday=0) # Lunes como primer día
    calendario_html = cal.formatmonth(year, month)

    return render_template('calendario/calendario.html', calendario_html=calendario_html, year=year, month=month, month_name=month_name)