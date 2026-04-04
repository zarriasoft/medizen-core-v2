import subprocess
import sys
from datetime import date

subprocess.run([sys.executable, "-m", "pip", "install", "fpdf2", "--quiet"], capture_output=True)

from fpdf import FPDF


REPORT_DATE = date.today().strftime("%d/%m/%Y")
OUTPUT_PATH = r"C:\Medizen\v2\Informe_Analisis_Medizen_v2.pdf"


class PDF(FPDF):
    def header(self):
        self.set_fill_color(15, 23, 42)
        self.rect(0, 0, 210, 20, "F")
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 14)
        self.set_xy(10, 5)
        self.cell(0, 6, "Informe de Analisis - Proyecto MediZen v2")
        self.set_font("Helvetica", "", 8)
        self.set_xy(10, 12)
        self.cell(0, 5, f"Vision de proyecto | Generado: {REPORT_DATE}")
        self.set_text_color(0, 0, 0)
        self.ln(16)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, f"Pagina {self.page_no()} | MediZen v2", align="C")

    def title_block(self, title, subtitle):
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(15, 23, 42)
        self.multi_cell(0, 8, title)
        self.ln(1)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(71, 85, 105)
        self.multi_cell(0, 6, subtitle)
        self.set_text_color(0, 0, 0)
        self.ln(3)

    def section(self, title, color=(14, 116, 144)):
        self.set_fill_color(*color)
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 11)
        self.cell(0, 8, f"  {title}", ln=True, fill=True)
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def paragraph(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 6, text)
        self.ln(1)

    def bullet_list(self, items):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        for item in items:
            self.multi_cell(0, 6, f"- {item}")
        self.ln(1)

    def callout(self, text, fill=(241, 245, 249), text_color=(30, 41, 59)):
        self.set_fill_color(*fill)
        self.set_text_color(*text_color)
        self.set_font("Helvetica", "I", 10)
        self.multi_cell(0, 6, f"  {text}", fill=True)
        self.set_text_color(0, 0, 0)
        self.ln(2)


pdf = PDF("P", "mm", "A4")
pdf.set_margins(12, 26, 12)
pdf.set_auto_page_break(True, 14)
pdf.add_page()

pdf.title_block(
    "Proyecto MediZen v2: lectura estrategica y tecnica",
    "Este informe resume la vision del proyecto alojado en la carpeta v2, su estado actual, fortalezas, riesgos principales y una lectura de hacia donde podria evolucionar si se consolida como producto.",
)

pdf.callout(
    "Conclusión ejecutiva: MediZen v2 ya se comporta como una plataforma de operacion clinico-comercial con dos frentes claros - administracion interna y autogestion del paciente - pero todavia arrastra deuda tecnica y de seguridad propia de una etapa MVP avanzada.",
    fill=(224, 242, 254),
    text_color=(3, 105, 161),
)

pdf.section("1. Vision del proyecto")
pdf.paragraph(
    "MediZen v2 no se siente como un sitio aislado ni como una simple app de agenda. Se siente como el inicio de un sistema vertical para una clinica o centro de bienestar, donde el negocio, la operacion interna y la experiencia del paciente comparten el mismo backend y la misma logica comercial."
)
pdf.bullet_list([
    "El frontend administrativo opera como Core de la clinica: dashboard, pacientes, citas, programas, membresias, configuracion y seguimiento.",
    "El portal de pacientes extiende ese Core hacia afuera: muestra planes, capta interesados, autentica pacientes y les permite autogestionar citas y membresias.",
    "El backend unifica autenticacion, modelo de datos, agenda, notificaciones y captacion publica.",
    "La pieza mas valiosa del modelo no es la agenda sino la continuidad terapeutica basada en membresias.",
])

pdf.section("2. Arquitectura observada", color=(22, 101, 52))
pdf.bullet_list([
    "Backend en FastAPI + SQLAlchemy + Pydantic, con routers separados por dominio funcional.",
    "Dos frontends React/Vite: uno para equipo interno y otro para pacientes.",
    "Persistencia con SQLite por defecto y soporte para PostgreSQL segun entorno.",
    "Autenticacion JWT para staff y pacientes.",
    "Capa de email SMTP configurable desde la aplicacion.",
    "Docker Compose presente como base de despliegue local, aunque la operacion real parece hibrida entre local, Vercel, Render y Neon.",
])
pdf.paragraph(
    "Conceptualmente la arquitectura esta bien encaminada: separa interfaces segun tipo de usuario, mantiene la logica de negocio en el backend y define un flujo de datos bastante claro entre captacion, registro, activacion y agenda."
)

pdf.section("3. Lo mejor que tiene hoy", color=(146, 64, 14))
pdf.bullet_list([
    "Hay una narrativa de producto clara: crear planes en el Core, publicarlos al portal, captar pacientes y llevarlos a autogestion.",
    "El Core ya cubre tareas reales del dia a dia de una clinica pequena o mediana.",
    "El portal paciente no es accesorio; agrega valor operativo porque reduce friccion para reservar horas y consultar estado.",
    "El modulo de settings y notificaciones abre una base para automatizaciones futuras.",
    "La documentacion, PDFs, scripts de arranque y capturas sugieren intencion de entrega y uso con usuarios reales.",
])

pdf.section("4. Valor de negocio percibido", color=(91, 33, 182))
pdf.paragraph(
    "El mayor potencial de MediZen v2 esta en convertirse en una herramienta de retencion y continuidad, no solo de administracion. La existencia de planes, sesiones, alertas, seguimiento IEIM y portal paciente le da al proyecto una base para capturar valor recurrente."
)
pdf.bullet_list([
    "Permite vender continuidad terapeutica en vez de citas aisladas.",
    "Puede conectar captacion digital con activacion comercial y seguimiento clinico.",
    "El IEIM puede transformarse en diferencial metodologico si luego alimenta renovaciones, alertas y progreso visible.",
    "A futuro tiene forma de SaaS nichado para medicina integrativa, bienestar o membresias terapeuticas.",
])

pdf.add_page()

pdf.section("5. Riesgos y debilidades principales", color=(153, 27, 27))
pdf.bullet_list([
    "Seguridad insuficiente para una etapa productiva: existen claves JWT hardcodeadas y configuraciones sensibles expuestas o demasiado abiertas.",
    "El modelo de membresias es fragil porque la asignacion se apoya en nombres de plan y no en relaciones fuertes por identificador.",
    "Se observan inconsistencias entre el modelo ORM y partes del codigo que esperan relaciones no definidas.",
    "Hay mezcla entre mocks, endpoints inexistentes, rutas hardcodeadas a localhost y comportamiento de entorno no totalmente cerrado.",
    "El repositorio acumula artefactos de ejecucion, bases locales, entornos virtuales y dependencias instaladas; eso perjudica mantenibilidad y colaboracion.",
    "La migracion entre prototipo y produccion aun no esta completamente normalizada; conviven create_all, scripts manuales y referencias a Alembic.",
])

pdf.section("6. Lectura de madurez", color=(30, 64, 175))
pdf.bullet_list([
    "Producto: prometedor y funcional.",
    "Arquitectura: suficiente para MVP real.",
    "Operacion: util para una implementacion controlada.",
    "Mantenibilidad: media a baja por deuda acumulada.",
    "Escalabilidad: limitada mientras el modelo de membresias y seguridad no se endurezcan.",
    "Listo para crecer: no todavia, pero si listo para una fase de consolidacion seria.",
])

pdf.section("7. Mi conclusion", color=(8, 47, 73))
pdf.paragraph(
    "MediZen v2 ya contiene la idea correcta. No intenta ser una suma de pantallas sueltas, sino un ecosistema clinico-comercial coherente. Su mayor fortaleza es que conecta adquisicion, operacion y experiencia del paciente bajo una misma logica de negocio. Eso le da potencial real."
)
pdf.paragraph(
    "Al mismo tiempo, el proyecto se encuentra en el punto clasico donde un MVP exitoso empieza a exigir disciplina de producto e ingenieria: seguridad, limpieza de repositorio, definicion mas fuerte del modelo de datos y cierre de las diferencias entre entorno local, demo y produccion."
)
pdf.callout(
    "Vision final: si el siguiente ciclo se enfoca en consolidacion tecnica, MediZen puede pasar de ser un sistema prometedor y funcional a una plataforma verdaderamente escalable para operacion clinica basada en membresias.",
    fill=(236, 253, 245),
    text_color=(22, 101, 52),
)

pdf.section("8. Prioridades sugeridas para una siguiente fase", color=(95, 58, 0))
pdf.bullet_list([
    "Cerrar brechas de seguridad y mover secretos a variables de entorno reales.",
    "Redisenar la relacion entre membresias y planes con referencias fuertes por ID.",
    "Separar claramente assets de trabajo, dependencias locales y archivos generados del codigo fuente.",
    "Formalizar migraciones y despliegue para evitar diferencias entre instancias.",
    "Definir una hoja de ruta de producto: captacion, pagos, renovacion, adherencia y analitica.",
])

pdf.output(OUTPUT_PATH)
print(f"PDF generado: {OUTPUT_PATH}")
