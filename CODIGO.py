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

# === FUNCIÓN PARA CREAR EL PDF DE UNA RESPUESTA ===
def generar_pdf_respuesta(row):
    pdf = PDF()
    pdf.set_left_margin(10)
    pdf.set_right_margin(10)
    pdf.add_page()

    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Nombre del asistente: {row.get('Nombre del asistente', '')}", ln=True)
    pdf.cell(0, 10, f"Carné: {row.get('Carné del asistente', '')}", ln=True)
    pdf.cell(0, 10, f"Periodo de nombramiento: {row.get('Periodo de nombramiento', '')}", ln=True)
    pdf.cell(0, 10, f"Cantidad de horas realizadas: {row.get('Indique la cantidad de horas realizadas', '')}", ln=True)
    pdf.cell(0, 10, f"Fecha de realización: {row.get('Seleccione la fecha en la que se realiza la actividad', '')}", ln=True)
    #pdf.cell(0, 10, f"Tipo de proyecto: {row.get('Tipo de proyecto', '')}", ln=True)
    #pdf.cell(0, 10, f"Tipo de actividad: {row.get('Tipo de actividad', '')}", ln=True)
    #pdf.ln(5)

    #tipo_proyecto = str(row.get('Tipo de proyecto', '')).strip().lower()
    #tipo_actividad = str(row.get('Tipo de actividad', '')).strip().lower()

    # Información general
    #pdf.set_font("Arial", 'B', 12)
    #pdf.cell(0, 10, "Información general:", ln=True)
    #pdf.set_font("Arial", '', 11)
    #pdf.multi_cell(0, 8, f"Objetivo de la actividad:\n{row.get('Objetivo', '')}")
    #pdf.multi_cell(0, 8, f"Lugar:\n{row.get('Lugar', '')}")
    #pdf.ln(5)

    # Condicional por tipo de proyecto
    #if "arpymes" in tipo_proyecto:
        #pdf.set_font("Arial", 'B', 12)
        #pdf.cell(0, 10, "Detalles del proyecto ARPYMES:", ln=True)
        #pdf.set_font("Arial", '', 11)
        #pdf.multi_cell(0, 8, f"Nombre del proyecto: {row.get('Nombre del proyecto ARPYMES', '')}")
        #pdf.multi_cell(0, 8, f"Investigador responsable: {row.get('Investigador responsable', '')}")
        #pdf.ln(5)

    #elif "fic" in tipo_proyecto:
        #pdf.set_font("Arial", 'B', 12)
        #pdf.cell(0, 10, "Detalles del proyecto FIC:", ln=True)
        #pdf.set_font("Arial", '', 11)
        #pdf.multi_cell(0, 8, f"Nombre del proyecto: {row.get('Nombre del proyecto FIC', '')}")
        #pdf.multi_cell(0, 8, f"Coordinador: {row.get('Coordinador FIC', '')}")
        #pdf.ln(5)

    # Condicional por tipo de actividad
    #if "gira" in tipo_actividad:
        #pdf.set_font("Arial", 'B', 12)
        #pdf.cell(0, 10, "Detalles de la gira:", ln=True)
        #pdf.set_font("Arial", '', 11)
        #pdf.multi_cell(0, 8, f"Participantes:\n{row.get('Participantes', '')}")
        #pdf.multi_cell(0, 8, f"Resultados esperados:\n{row.get('Resultados esperados', '')}")

    #elif "formulación" in tipo_actividad:
        #pdf.set_font("Arial", 'B', 12)
        #pdf.cell(0, 10, "Detalles de formulación de proyecto:", ln=True)
        #pdf.set_font("Arial", '', 11)
        #pdf.multi_cell(0, 8, f"Descripción de la propuesta:\n{row.get('Descripción del proyecto', '')}")

    #else:
        #pdf.set_font("Arial", 'B', 12)
        #pdf.cell(0, 10, "Otra actividad:", ln=True)
        #pdf.set_font("Arial", '', 11)
        #pdf.multi_cell(0, 8, f"Descripción:\n{row.get('Descripción', '')}")

    return pdf

# === INTERFAZ STREAMLIT (SE QUEDA IGUAL) ===
image = Image.open("IMAGEN_SIN_FONDO.png")
st.image(image, width=500)

st.title("Registro de labores INIFAR 🧾")

df = cargar_personas()            # 👈 Para la interfaz (NO se toca)
df_respuestas = cargar_respuestas()  # 👈 Para el PDF

st.write("Total de respuestas cargadas:", len(df))

# Selección de registro por nombre (IGUAL)
opciones = sorted(df["Nombre"].dropna().unique())
nombre_sel = st.selectbox("Selecciona un asistente:", opciones)

# Selección de actividad (IGUAL)
actividades = sorted(df["Tipo de actividad"].dropna().unique())
actividad_sel = st.selectbox("Selecciona una actividad:", actividades)

if st.button("Generar PDF"):
    fila = df_respuestas[
        (df_respuestas["Nombre completo"] == nombre_sel) &
        (df_respuestas["Tipo de actividad"] == actividad_sel)
    ].iloc[0]

    pdf = generar_pdf_respuesta(fila)
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    buffer = io.BytesIO(pdf_bytes)

    st.download_button(
        label="📥 Descargar PDF",
        data=buffer,
        file_name=f"reporte_{nombre_sel.replace(' ', '_')}.pdf",
        mime="application/pdf"
    )

