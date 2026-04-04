import subprocess
import sys
from datetime import date

subprocess.run([sys.executable, "-m", "pip", "install", "fpdf2", "--quiet"], capture_output=True)

from fpdf import FPDF


REPORT_DATE = date.today().strftime("%d/%m/%Y")
OUTPUT_PATH = r"C:\Medizen\v2\Informe_Costos_Medizen_v2_corregido.pdf"


class PDF(FPDF):
    def header(self):
        self.set_fill_color(17, 24, 39)
        self.rect(0, 0, 210, 22, "F")
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 14)
        self.set_xy(10, 5)
        self.cell(0, 6, "Informe de costos - MediZen v2")
        self.set_font("Helvetica", "", 8)
        self.set_xy(10, 12)
        self.cell(0, 5, f"Infraestructura, tokens y costos ocultos | {REPORT_DATE}")
        self.set_text_color(0, 0, 0)
        self.set_y(28)

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

    def bullets(self, items):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        for item in items:
            self.multi_cell(0, 6, f"- {item}")
        self.ln(1)

    def callout(self, text, fill=(239, 246, 255), text_color=(30, 64, 175)):
        self.set_fill_color(*fill)
        self.set_text_color(*text_color)
        self.set_font("Helvetica", "I", 10)
        self.multi_cell(0, 6, f"  {text}", fill=True)
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def cost_row(self, concept, amount, note):
        self.set_fill_color(241, 245, 249)
        self.set_text_color(15, 23, 42)
        self.set_font("Helvetica", "B", 9)
        self.cell(0, 7, f"  {concept}: {amount}", ln=True, fill=True, border=1)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 6, f"  {note}", border=1)
        self.ln(1)


pdf = PDF("P", "mm", "A4")
pdf.set_margins(12, 30, 12)
pdf.set_auto_page_break(True, 14)
pdf.add_page()

pdf.title_block(
    "MediZen v2: cuanto cuesta tenerlo arriba en la nube",
    "Este documento analiza los costos mas probables del proyecto segun lo observado en el repositorio: frontends en Vercel, backend en Render, base de datos en Neon, correos SMTP y una capa de IA potencial con Gemini y Ollama.",
)

pdf.callout(
    "Conclusion corta: hoy el proyecto puede mantenerse en modo demo o piloto por muy poco dinero, incluso cerca de USD 0-15/mes. El salto real de costo aparece cuando se vuelve productivo, se exige disponibilidad estable, se agrega correo serio, se habilita IA en la nube o se requiere cumplimiento mas estricto para datos de salud.",
)

pdf.section("1. Lo que el proyecto parece usar hoy")
pdf.bullets([
    "Dos frontends desplegables en Vercel: `frontend` y `patient-frontend`.",
    "Un backend FastAPI apuntando a Render segun `frontend/vercel.json` y `backend/Procfile`.",
    "Base de datos con SQLite local por defecto y Neon PostgreSQL como destino cloud mencionado en documentacion y scripts.",
    "Correo saliente por SMTP configurable desde la app; hoy no depende de un proveedor transaccional especifico.",
    "IA en dos sabores: Gemini desde frontend y Ollama local desde backend.",
])

pdf.section("2. Costos de infraestructura base", color=(22, 101, 52))
pdf.paragraph("Tomando como referencia la estructura actual, estos son los componentes de costo mas probables:")
pdf.cost_row("Vercel", "USD 0 o USD 20+/mes", "Hobby puede servir para demo; Pro parte en USD 20 por usuario/mes.")
pdf.cost_row("Render backend", "USD 0 o USD 7+/mes", "Servicio web free para pruebas; Starter en torno a USD 7/mes para algo mas estable.")
pdf.cost_row("Neon DB", "USD 0 o USD 5-20+/mes", "Free sirve para piloto; plan Launch es uso variable y Neon declara gasto tipico cercano a USD 15/mes.")
pdf.cost_row("Dominio", "USD 10-20/anio", "Opcional si dejan subdominios de Vercel/Render; recomendable para imagen y correo.")
pdf.cost_row("SMTP / correo", "USD 0-20+/mes", "Puede operar con cuenta SMTP propia; si se profesionaliza, conviene Workspace o Resend.")

pdf.paragraph("Lectura practica por etapa:")
pdf.bullets([
    "Demo interna: Vercel Hobby + Render Free + Neon Free = costo cercano a USD 0/mes, con limitaciones y cold starts.",
    "Piloto serio: Vercel Pro + Render Starter + Neon pago liviano = aprox. USD 32-45/mes mas dominio y correo.",
    "Produccion pequena: Vercel Pro + backend estable + Neon pago + correo profesional = aprox. USD 45-80/mes.",
])

pdf.section("3. Correo y notificaciones", color=(146, 64, 14))
pdf.paragraph(
    "El proyecto envia pocos correos por evento. En el flujo actual, una inscripcion publica dispara un correo al administrador y otro al paciente. Una reserva de cita dispara al menos un correo al administrador. Eso hace que el volumen mensual sea bajo mientras la operacion sea pequena."
)
pdf.bullets([
    "Con 100 inscripciones/mes y 200 citas agendadas/mes, el sistema enviaria alrededor de 400 correos mensuales.",
    "Con 500 inscripciones/mes y 800 citas/mes, enviaria cerca de 1.800 correos mensuales.",
    "Eso cabe sin problema en planes pequenos o incluso gratuitos de varios proveedores transaccionales.",
])
pdf.cost_row("Google Workspace", "CLP 6.500+/usuario/mes", "Business Starter en Chile, util si quieren correo corporativo tipo admin@dominio.cl.")
pdf.cost_row("Resend", "USD 0 hasta 3.000 correos", "Luego Pro: USD 20/mes hasta 50.000 correos, mas overage.")
pdf.callout(
    "En este proyecto el correo no sera el driver principal de costo al inicio. El valor del correo es mas de imagen, entregabilidad y seguridad operacional que de volumen.",
    fill=(254, 249, 195),
    text_color=(133, 77, 14),
)

pdf.add_page()

pdf.section("4. Costos de IA y tokens", color=(91, 33, 182))
pdf.paragraph(
    "Aqui hay una diferencia importante: el backend trae un endpoint para Ollama local, lo que no genera costo por token en la nube. En paralelo, el frontend incluye un servicio Gemini con modelos premium, lo que si podria generar costo variable si se activa con una API key real y se conecta a la interfaz."
)
pdf.bullets([
    "Ollama local: costo cloud por token = cero; costo real = CPU, RAM, electricidad y mantener una maquina encendida.",
    "Gemini en frontend: costo cloud variable segun tokens de entrada y salida, y segun el modelo finalmente contratado.",
    "Hoy, por el codigo observado, la capa Gemini parece preparada pero no claramente integrada en pantallas activas; por eso su costo actual probable es cero o casi cero.",
])

pdf.paragraph("Estimacion de tokens por tipo de operacion si Gemini se habilita:")
pdf.cost_row("Consulta estructurada", "700-1.500 in / 300-800 out", "Ejemplo: diferenciar sindrome desde un JSON clinico mediano.")
pdf.cost_row("Chat clinico", "150-800 in / 150-600 out", "Cada turno simple de conversacion o apoyo clinico.")
pdf.cost_row("Prompt largo", "2.000-6.000 in / 500-1.500 out", "Si se agregan historia, examen, varios campos y contexto largo.")
pdf.cost_row("TTS", "No usar texto-token puro", "Normalmente se cobra por caracteres, segundos o modalidad especial; requiere revisar el proveedor exacto.")

pdf.paragraph("Escenarios de consumo mensual para IA textual:")
pdf.bullets([
    "100 consultas mensuales de 1.200 tokens de entrada y 500 de salida = 120.000 tokens in + 50.000 tokens out.",
    "500 consultas mensuales del mismo tamano = 600.000 tokens in + 250.000 tokens out.",
    "2.000 consultas mensuales del mismo tamano = 2,4M tokens in + 1,0M tokens out.",
])

pdf.paragraph("Formula simple para proyectar costo mensual de IA:")
pdf.callout(
    "Costo IA = (tokens_entrada / 1.000.000 x tarifa_entrada) + (tokens_salida / 1.000.000 x tarifa_salida)",
    fill=(237, 233, 254),
    text_color=(88, 28, 135),
)
pdf.paragraph(
    "Como la tarifa cambia segun el modelo y la modalidad, la decision importante no es solo 'usar IA', sino definir que casos de uso realmente ameritan modelo premium. Para un sistema como MediZen, una mala decision aqui puede hacer que la IA cueste mas que toda la infraestructura base."
)

pdf.section("5. Mi lectura sobre IA en este proyecto", color=(30, 64, 175))
pdf.bullets([
    "Si se usa solo Ollama local para pruebas o asistente interno, el costo monetario directo puede ser casi cero.",
    "Si se activa Gemini Pro para asistencia clinica, chat o analisis estructurado, el costo empieza a escalar por uso y conviene poner limites de presupuesto.",
    "El archivo actual expone la idea de pasar `GEMINI_API_KEY` al frontend; eso no solo puede elevar costos, tambien aumenta riesgo de fuga de clave y consumo no controlado.",
    "La mejor practica economica y de seguridad seria mover cualquier IA paga al backend, con cuotas, logs y limites por usuario o por accion.",
])

pdf.section("6. Costos menos visibles pero importantes", color=(153, 27, 27))
pdf.bullets([
    "Observabilidad: logs, errores y trazas. Si luego agregan Sentry, Logtail o equivalente, aparece otro costo mensual.",
    "Backups y retencion: Neon puede seguir siendo barato, pero ventanas largas de restore y mas almacenamiento suben la cuenta.",
    "Cumplimiento y datos sensibles: al manejar pacientes, un entorno realmente productivo puede requerir BAAs, mejores controles y planes mas caros. Solo Vercel ya publica un add-on HIPAA BAA de USD 350/mes en Pro.",
    "Soporte y cuentas de equipo: Vercel y Render cobran por usuario en planes pagos, por lo que una app barata puede crecer en costo si entra mas equipo tecnico.",
    "Tiempo de ingenieria: no sale en la factura cloud, pero es uno de los costos reales mas altos si hay que mantener despliegues, incidencias y seguridad.",
])

pdf.section("7. Escenarios de costo recomendados", color=(8, 47, 73))
pdf.cost_row("Escenario A - demo", "USD 0-15/mes", "Subdominios gratis, servicios free, base free y correo minimo.")
pdf.cost_row("Escenario B - piloto estable", "USD 35-60/mes", "1 Vercel Pro, backend pago chico, Neon liviano, dominio y correo profesional minimo.")
pdf.cost_row("Escenario C - produccion pequena", "USD 60-120/mes", "Mas estabilidad, mejor correo, mas almacenamiento, monitoreo liviano y margen operativo.")
pdf.cost_row("Escenario D - salud/compliance", "USD 300+/mes", "Cuando se busca formalidad, controles y cumplimiento, la cuenta sube rapido aunque el trafico aun sea bajo.")

pdf.paragraph("Si se habilita IA paga, el costo del escenario puede subir de forma adicional. En una operacion de bajo uso, el impacto podria ser menor. En una operacion intensiva con prompts largos, la IA puede superar el gasto mensual de hosting sin demasiado esfuerzo.")

pdf.section("8. Conclusiones y recomendacion final", color=(95, 58, 0))
pdf.bullets([
    "MediZen v2 es barato de sostener mientras opere como demo o piloto controlado.",
    "La infraestructura base no es el principal problema economico; el riesgo mayor esta en compliance, seguridad y una IA mal controlada.",
    "El correo no deberia preocupar al inicio por costo, pero si por reputacion y dominio propio.",
    "Si se decide usar IA real, conviene presupuestarla aparte y no mezclarla con el costo base de hosting.",
    "Mi recomendacion: separar presupuesto en dos bolsas: infraestructura fija y consumo variable de IA. Eso evita sorpresas.",
])

pdf.section("9. Fuentes usadas para la estimacion", color=(22, 101, 52))
pdf.bullets([
    "Observacion del propio repositorio: Vercel, Render, Neon, SMTP, Gemini y Ollama.",
    "Paginas publicas de pricing revisadas durante este analisis: Vercel, Render, Neon, Google Workspace y Resend.",
    "Las cifras de IA se presentan como estimaciones operativas porque el costo exacto depende del modelo final, la modalidad y la tarifa vigente al momento de contratar.",
])

pdf.output(OUTPUT_PATH)
print(f"PDF generado: {OUTPUT_PATH}")
