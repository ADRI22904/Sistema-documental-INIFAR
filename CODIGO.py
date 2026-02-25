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


    # === TIPO DE ACTIVIDAD ===
    tipo_actividad = row.get("Seleccione el tipo de actividad que realizó", "")
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"Tipo de actividad: {tipo_actividad}", ln=True)
    pdf.set_font("Arial", '', 12)

    tipo_norm = str(tipo_actividad).strip().lower()
    def campo(nombre): return row.get(nombre, "")

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
        pdf.multi_cell(0, 8, f"Fotos: {campo('Adjunte 2 fotografías como registro fotográfico')}")

        cantones = {
            "San José": "Cantones de San José",
            "Cartago": "Cantones de Cartago",
            "Heredia": "Cantones de Heredia",
            "Alajuela": "Cantones de Alajuela",
            "Puntarenas": "Cantones de Puntarenas",
            "Guanacaste": "Cantones de Guanacaste",
            "Limón": "Cantones de Limón"
        }

        if provincia in cantones:
            pdf.multi_cell(0, 8, f"Cantón: {campo(cantones[provincia])}")

        pdf.multi_cell(0, 8, f"Distrito: {campo('Indique el distrito del lugar donde se realizó la gira')}")
        pdf.multi_cell(0, 8, f"Barrio: {campo('Indique el barrio o comunidad del lugar donde se realizó la gira')}")

    elif tipo_norm == "revisión bibliográfica":
        pdf.multi_cell(0, 8, f"Tema: {campo('Indique el tema a investigar a través de la revisión bibliográfica')}")
        pdf.multi_cell(0, 8, f"Aportes: {campo('Indique aspectos relevantes encontrados en el documento, y que representen un aporte sustancioso para el proyecto y el trabajo en el laboratorio.')}")
        pdf.multi_cell(0, 8, f"Documento: {campo('Agregue un documento PDF con una tabla que contenga el título del artículo, enlace y abstract.')}")

    elif tipo_norm == "pruebas de laboratorio":
        pdf.multi_cell(0, 8, f"Empresa: {campo('Seleccione el nombre de la empresa para la cual se realizó la actividad')}")
        pdf.multi_cell(0, 8, f"Laboratorio: {campo('Indique el laboratorio donde se realizaron las pruebas')}")
        pdf.multi_cell(0, 8, f"Estatus: {campo('Indique el estatus de la actividad realizada')}")
        pdf.multi_cell(0, 8, f"Número de pruebas: {campo('Indique el número de pruebas por tipo de apoyo')}")
        pdf.multi_cell(0, 8, f"Drive: {campo('Adjuntar el enlace del documento del drive del esquema general del proyecto donde se detallen los pasos generales del ensayo o prueba a realizar.')}")
        pdf.multi_cell(0, 8, f"Tipo de prueba: {campo('Seleccione el tipo de prueba realizada')}")
        pdf.multi_cell(0, 8, f"Formulación: {campo('Describa detalladamente el tipo de formulación con extracto detallada y la cantidad de formulaciones')}")
        pdf.multi_cell(0, 8, f"Resultados: {campo('Agregar un resumen de los resultados obtenidos (incluya resultados relevantes o poco esperados)')}")
        pdf.multi_cell(0, 8, f"Registro fotográfico: {campo('Registro fotográfico')}")

    elif tipo_norm == "sesiones de trabajo con equipo inifar":
        pdf.multi_cell(0, 8, f"Docentes: {campo('Seleccione el o los nombres de los docentes responsables de la reunión')}")
        pdf.multi_cell(0, 8, f"Horario: {campo('Indique el horario en el que realizó la reunión')}")
        pdf.multi_cell(0, 8, f"Modalidad: {campo('Seleccione la modalidad de la reunión')}")
        pdf.multi_cell(0, 8, f"Lugar: {campo('Indique el lugar o plataforma por la cuál se desarrolló la reunión')}")
        pdf.multi_cell(0, 8, f"Estudiantes: {campo('Indique el nombre  de los estudiantes participantes')}")
        pdf.multi_cell(0, 8, f"Personas INIFAR: {campo('Indique los nombres de las personas del INIFAR que participan de la reunión')}")
        pdf.multi_cell(0, 8, f"Descripción: {campo('Descripción de la actividad')}")
        pdf.multi_cell(0, 8, f"Fotos: {campo('Favor incluir 1 fotografías de las actividades realizadas ')}")

    elif tipo_norm == "otras actividades":
        pdf.multi_cell(0, 8, f"Empresa: {campo('Si aplica seleccione el nombre de la empresa para la cual se realizó la actividad')}")
        pdf.multi_cell(0, 8, f"Estado: {campo('Estado de la actividad')}")
        pdf.multi_cell(0, 8, f"Detalle: {campo('Describir, de manera detallada, la actividad realizada para el proyecto.')}")
        pdf.multi_cell(0, 8, f"Evidencia: {campo('Evidencia fotográfica')}")
        pdf.multi_cell(0, 8, f"Anexos: {campo('Anexos')}")

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
