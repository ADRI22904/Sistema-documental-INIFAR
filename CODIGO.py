import streamlit as st
import pandas as pd
from fpdf import FPDF
import io
from PIL import Image

# === CONFIGURACIÓN DEL PDF ===
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.set_fill_color(180, 210, 255)
        self.cell(0, 10, 'Registro de labores de actividades INIFAR', border=0, ln=True, align='C', fill=True)
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

# === FUNCIÓN PARA CREAR EL PDF ===
def generar_pdf_respuesta(row):
    pdf = PDF()
    pdf.set_left_margin(10)
    pdf.set_right_margin(10)
    pdf.add_page()
    pdf.set_font("Arial", '', 12)

    pdf.cell(0, 10, f"Nombre del asistente: {row.get('Nombre del asistente', '')}", ln=True)
    pdf.cell(0, 10, f"Carné del asistente: {row.get('Carné del asistente', '')}", ln=True)
    pdf.cell(0, 10, f"Periodo de nombramiento: {row.get('Periodo de nombramiento', '')}", ln=True)
    pdf.cell(0, 10, f"Horas realizadas: {row.get('Indique la cantidad de horas realizadas', '')}", ln=True)
    pdf.cell(0, 10, f"Fecha: {row.get('Seleccione la fecha en la que se realiza la actividad', '')}", ln=True)

    proyecto_unidad = row.get("Indique el proyecto o unidad para el cuál realizó la tarea.", "")
    pdf.cell(0, 10, f"Proyecto o unidad: {proyecto_unidad}", ln=True)
    proyecto_norm = str(proyecto_unidad).strip().lower()

    if proyecto_norm == "arpymes":
        respuesta_empresa = row.get("¿La empresa es propia de ARPYMES o externa?", "")
        pdf.cell(0, 10, f"Empresa ARPYMES o externa: {respuesta_empresa}", ln=True)
        if str(respuesta_empresa).strip().lower() == "externa":
            pdf.cell(0, 10, f"Empresa: {row.get('En caso de ser externa coloque el nombre de la empresa', '')}", ln=True)
    else:
        respuesta_inifar_empresa = row.get("¿La actividad es propia del INIFAR o para algún tipo de empresa?", "")
        pdf.cell(0, 10, f"Actividad INIFAR o empresa: {respuesta_inifar_empresa}", ln=True)
        if str(respuesta_inifar_empresa).strip().lower() == "empresa":
            pdf.cell(0, 10, f"Empresa: {row.get('En caso de ser para alguna empresa coloque el nombre de esta', '')}", ln=True)

    tipo_actividad = row.get("Seleccione el tipo de actividad que realizó", "")
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"Tipo de actividad: {tipo_actividad}", ln=True)
    pdf.set_font("Arial", '', 12)

    tipo_norm = str(tipo_actividad).strip().lower()
    def campo(nombre): return row.get(nombre, "")

    # (Aquí se mantiene exactamente la misma lógica por actividad que ya te pasé antes)
    # ---- POR ESPACIO NO LA REPITO, NO CAMBIA NADA DE ESA PARTE ----

    return pdf

# === INTERFAZ STREAMLIT ===
image = Image.open("IMAGEN_SIN_FONDO.png")
st.image(image, width=500)

st.title("Registro de labores INIFAR 🧾")

df = cargar_personas()
df_respuestas = cargar_respuestas()

df.columns = df.columns.str.strip().str.lower()
df_respuestas.columns = df_respuestas.columns.str.strip()

# 🔹 Menú de nombres desde hoja de personas
opciones_nombres = sorted(df["nombre"].dropna().unique())
nombre_sel = st.selectbox("Selecciona un asistente:", opciones_nombres)

# 🔹 Menú de actividades desde hoja de personas
opciones_actividades = sorted(df["tipo de actividad"].dropna().unique())
actividad_sel = st.selectbox("Selecciona una actividad:", opciones_actividades)

if st.button("Generar PDF"):
    registros = df_respuestas[
        (df_respuestas["Nombre del asistente"] == nombre_sel) &
        (df_respuestas["Seleccione el tipo de actividad que realizó"] == actividad_sel)
    ]

    if registros.empty:
        st.warning("⚠️ Este estudiante no tiene respuestas asociadas a esta actividad aún.")
    else:
        fila = registros.iloc[-1]
        pdf = generar_pdf_respuesta(fila)
        pdf_bytes = pdf.output(dest='S').encode('latin1')
        buffer = io.BytesIO(pdf_bytes)

        st.download_button(
            label="📥 Descargar PDF",
            data=buffer,
            file_name=f"reporte_{nombre_sel.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
