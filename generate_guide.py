import subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "fpdf2", "--quiet"], capture_output=True)

from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_fill_color(0, 128, 128)
        self.rect(0, 0, 210, 22, 'F')
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(255, 255, 255)
        self.set_xy(0, 5)
        self.cell(210, 12, 'MEDIZEN CORE 2.0 - Guia de Acceso', align='C', ln=True)
        self.set_text_color(0, 0, 0)
        self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Pagina {self.page_no()} | Medizen Core 2.0 - Confidencial', align='C')

    def section_title(self, title, r=0, g=128, b=128):
        self.set_font('Helvetica', 'B', 11)
        self.set_fill_color(r, g, b)
        self.set_text_color(255, 255, 255)
        self.cell(0, 8, f'  {title}', fill=True, ln=True)
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def step_item(self, num, title, lines):
        self.set_fill_color(0, 128, 128)
        self.set_text_color(255, 255, 255)
        self.set_font('Helvetica', 'B', 10)
        self.cell(8, 7, str(num), fill=True, align='C')
        self.set_text_color(20, 20, 20)
        self.set_font('Helvetica', 'B', 10)
        self.cell(0, 7, f'  {title}', ln=True)
        self.set_left_margin(18)
        for line in lines:
            if line.startswith('>>'):
                self.set_fill_color(220, 255, 240)
                self.set_font('Helvetica', 'B', 10)
                self.set_text_color(0, 100, 50)
                self.multi_cell(0, 7, f'  {line[2:].strip()}', fill=True)
                self.set_text_color(20, 20, 20)
            elif line.startswith('!!'):
                self.set_fill_color(255, 245, 210)
                self.set_font('Helvetica', 'B', 9)
                self.set_text_color(160, 90, 0)
                self.multi_cell(0, 7, f'  IMPORTANTE: {line[2:].strip()}', fill=True)
                self.set_text_color(20, 20, 20)
            else:
                self.set_font('Helvetica', '', 10)
                self.multi_cell(0, 6, line)
        self.set_left_margin(10)
        self.ln(3)

    def problem_row(self, problem, solution):
        self.set_fill_color(255, 240, 240)
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(150, 0, 0)
        self.multi_cell(0, 6, f'  Problema: {problem}', fill=True)
        self.set_fill_color(240, 255, 240)
        self.set_font('Helvetica', '', 9)
        self.set_text_color(0, 100, 0)
        self.multi_cell(0, 6, f'  Solucion: {solution}', fill=True)
        self.set_text_color(0, 0, 0)
        self.ln(1)

pdf = PDF('P', 'mm', 'A4')
pdf.set_margins(10, 26, 10)
pdf.set_auto_page_break(True, 18)
pdf.add_page()

# Subtitle
pdf.set_font('Helvetica', '', 10)
pdf.set_text_color(80, 80, 80)
pdf.multi_cell(0, 5, 'Sistema de Gestion Clinica | Acceso para Usuarios Autorizados | Marzo 2025', align='C')
pdf.ln(5)

# Section 1: Steps
pdf.section_title('PASOS PARA INGRESAR AL SISTEMA')

pdf.step_item(1, 'Abre tu navegador de internet', [
    'Usa Google Chrome, Microsoft Edge o Firefox (cualquiera funciona).',
    'Abre una pestana nueva.'
])

pdf.step_item(2, 'Escribe la direccion del sistema', [
    'En la barra de direcciones (donde escribes las paginas web), escribe:',
    '>> https://medizen-frontend-v2.loca.lt',
    'Consejo: copia y pega el enlace para evitar errores.'
])

pdf.step_item(3, 'Pantalla de seguridad - Ingresa la clave del tunel', [
    'Veras una pagina gris con texto en ingles. Esto es normal.',
    'Busca el campo que dice: "Tunnel Password"',
    'Escribe exactamente esto:',
    '>> 186.78.142.168',
    'Haz clic en el boton azul que dice "Click to Submit"'
])

pdf.step_item(4, 'Inicia sesion en Medizen', [
    'Veras la pantalla azul/verde de Medizen con un formulario.',
    'Usa estas credenciales:',
    '>> Usuario: admin',
    '>> Contrasena: adminpassword',
    'Haz clic en "Iniciar Sesion".'
])

pdf.step_item(5, 'Ya estas adentro!', [
    'Veras el Panel de Control con estadisticas de la clinica.',
    'Usa el menu lateral (a la izquierda) para navegar entre pantallas.',
    '!! Si ves que el sistema te cierra la sesion, simplemente vuelve a iniciar sesion.'
])

pdf.ln(3)

# Section 2: Problems
pdf.section_title('PROBLEMAS FRECUENTES Y SOLUCIONES', r=180, g=80, b=0)

problems = [
    ('La pagina dice "503 - Tunnel Unavailable"',
     'El servicio se cayo. Comunicate con el administrador para que lo reinicie.'),
    ('La clave del tunel no funciona o la pagina gris no desaparece',
     'Verifica que escribiste exactamente: 186.78.142.168 (sin espacios). Intenta de nuevo.'),
    ('El navegador dice "No se puede acceder al sitio"',
     'Puede ser tu red Wi-Fi. Prueba usando los datos moviles de tu celular.'),
    ('El usuario y contrasena no funcionan',
     'Verifica que escribiste exactamente: admin (usuario) y adminpassword (contrasena). Son minusculas.'),
    ('El sistema va muy lento',
     'El sistema trabaja con internet. Espera unos segundos y vuelve a intentar. Si sigue lento, recarga con F5.'),
    ('Se cerro la sesion sola',
     'Es normal, por seguridad. Solo vuelve a iniciar sesion con el mismo usuario y contrasena.'),
    ('Tres personas entran al mismo tiempo - hay problemas?',
     'No hay problema. El sistema esta disenado para soportar varios usuarios a la vez. Puede ir un poco mas lento, es normal.'),
]

for prob, sol in problems:
    pdf.problem_row(prob, sol)

pdf.ln(3)

# Section 3: Limitations
pdf.section_title('Informacion Importante - Version Demo', r=60, g=60, b=150)
pdf.set_font('Helvetica', '', 9)
pdf.set_text_color(40, 40, 40)
pdf.multi_cell(0, 5,
    'Este sistema esta en modo DEMO desde una computadora local. Esto significa:\n'
    '  - Requiere que la computadora del administrador este encendida y conectada.\n'
    '  - El enlace puede cambiar si el sistema se reinicia. El administrador informara si cambia.\n'
    '  - Capacidad actual: hasta 3 a 5 usuarios al mismo tiempo sin problemas.\n'
    '  - No utilizar aun para almacenar datos medicos sensibles (proxima version).'
)

pdf.ln(5)

# Contact
pdf.section_title('Soporte y Contacto', r=30, g=100, b=30)
pdf.set_font('Helvetica', 'B', 10)
pdf.set_text_color(30, 30, 30)
pdf.multi_cell(0, 6,
    'Si el sistema no esta disponible o tienes dudas, comunicate con el administrador del sistema.\n'
    'Horario de atencion para soporte tecnico: a convenir con tu equipo.'
)

out = r'C:\Medizen\v2\Guia_Acceso_Medizen.pdf'
pdf.output(out)
print(f'PDF generado: {out}')
