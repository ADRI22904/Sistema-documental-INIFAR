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
    pdf.cell(0, 10, f"Nombre del asistente: {row['Nombre del asistente']}", ln=True)
    pdf.cell(0, 10, f"Carné del asistente: {row['Carné del asistente']}", ln=True)
    pdf.cell(0, 10, f"Periodo de nombramiento: {row['Periodo de nombramiento']}", ln=True)
    pdf.cell(0, 10, f"Cantidad de horas realizadas: {row['Indique la cantidad de horas realizadas']}", ln=True)
    pdf.cell(0, 10, f"Fecha de la actividad: {row['Seleccione la fecha en la que se realiza la actividad']}", ln=True)

    return pdf

# === INTERFAZ STREAMLIT ===
image = Image.open("IMAGEN_SIN_FONDO.png")
st.image(image, width=500)
st.title("Registro de labores INIFAR 🧾")

df_personas = cargar_personas()
df_respuestas = cargar_respuestas()

st.write("Total de personas cargadas:", len(df_personas))
st.write("Total de respuestas cargadas:", len(df_respuestas))

# Selección de asistente
opciones_personas = df_respuestas["Nombre del asistente"].dropna().unique()
nombre_asistente = st.selectbox("Selecciona un asistente:", opciones_personas)

# Selección de actividad
opciones_actividad = df_respuestas["Tipo de actividad"].dropna().unique()
actividad_sel = st.selectbox("Selecciona una actividad:", opciones_actividad)

if st.button("Generar PDF"):
    filtro = (
        (df_respuestas["Nombre del asistente"] == nombre_asistente) &
        (df_respuestas["Tipo de actividad"] == actividad_sel)
    )

    if df_respuestas[filtro].empty:
        st.error("❌ No se encontró ninguna actividad para ese asistente.")
    else:
        fila = df_respuestas[filtro].iloc[0]
        pdf = generar_pdf_respuesta(fila)

        pdf_str = pdf.output(dest='S')
        pdf_bytes = pdf_str.encode('latin1')
        buffer = io.BytesIO(pdf_bytes)

        st.download_button(
            label="📥 Descargar PDF",
            data=buffer,
            file_name=f"reporte_{nombre_asistente.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
