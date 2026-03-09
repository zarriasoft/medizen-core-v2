import subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "fpdf2", "--quiet"], capture_output=True)
from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_fill_color(0, 105, 105)
        self.rect(0, 0, 210, 20, 'F')
        self.set_font('Helvetica', 'B', 13)
        self.set_text_color(255, 255, 255)
        self.set_xy(0, 4)
        self.cell(210, 12, 'MEDIZEN CORE 2.0 - Manual del Sistema', align='C', ln=True)
        self.set_text_color(0, 0, 0)
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(130, 130, 130)
        self.cell(0, 10, f'Pagina {self.page_no()} | Medizen Core 2.0 | Documento Interno', align='C')

    def section_header(self, icon, title, r=0, g=128, b=128):
        self.set_fill_color(r, g, b)
        self.set_text_color(255, 255, 255)
        self.set_font('Helvetica', 'B', 11)
        self.cell(0, 9, f'  {icon}  {title}', fill=True, ln=True)
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def feature_block(self, name, description_lines):
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(0, 90, 50)
        self.set_fill_color(220, 255, 235)
        self.cell(0, 6, f'  {name}', fill=True, ln=True)
        self.set_text_color(50, 50, 50)
        self.set_left_margin(16)
        self.set_font('Helvetica', '', 9)
        for line in description_lines:
            self.multi_cell(0, 5, f'- {line}')
        self.set_left_margin(10)
        self.ln(2)

    def info_box(self, text):
        self.set_fill_color(230, 245, 255)
        self.set_font('Helvetica', 'I', 9)
        self.set_text_color(50, 50, 100)
        self.multi_cell(0, 6, f'  {text}', fill=True)
        self.set_text_color(0, 0, 0)
        self.ln(2)

pdf = PDF('P', 'mm', 'A4')
pdf.set_margins(10, 26, 10)
pdf.set_auto_page_break(True, 18)
pdf.add_page()

# Intro
pdf.set_font('Helvetica', '', 10)
pdf.set_text_color(80, 80, 80)
pdf.multi_cell(0, 5, 'Sistema de Gestion de Clinica de Medicina Funcional e Integrativa\nVersion 2.0 - Marzo 2025', align='C')
pdf.ln(5)

pdf.info_box(
    'Este documento describe todas las funcionalidades de la plataforma Medizen Core 2.0. '
    'Esta disenado para que cualquier persona del equipo clinico pueda entender que hace el sistema y como usarlo.'
)

# QUE ES
pdf.section_header('*', 'QUE ES MEDIZEN CORE 2.0')
pdf.set_font('Helvetica', '', 10)
pdf.set_text_color(40, 40, 40)
pdf.multi_cell(0, 5,
    'Medizen Core 2.0 es una plataforma web de gestion clinica disenada para clinicas de '
    'medicina funcional e integrativa. Permite administrar pacientes, citas, membresias, '
    'evaluaciones clinicas y notificaciones automaticas, todo desde un navegador web.'
)
pdf.ln(3)

# DASHBOARD
pdf.section_header('[1]', 'PANEL DE CONTROL (DASHBOARD)')
pdf.feature_block('Estadisticas de la Clinica', [
    'Muestra el total de pacientes activos registrados en el sistema.',
    'Calcula el promedio del indice IEIM (bienestar) de todos los pacientes.',
    'Indica cuantas citas hay programadas para el dia de hoy.',
    'Muestra el numero de pacientes en riesgo (sin evaluacion en 30 dias).',
])
pdf.feature_block('Grafico de Evolucion IEIM', [
    'Grafico de linea que muestra la tendencia de bienestar semanal de los pacientes.',
])
pdf.feature_block('Alertas Clinicas en Tiempo Real', [
    'Panel de alertas con codigo de color: Rojo=Critico, Amarillo=Advertencia, Azul=Info.',
    'Se actualiza automaticamente al ingresar al dashboard.',
])
pdf.feature_block('Exportar Resumen a Excel', [
    'Descarga un archivo .xlsx con KPIs del dia: pacientes, IEIM, sesiones y alertas.',
])

# PACIENTES
pdf.section_header('[2]', 'GESTION DE PACIENTES', r=30, g=100, b=30)
pdf.feature_block('Listado de Pacientes', [
    'Tabla con todos los pacientes activos con buscador integrado.',
    'Filtros por estado activo/inactivo.',
])
pdf.feature_block('Registro de Nuevo Paciente', [
    'Formulario: nombre, apellidos, correo, telefono y fecha de nacimiento.',
])
pdf.feature_block('Vista Detallada del Paciente', [
    'Historial IEIM completo con fechas y puntajes de cada evaluacion.',
    'Historial clinico (notas de sesiones anteriores).',
    'Membresias y planes asignados con sesiones restantes.',
])
pdf.feature_block('Editar y Desactivar Paciente', [
    'Actualizar datos personales del paciente en cualquier momento.',
    'Desactivar pacientes que dejaron el tratamiento (se conserva su historial).',
])
pdf.feature_block('Exportar a Excel', [
    'Descarga el listado completo de pacientes en formato .xlsx.',
])

# IEIM
pdf.section_header('[3]', 'EVALUACIONES IEIM', r=80, g=50, b=130)
pdf.info_box('IEIM: Indice de Evaluacion Integral de Medicina. Mide 6 dimensiones del bienestar del paciente (escala 1-10).')
pdf.feature_block('Registro de Evaluacion IEIM', [
    'Nivel de Dolor, Calidad del Sueno, Nivel de Energia, Estres/Ansiedad, Movilidad, Inflamacion.',
    'El puntaje global (promedio) se calcula automaticamente.',
])
pdf.feature_block('Historial de Evaluaciones', [
    'Todas las evaluaciones quedan guardadas con fecha para ver la evolucion del paciente.',
])

# CITAS
pdf.add_page()
pdf.section_header('[4]', 'AGENDA Y CITAS', r=180, g=80, b=0)
pdf.feature_block('Vista de Citas de Hoy', [
    'Lista de citas del dia en curso, ordenadas por hora.',
    'Muestra: paciente, hora, estado (pendiente, completada).',
    'Buscador y navegacion entre dias disponible.',
])
pdf.feature_block('Programar Nueva Cita', [
    'Seleccion de paciente, fecha, hora y notas previas.',
])
pdf.feature_block('Finalizar Sesion (Completar Cita)', [
    'Al completar una cita:',
    '  a) Descuenta 1 sesion del plan activo del paciente.',
    '  b) Solicita agregar una nota clinica de la sesion.',
    '  c) Guarda la nota en el historial clinico del paciente con fecha y hora.',
])
pdf.feature_block('Exportar Agenda a Excel', [
    'Descarga el listado de citas del periodo filtrado en .xlsx.',
])

# MEMBRESIAS
pdf.section_header('[5]', 'MEMBRESIAS Y PLANES', r=0, g=80, b=160)
pdf.feature_block('Listado de Planes', [
    'Ver todos los planes de membresia disponibles en la clinica.',
])
pdf.feature_block('Crear y Editar Planes', [
    'El administrador puede crear nuevos planes (ejemplo: Plan Premium - 10 sesiones).',
    'Se puede editar nombre, duracion o numero de sesiones.',
    'Se puede desactivar planes que ya no se ofrezcan.',
])
pdf.feature_block('Asignar Plan a Paciente', [
    'Desde el perfil del paciente se asigna el plan contratado.',
    'El sistema lleva el control de sesiones utilizadas y restantes.',
])
pdf.feature_block('Alertas de Vencimiento', [
    'Alerta automatica cuando la membresia de un paciente vence en menos de 7 dias.',
])

# PROGRAMAS
pdf.section_header('[6]', 'PROGRAMAS CLINICOS', r=100, g=0, b=80)
pdf.feature_block('Gestion de Programas de Tratamiento', [
    'Registrar protocolos clinicos de la clinica (ej: Programa Anti-Inflamacion 3 meses).',
    'Crear, editar y desactivar programas desde esta seccion.',
])

# CONFIGURACION
pdf.section_header('[7]', 'CONFIGURACION Y PERFIL DEL USUARIO')
pdf.feature_block('Perfil del Doctor / Administrador', [
    'Actualizar nombre completo y correo electronico del usuario logueado.',
    'Los cambios se reflejan de inmediato en toda la plataforma.',
])
pdf.feature_block('Seguridad del Sistema', [
    'Sistema de login seguro con tokens de sesion (JWT).',
    'La sesion expira automaticamente por seguridad.',
])

# NOTIFICACIONES
pdf.section_header('[8]', 'NOTIFICACIONES AUTOMATICAS', r=160, g=50, b=0)
pdf.info_box('El sistema revisa la base de datos cada 60 segundos y genera alertas automaticas.')
pdf.feature_block('Tipos de Alertas Automaticas', [
    'Email: Pacientes sin evaluacion IEIM en mas de 30 dias (riesgo de abandono).',
    'SMS: Paciente con IEIM critico detectado (puntaje menor a 4.0).',
    'WhatsApp: Aviso de membresia proxima a vencer (menos de 7 dias).',
])
pdf.feature_block('Vista en Dashboard', [
    'Todas las alertas activas aparecen en el panel de control en tiempo real.',
])

# EXCEL
pdf.section_header('[9]', 'EXPORTACION A EXCEL (EN TODAS LAS PANTALLAS)', r=30, g=80, b=30)
pdf.feature_block('Disponible en: Dashboard, Pacientes, Citas, Membresias', [
    'Cada pantalla tiene un boton "Exportar Excel" que descarga los datos visibles.',
    'Los archivos se guardan directamente en la computadora del usuario.',
])

# RESUMEN FINAL
pdf.ln(3)
pdf.section_header('*', 'RESUMEN: QUE PUEDE HACER EL SISTEMA', r=0, g=80, b=40)
pdf.set_font('Helvetica', '', 9)
pdf.set_text_color(30, 30, 30)
resumen = [
    'Registrar y gestionar pacientes de la clinica',
    'Agendar, ver y completar citas con notas clinicas automaticas',
    'Evaluar el bienestar de cada paciente con el indice IEIM',
    'Gestionar planes de membresia y controlar las sesiones disponibles',
    'Crear y administrar programas de tratamiento',
    'Ver alertas clinicas criticas en tiempo real en el Dashboard',
    'Recibir notificaciones automaticas de eventos importantes',
    'Exportar cualquier listado a Excel con un solo clic',
    'Acceder desde cualquier dispositivo con navegador web e internet',
    'Sistema de login seguro para proteger la informacion clinica',
]
for item in resumen:
    pdf.multi_cell(0, 6, f'  OK  {item}')

out = r'C:\Medizen\v2\Manual_Sistema_Medizen.pdf'
pdf.output(out)
print(f'PDF generado: {out}')
