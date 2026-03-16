import subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "fpdf2", "--quiet"], capture_output=True)
from fpdf import FPDF
from datetime import date

fecha = date.today().strftime("%d/%m/%Y")

class PDF(FPDF):
    def header(self):
        self.set_fill_color(0, 95, 115)
        self.rect(0, 0, 210, 22, 'F')
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(255, 255, 255)
        self.set_xy(0, 4)
        self.cell(210, 8, 'MEDIZEN CORE 2.0', align='C', ln=True)
        self.set_font('Helvetica', '', 8)
        self.set_text_color(200, 235, 245)
        self.cell(210, 5, 'Manual del Sistema - Version para Cliente', align='C', ln=True)
        self.set_text_color(0, 0, 0)
        self.ln(8)

    def footer(self):
        self.set_y(-14)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Pagina {self.page_no()}  |  Medizen Core 2.0  |  Documento Confidencial  |  {fecha}', align='C')

    def section_header(self, number, title, r=0, g=95, b=115):
        self.set_fill_color(r, g, b)
        self.set_text_color(255, 255, 255)
        self.set_font('Helvetica', 'B', 10)
        self.cell(0, 8, f'  {number}  {title}', fill=True, ln=True)
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def feature_block(self, name, lines):
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(0, 80, 50)
        self.set_fill_color(230, 255, 240)
        self.cell(0, 6, f'   {name}', fill=True, ln=True)
        self.set_text_color(50, 50, 50)
        self.set_left_margin(16)
        self.set_font('Helvetica', '', 9)
        for line in lines:
            self.multi_cell(0, 5, f'- {line}')
        self.set_left_margin(10)
        self.ln(2)

    def info_box(self, text, r=220, g=240, b=255):
        self.set_fill_color(r, g, b)
        self.set_font('Helvetica', 'I', 9)
        self.set_text_color(30, 60, 120)
        self.multi_cell(0, 6, f'   {text}', fill=True)
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def access_box(self, label, value):
        self.set_font('Helvetica', 'B', 9)
        self.set_fill_color(0, 95, 115)
        self.set_text_color(255, 255, 255)
        self.cell(45, 7, f'  {label}', fill=True)
        self.set_fill_color(235, 250, 255)
        self.set_text_color(0, 50, 100)
        self.set_font('Helvetica', '', 9)
        self.cell(145, 7, f'  {value}', fill=True, ln=True)


pdf = PDF('P', 'mm', 'A4')
pdf.set_margins(10, 28, 10)
pdf.set_auto_page_break(True, 16)
pdf.add_page()

# PORTADA INFO
pdf.set_font('Helvetica', 'B', 13)
pdf.set_text_color(0, 95, 115)
pdf.cell(0, 8, 'Sistema de Gestion Clinica Funcional e Integrativa', align='C', ln=True)
pdf.set_font('Helvetica', '', 9)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 6, f'Version 2.0  |  Release: Marzo 2026  |  Generado: {fecha}', align='C', ln=True)
pdf.ln(5)

pdf.info_box(
    'Este documento describe todas las funcionalidades de Medizen Core 2.0. '
    'Disenado para el equipo clinico que usara la plataforma en el dia a dia.'
)

# ACCESO AL SISTEMA
pdf.section_header('*', 'ACCESO AL SISTEMA EN LA NUBE')
pdf.set_font('Helvetica', '', 9)
pdf.set_text_color(40, 40, 40)
pdf.multi_cell(0, 5,
    'Medizen Core 2.0 es una plataforma 100% en la nube. No requiere instalacion. '
    'Solo necesitas un navegador web (Chrome, Firefox, Edge) y conexion a internet.'
)
pdf.ln(3)
pdf.access_box('URL de Acceso', 'https://medizen-frontend.vercel.app')
pdf.access_box('Usuario inicial', 'admin')
pdf.access_box('Contrasena inicial', 'adminpassword')
pdf.access_box('Soporte tecnico', 'Consultar con el administrador del sistema')
pdf.ln(3)
pdf.info_box(
    'IMPORTANTE: Se recomienda cambiar la contrasena inicial al primer ingreso '
    'desde Configuracion > Perfil de Usuario.'
, r=255, g=245, b=220)
pdf.ln(2)

# QUE ES
pdf.section_header('1.', 'QUE ES MEDIZEN CORE 2.0')
pdf.set_font('Helvetica', '', 9)
pdf.set_text_color(40, 40, 40)
pdf.multi_cell(0, 5,
    'Medizen Core 2.0 es una plataforma web de gestion clinica para clinicas de medicina '
    'funcional e integrativa. Permite administrar pacientes, citas, membresias, evaluaciones '
    'y notificaciones automaticas, todo desde cualquier dispositivo con internet.'
)
pdf.ln(3)

# INFRAESTRUCTURA
pdf.section_header('2.', 'INFRAESTRUCTURA TECNICA', r=60, g=60, b=80)
pdf.feature_block('Frontend (Interfaz de usuario)', [
    'Plataforma: Vercel (CDN global, alta disponibilidad)',
    'URL: https://medizen-frontend.vercel.app',
    'Tecnologia: React + TypeScript + Vite',
])
pdf.feature_block('Backend (Logica del sistema)', [
    'Plataforma: Render.com | URL API: https://medizen-api.onrender.com',
    'Tecnologia: Python + FastAPI',
    'Nota: En plan gratuito puede tardar 30-60s en el primer acceso del dia.',
])
pdf.feature_block('Base de Datos', [
    'Plataforma: Neon PostgreSQL (serverless, cloud AWS)',
    'Backups automaticos incluidos.',
])

# DASHBOARD
pdf.section_header('3.', 'PANEL DE CONTROL (DASHBOARD)')
pdf.feature_block('Estadisticas de la Clinica', [
    'Total de pacientes activos, promedio IEIM, citas del dia y pacientes en riesgo.',
])
pdf.feature_block('Grafico de Evolucion IEIM', [
    'Grafico de linea con tendencia de bienestar semanal de los pacientes.',
])
pdf.feature_block('Alertas Clinicas en Tiempo Real', [
    'Rojo = Critico, Amarillo = Advertencia, Azul = Informativo.',
    'Se actualiza automaticamente al abrir el dashboard.',
])
pdf.feature_block('Exportar Resumen a Excel', [
    'Descarga KPIs del dia: pacientes, IEIM, sesiones y alertas activas.',
])

# PACIENTES
pdf.add_page()
pdf.section_header('4.', 'GESTION DE PACIENTES', r=20, g=100, b=40)
pdf.feature_block('Listado de Pacientes', [
    'Tabla con todos los pacientes activos, buscador y filtro por estado.',
])
pdf.feature_block('Registro de Nuevo Paciente', [
    'Formulario: nombre, apellidos, correo, telefono y fecha de nacimiento.',
])
pdf.feature_block('Vista Detallada del Paciente', [
    'Historial IEIM completo con fechas y puntajes.',
    'Historial clinico (notas de sesiones anteriores).',
    'Membresias asignadas con sesiones restantes.',
])
pdf.feature_block('Editar y Desactivar Paciente', [
    'Actualizar datos personales en cualquier momento.',
    'Desactivar pacientes sin eliminar su historial.',
])
pdf.feature_block('Exportar a Excel', [
    'Descarga el listado completo de pacientes en formato .xlsx.',
])

# IEIM
pdf.section_header('5.', 'EVALUACIONES IEIM', r=80, g=50, b=130)
pdf.info_box('IEIM: Indice de Evaluacion Integral de Medicina. Mide 6 dimensiones del bienestar (escala 1-10).')
pdf.feature_block('Registro de Evaluacion', [
    'Dimensiones: Dolor, Calidad del Sueno, Energia, Estres/Ansiedad, Movilidad, Inflamacion.',
    'Puntaje global calculado automaticamente como promedio.',
])
pdf.feature_block('Historial de Evaluaciones', [
    'Todas las evaluaciones quedan guardadas con fecha para ver la evolucion clinica.',
])

# CITAS
pdf.section_header('6.', 'AGENDA Y CITAS', r=180, g=80, b=0)
pdf.feature_block('Vista de Citas del Dia', [
    'Lista de citas ordenadas por hora con estado (pendiente / completada).',
    'Navegacion entre dias disponible.',
])
pdf.feature_block('Programar Nueva Cita', [
    'Seleccion de paciente, fecha, hora y notas previas.',
])
pdf.feature_block('Completar una Sesion', [
    'Descuenta 1 sesion del plan activo del paciente.',
    'Solicita nota clinica que queda guardada en el historial con fecha y hora.',
])
pdf.feature_block('Exportar Agenda a Excel', [
    'Descarga las citas del periodo filtrado en formato .xlsx.',
])

# MEMBRESIAS
pdf.section_header('7.', 'MEMBRESIAS Y PLANES', r=0, g=80, b=160)
pdf.feature_block('Gestion de Planes', [
    'Ver, crear, editar y desactivar planes de membresia de la clinica.',
    'Cada plan tiene nombre, duracion y numero de sesiones incluidas.',
])
pdf.feature_block('Asignar Plan a Paciente', [
    'Desde el perfil del paciente se asigna el plan contratado.',
    'El sistema lleva el control de sesiones utilizadas y restantes.',
])
pdf.feature_block('Alertas de Vencimiento', [
    'Alerta automatica cuando una membresia vence en menos de 7 dias.',
])

# PROGRAMAS
pdf.section_header('8.', 'PROGRAMAS CLINICOS', r=100, g=0, b=80)
pdf.feature_block('Protocolos de Tratamiento', [
    'Registrar programas clinicos (ej: Programa Anti-Inflamacion 3 meses).',
    'Crear, editar y desactivar programas desde esta seccion.',
])

# CONFIGURACION
pdf.section_header('9.', 'CONFIGURACION Y PERFIL')
pdf.feature_block('Perfil del Usuario', [
    'Actualizar nombre completo, correo electronico y contrasena.',
])
pdf.feature_block('Seguridad', [
    'Login seguro con tokens JWT. La sesion expira automaticamente.',
])

# NOTIFICACIONES
pdf.add_page()
pdf.section_header('10.', 'NOTIFICACIONES AUTOMATICAS', r=160, g=50, b=0)
pdf.info_box('El sistema revisa la base de datos periodicamente y genera alertas automaticas.')
pdf.feature_block('Tipos de Alertas', [
    'IEIM critico: Puntaje menor a 4.0 (alerta roja urgente).',
    'Sin evaluacion: Paciente sin IEIM en mas de 30 dias.',
    'Membresia por vencer: Menos de 7 dias de vigencia.',
])
pdf.feature_block('Visualizacion', [
    'Todas las alertas activas aparecen en el Dashboard en tiempo real.',
])

# EXCEL
pdf.section_header('11.', 'EXPORTACION A EXCEL', r=30, g=80, b=30)
pdf.feature_block('Disponible en todas las pantallas', [
    'Dashboard, Pacientes, Citas y Membresias tienen boton "Exportar Excel".',
    'Archivos .xlsx se descargan directamente al dispositivo del usuario.',
    'No requiere ninguna instalacion adicional.',
])

# RESUMEN FINAL
pdf.ln(3)
pdf.section_header('*', 'RESUMEN: QUE PUEDE HACER EL SISTEMA', r=0, g=95, b=115)
pdf.set_font('Helvetica', '', 9)
pdf.set_text_color(30, 30, 30)
resumen = [
    'Registrar y gestionar pacientes de la clinica',
    'Agendar, ver y completar citas con notas clinicas automaticas',
    'Evaluar el bienestar con el indice IEIM (6 dimensiones)',
    'Gestionar planes de membresia y controlar sesiones disponibles',
    'Crear y administrar programas de tratamiento clinico',
    'Ver alertas criticas en tiempo real desde el Dashboard',
    'Recibir notificaciones automaticas de eventos importantes',
    'Exportar cualquier listado a Excel con un clic',
    'Acceder desde cualquier dispositivo con navegador e internet',
    'Login seguro con cierre automatico de sesion',
    'Sin instalacion requerida - 100% en la nube',
]
for item in resumen:
    pdf.multi_cell(0, 6, f'  [OK]  {item}')

# PIE
pdf.ln(5)
pdf.set_fill_color(0, 95, 115)
pdf.set_text_color(255, 255, 255)
pdf.set_font('Helvetica', 'B', 9)
pdf.cell(0, 7, f'  Medizen Core 2.0  |  https://medizen-frontend.vercel.app  |  Version 2.0  |  {fecha}', fill=True, ln=True)

out = r'C:\Medizen\v2\Manual_Sistema_Medizen_v2.pdf'
pdf.output(out)
print(f'PDF generado: {out}')
