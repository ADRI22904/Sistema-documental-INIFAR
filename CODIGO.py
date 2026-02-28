import streamlit as st
import pandas as pd
from fpdf import FPDF
import io
from PIL import Image
import os

# === CONFIGURACIÓN DEL PDF ===
class PDF(FPDF):
    def __init__(self, titulo):
        super().__init__()
        self.titulo = titulo

    def header(self):
        if os.path.exists("IMAGEN_SIN_FONDO.png"):
            self.image("IMAGEN_SIN_FONDO.png", x=160, y=8, w=35)

        self.ln(20)
        self.set_font('Arial', 'B', 14)
        self.set_fill_color(180, 210, 255)
        self.cell(0, 10, self.titulo, border=0, ln=True, align='C', fill=True)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')


# === CARGAR DATOS DESDE GOOGLE SHEETS ===
def cargar_respuestas():
    sheet_id_respuestas = "1222LBCTgivujNTB8YL17QrJXDH6eRqUKCZG8UKrskbc"
    url_respuestas = f"https://docs.google.com/spreadsheets/d/{sheet_id_respuestas}/export?format=csv"
    return pd.read_csv(url_respuestas)

def cargar_personas():
    sheet_id_personas = "1oQ6I-GV56ubn4MLlrRGC91tFCR7YE2uyHdOm5Rc4lFE"
    url_personas = f"https://docs.google.com/spreadsheets/d/{sheet_id_personas}/export?format=csv"
    return pd.read_csv(url_personas)


# === FUNCIÓN REUTILIZABLE PARA PINTAR DETALLE SEGÚN TIPO DE ACTIVIDAD ===
def pintar_detalle_por_tipo(pdf, row, tipo_actividad):
    def campo(nombre): 
        return row.get(nombre, "")

    tipo_norm = str(tipo_actividad).strip().lower()

    if tipo_norm == "sesión de trabajo con empresa":
        pdf.multi_cell(0, 8, f"Docentes: {campo('Seleccione el o los nombres de los docentes responsables de la reunión')}")
        pdf.multi_cell(0, 8, f"Horario: {campo('Indique el horario en el que realizó la reunión')}")
        pdf.multi_cell(0, 8, f"Modalidad: {campo('Seleccione la modalidad de la reunión')}")
        pdf.multi_cell(0, 8, f"Lugar: {campo('Indique el lugar o plataforma por la cuál se desarrolló la reunión')}")
        pdf.multi_cell(0, 8, f"Empresa: {campo('Seleccione el nombre de la empresa para la cual realizó la actividad')}")
        pdf.multi_cell(0, 8, f"Provincia: {campo('Seleccione la provincia donde se ubica la empresa')}")
        pdf.multi_cell(0, 8, f"Estudiantes: {campo('Indique el nombre  de los estudiantes participantes')}")
        pdf.multi_cell(0, 8, f"Personas empresa: {campo('Indique el nombre de las personas de la empresa que participan de la reunión')}")
        pdf.multi_cell(0, 8, f"Población beneficiaria: {campo('Indique la población beneficiaria de la sesión (los que reciben el apoyo)')}")
        pdf.multi_cell(0, 8, f"Tipo de apoyo: {campo('Seleccione el(los) tipo(s) de apoyo(s) solicitado(s) por la empresa')}")
        pdf.multi_cell(0, 8, f"Descripción: {campo('Descripción de la actividad')}")
        pdf.multi_cell(0, 8, f"Fotos: {campo('Favor incluir 1 fotografías de las actividades realizadas ')}")

        contacto = campo("Indique el contacto de la empresa")
        pdf.multi_cell(0, 8, f"Contacto: {contacto}")
        if str(contacto).lower() == "teléfono":
            pdf.multi_cell(0, 8, f"Teléfono: {campo('Ingrese el número de teléfono de contacto de la empresa')}")
        elif str(contacto).lower() == "correo electrónico":
            pdf.multi_cell(0, 8, f"Correo: {campo('Indique el correo electrónico de la empresa')}")

    elif tipo_norm == "apoyo logístico":
        pdf.multi_cell(0, 8, f"Empresa: {campo('Seleccione el nombre de la empresa para la cual se realizó la actividad')}")
        pdf.multi_cell(0, 8, f"Detalle: {campo('Indique de manera detallada la actividad de apoyo logístico brindado')}")
        pdf.multi_cell(0, 8, f"Fotos: {campo('Adjunte 2 fotografías como registro fotográfico')}")
        pdf.multi_cell(0, 8, f"Documentos: {campo('Coloque la referencia a todos los documentos generados.')}")

    elif tipo_norm == "giras":
        provincia = campo("Seleccione la provincia del lugar donde se realizó la gira")
        pdf.multi_cell(0, 8, f"Empresa: {campo('Seleccione el nombre de la empresa para la cual se realizó la actividad')}")
        pdf.multi_cell(0, 8, f"Provincia: {provincia}")
        pdf.multi_cell(0, 8, f"Objetivo: {campo('Describa el objetivo de la gira o visita y las actividades realizadas en la misma.')}")

    elif tipo_norm == "revisión bibliográfica":
        pdf.multi_cell(0, 8, f"Tema: {campo('Indique el tema a investigar a través de la revisión bibliográfica')}")
        pdf.multi_cell(0, 8, f"Aportes: {campo('Indique aspectos relevantes encontrados en el documento, y que representen un aporte sustancioso para el proyecto y el trabajo en el laboratorio.')}")

    elif tipo_norm == "pruebas de laboratorio":
        pdf.multi_cell(0, 8, f"Empresa: {campo('Seleccione el nombre de la empresa para la cual se realizó la actividad')}")
        pdf.multi_cell(0, 8, f"Laboratorio: {campo('Indique el laboratorio donde se realizaron las pruebas')}")

    elif tipo_norm == "sesiones de trabajo con equipo inifar":
        pdf.multi_cell(0, 8, f"Docentes: {campo('Seleccione el o los nombres de los docentes responsables de la reunión')}")
        pdf.multi_cell(0, 8, f"Horario: {campo('Indique el horario en el que realizó la reunión')}")

    elif tipo_norm == "otras actividades":
        pdf.multi_cell(0, 8, f"Detalle: {campo('Describir, de manera detallada, la actividad realizada para el proyecto.')}")


# === FUNCIÓN PDF INDIVIDUAL ===
def generar_pdf_respuesta(registros, tipo_actividad):
    pdf = PDF(f"Registro de {tipo_actividad.title()}")
    pdf.set_left_margin(10)
    pdf.set_right_margin(10)
    pdf.add_page()
    pdf.set_font("Arial", '', 12)

    fila_base = registros.iloc[0]
    pdf.cell(0, 10, f"Nombre del asistente: {fila_base.get('Nombre del asistente', '')}", ln=True)
    pdf.cell(0, 10, f"Carné del asistente: {fila_base.get('Carné del asistente', '')}", ln=True)
    pdf.cell(0, 10, f"Periodo de nombramiento: {fila_base.get('Periodo de nombramiento', '')}", ln=True)
    pdf.ln(5)

    for _, row in registros.iterrows():
        pdf.set_fill_color(180, 210, 255)
        pdf.cell(0, 3, "", ln=True, fill=True)
        pdf.ln(3)

        pdf.cell(0, 10, f"Horas realizadas: {row.get('Indique la cantidad de horas realizadas', '')}", ln=True)
        pdf.cell(0, 10, f"Fecha: {row.get('Seleccione la fecha en la que se realiza la actividad', '')}", ln=True)
        pdf.cell(0, 10, f"Proyecto o unidad: {row.get('Indique el proyecto o unidad para el cuál realizó la tarea.', '')}", ln=True)

        pintar_detalle_por_tipo(pdf, row, tipo_actividad)

    return pdf


# === FUNCIÓN PDF CONSOLIDADO ===
def generar_pdf_consolidado(registros, unidad, tipo_actividad):
    pdf = PDF(f"Informe consolidado - {unidad} - {tipo_actividad.title()}")
    pdf.set_left_margin(10)
    pdf.set_right_margin(10)
    pdf.add_page()
    pdf.set_font("Arial", '', 12)

    pdf.cell(0, 10, f"Unidad / Proyecto: {unidad}", ln=True)
    pdf.cell(0, 10, f"Actividad: {tipo_actividad}", ln=True)
    pdf.cell(0, 10, f"Total de registros: {len(registros)}", ln=True)
    pdf.ln(5)

    for _, row in registros.iterrows():
        pdf.set_fill_color(180, 210, 255)
        pdf.cell(0, 3, "", ln=True, fill=True)
        pdf.ln(3)

        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, f"Asistente: {row.get('Nombre del asistente', '')}", ln=True)

        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, f"Carné: {row.get('Carné del asistente', '')}", ln=True)
        pdf.cell(0, 10, f"Fecha: {row.get('Seleccione la fecha en la que se realiza la actividad', '')}", ln=True)
        pdf.cell(0, 10, f"Horas: {row.get('Indique la cantidad de horas realizadas', '')}", ln=True)
        pdf.cell(0, 10, f"Proyecto o unidad: {row.get('Indique el proyecto o unidad para el cuál realizó la tarea.', '')}", ln=True)

        pintar_detalle_por_tipo(pdf, row, tipo_actividad)

    return pdf


# === INTERFAZ STREAMLIT ===
image = Image.open("IMAGEN_SIN_FONDO.png")
st.image(image, width=500)

st.title("Registro de labores INIFAR 🧾")

df = cargar_personas()
df_respuestas = cargar_respuestas()

df.columns = df.columns.str.strip().str.lower()
df_respuestas.columns = df_respuestas.columns.str.strip()

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

opciones_nombres = sorted(df["nombre"].dropna().unique())
nombre_sel = st.selectbox("Selecciona un asistente:", opciones_nombres)
password_input = st.text_input("Ingrese su contraseña:", type="password")

if st.button("Validar contraseña"):
    fila_persona = df[df["nombre"] == nombre_sel]
    if not fila_persona.empty:
        if password_input.strip() == str(fila_persona.iloc[0]["contraseña"]).strip():
            st.success("✅ Acceso correcto")
            st.session_state.autenticado = True
        else:
            st.error("❌ Contraseña incorrecta")

if st.session_state.autenticado:
    opciones_actividades = sorted(df["tipo de actividad"].dropna().unique())
    actividad_sel = st.selectbox("Selecciona una actividad:", opciones_actividades)

    unidades = [
        "ARPYMES",
        "LAFITEC",
        "LAPONABI",
        "BIOEQUIVALENCIA",
        "Análisis de estado sólido",
        "Formulación de productos"
    ]
    unidad_sel = st.selectbox("Selecciona el proyecto / unidad:", unidades)

    if st.button("📄 Generar PDF individual"):
        registros = df_respuestas[
            (df_respuestas["Nombre del asistente"] == nombre_sel) &
            (df_respuestas["Seleccione el tipo de actividad que realizó"] == actividad_sel)
        ]

        if registros.empty:
            st.warning("⚠️ No hay registros para este asistente y actividad.")
        else:
            pdf = generar_pdf_respuesta(registros, actividad_sel)
            buffer = io.BytesIO(pdf.output(dest='S').encode('latin1'))

            st.download_button(
                "📥 Descargar PDF individual",
                data=buffer,
                file_name=f"reporte_{nombre_sel.replace(' ', '_')}.pdf",
                mime="application/pdf"
            )

    if st.button("📊 Generar PDF consolidado por unidad y actividad"):
        registros = df_respuestas[
            (df_respuestas["Indique el proyecto o unidad para el cuál realizó la tarea."].str.strip().str.lower() == unidad_sel.strip().lower()) &
            (df_respuestas["Seleccione el tipo de actividad que realizó"] == actividad_sel)
        ]

        if registros.empty:
            st.warning("⚠️ No hay registros para esa unidad y actividad.")
        else:
            pdf = generar_pdf_consolidado(registros, unidad_sel, actividad_sel)
            buffer = io.BytesIO(pdf.output(dest='S').encode('latin1'))

            st.download_button(
                "📥 Descargar PDF consolidado",
                data=buffer,
                file_name=f"reporte_{unidad_sel.replace(' ', '_')}_{actividad_sel.replace(' ', '_')}.pdf",
                mime="application/pdf"
            )
