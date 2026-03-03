import streamlit as st
import pandas as pd
from fpdf import FPDF
import io
from PIL import Image
import os
import requests
from tempfile import NamedTemporaryFile

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

# Insertar imagen
def insertar_imagen_desde_url(pdf, url, ancho=100):
    try:
        if pd.isna(url) or str(url).strip() == "":
            return

        # Si vienen varios enlaces separados por coma
        enlaces = str(url).split(",")

        for enlace in enlaces:
            enlace = enlace.strip()

            if "drive.google.com" in enlace:
                # Convertir link de Drive a descarga directa
                file_id = enlace.split("/d/")[1].split("/")[0]
                enlace = f"https://drive.google.com/uc?export=download&id={file_id}"

            response = requests.get(enlace)

            if response.status_code == 200:
                with NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                    tmp.write(response.content)
                    tmp_path = tmp.name

                pdf.ln(5)
                pdf.image(tmp_path, w=ancho)
                pdf.ln(5)

                os.remove(tmp_path)

    except Exception as e:
        pdf.multi_cell(0, 8, "⚠️ No se pudo cargar la imagen.")



# === FUNCIÓN PARA CREAR EL PDF ===
def generar_pdf_respuesta(registros, titulo_pdf, tipo_actividad):
    pdf = PDF(titulo_pdf)
    pdf.set_left_margin(10)
    pdf.set_right_margin(10)
    pdf.add_page()
    pdf.set_font("Arial", '', 12)

    # 🔹 Datos generales SOLO UNA VEZ
    asistente_actual = None

    for _, row in registros.iterrows():

        # Evita que se "pierdan" registros al final de la página
        if pdf.get_y() > 250:
            pdf.add_page()
            pdf.set_font("Arial", '', 12)

        nombre_asistente = str(row.get("Nombre del asistente", "")).strip().lower()
        nombre_asistente_mostrar = str(row.get("Nombre del asistente", "")).strip()
    
        # Si cambia el asistente, imprimimos encabezado nuevo
        if nombre_asistente != asistente_actual:
            asistente_actual = nombre_asistente

            pdf.ln(5)
            pdf.set_fill_color(200, 230, 255)
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, f"Asistente: {nombre_asistente_mostrar}", ln=True, fill=True)

            pdf.set_font("Arial", "", 12)
            pdf.cell(0, 8, f"Carné: {row.get('Carné del asistente', '')}", ln=True)
            pdf.cell(0, 8, f"Periodo de nombramiento: {row.get('Periodo de nombramiento', '')}", ln=True)
            pdf.ln(3)

        # 🔹 División celeste
        pdf.set_fill_color(180, 210, 255)
        pdf.cell(0, 3, "", ln=True, fill=True)
        pdf.ln(3)

        pdf.set_font("Arial", '', 12)
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
    

        tipo_norm = str(tipo_actividad).strip().lower()
        def campo(nombre): return row.get(nombre, "")

        if tipo_norm == "sesión de trabajo con empresa":
            pdf.multi_cell(0, 8, f"Docentes: {campo('Seleccione el o los nombres de los docentes responsables de la reunión ')}")
            pdf.multi_cell(0, 8, f"Horario: {campo('Indique el horario en el que realizó la reunión ')}")
            pdf.multi_cell(0, 8, f"Modalidad: {campo('Seleccione la modalidad de la reunión ')}")
            pdf.multi_cell(0, 8, f"Lugar: {campo('Indique el lugar o plataforma por la cuál se desarrolló la reunión')}")
            pdf.multi_cell(0, 8, f"Empresa: {campo('Seleccione el nombre de la empresa para la cual realizó la actividad')}")
            pdf.multi_cell(0, 8, f"Provincia: {campo('Seleccione la provincia donde se ubica la empresa')}")
            pdf.multi_cell(0, 8, f"Estudiantes: {campo('Indique el nombre  de los estudiantes participantes')}")
            pdf.multi_cell(0, 8, f"Personas empresa: {campo('Indique el nombre de las personas de la empresa que participan de la reunión')}")
            pdf.multi_cell(0, 8, f"Población beneficiaria: {campo('Indique la población beneficiaria de la sesión (los que reciben el apoyo)')}")
            pdf.multi_cell(0, 8, f"Tipo de apoyo: {campo('Seleccione el(los) tipo(s) de apoyo(s) solicitado(s) por la empresa')}")
            pdf.multi_cell(0, 8, f"Descripción: {campo('Descripción de la actividad')}")
            pdf.multi_cell(0, 8, "Registro fotográfico:")
            insertar_imagen_desde_url(pdf, campo('Favor incluir 1 fotografías de las actividades realizadas '))
            

            contacto = campo("Indique el contacto de la empresa")
            pdf.multi_cell(0, 8, f"Contacto: {contacto}")
            if str(contacto).lower() == "teléfono":
                pdf.multi_cell(0, 8, f"Teléfono: {campo('Ingrese el número de teléfono de contacto de la empresa')}")
            elif str(contacto).lower() == "correo electrónico":
                pdf.multi_cell(0, 8, f"Correo: {campo('Indique el correo electrónico de la empresa')}")

        elif tipo_norm == "apoyo logístico":
            pdf.multi_cell(0, 8, f"Empresa para la cual se realiza la actividad: {campo('Seleccione el nombre de la empresa para la cual se realizó la actividad')}")
            pdf.multi_cell(0, 8, f"Detalle de la actividad de apoyo logístico: {campo('Indique de manera detallada la actividad de apoyo logístico brindado')}")
            pdf.multi_cell(0, 8, "Registro fotográfico:")
            insertar_imagen_desde_url(pdf, campo('Adjunte 2 fotografías como registro fotográfico'))
            pdf.multi_cell(0, 8, f"Referencia de documentos generados: {campo('Coloque la referencia a todos los documentos generados.')}")

        elif tipo_norm == "giras":
            provincia = campo("Seleccione la provincia del lugar donde se realizó la gira")
            pdf.multi_cell(0, 8, f"Empresa para la cual se realiza la actividad: {campo('Seleccione el nombre de la empresa para la cual se realizó la actividad')}")
            pdf.multi_cell(0, 8, f"Provincia donde se realizó la gira: {provincia}")
            pdf.multi_cell(0, 8, f"Objetivo de la gira: {campo('Describa el objetivo de la gira o visita y las actividades realizadas en la misma.')}")
            pdf.multi_cell(0, 8, "Registro fotográfico:")
            insertar_imagen_desde_url(pdf, campo('Adjunte 2 fotografías como registro fotográfico'))


        
        elif tipo_norm == "revisión bibliográfica":
            pdf.multi_cell(0, 8, f"Tema: {campo('Indique el tema a investigar a través de la revisión bibliográfica')}")
            pdf.multi_cell(0, 8, f"Aportes: {campo('Indique aspectos relevantes encontrados en el documento, y que representen un aporte sustancioso para el proyecto y el trabajo en el laboratorio.')}")

        elif tipo_norm == "pruebas de laboratorio":
            pdf.multi_cell(0, 8, f"Empresa: {campo('Seleccione el nombre de la empresa para la cual se realizó la actividad')}")
            pdf.multi_cell(0, 8, f"Laboratorio: {campo('Indique el laboratorio donde se realizaron las pruebas')}")

        elif tipo_norm == "sesiones de trabajo con equipo inifar":
            pdf.multi_cell(0, 8, f"Docentes: {campo('Seleccione el o los nombres de los docentes responsables de la reunión')}")
            pdf.multi_cell(0, 8, f"Horario: {campo('Indique el horario en el que realizó la reunión')}")
            pdf.multi_cell(0, 8, f"Modalidad de la reunión: {campo('Seleccione la modalidad de la reunión')}")
            pdf.multi_cell(0, 8, f"Lugar o plataforma: {campo('Indique el lugar o plataforma por la cuál se desarrolló la reunión')}")
            pdf.multi_cell(0, 8, f"Estudiantes participantes: {campo('Indique el nombre  de los estudiantes participantes')}") 
            pdf.multi_cell(0, 8, f"Personas del INIFAR que participan: {campo('Indique los nombres de las personas del INIFAR que participan de la reunión')}")
            pdf.multi_cell(0, 8, f"Descripción de la actividad: {campo('Descripción de la actividad')}")
            pdf.multi_cell(0, 8, "Registro fotográfico:")
            insertar_imagen_desde_url(pdf, campo('Favor incluir 1 fotografías de las actividades realizadas'))


        
        elif tipo_norm == "otras actividades":
            pdf.multi_cell(0, 8, f"Detalle: {campo('Describir, de manera detallada, la actividad realizada para el proyecto.')}")

    return pdf


# === INTERFAZ STREAMLIT ===
# === INTERFAZ STREAMLIT ===
image = Image.open("IMAGEN_SIN_FONDO.png")
st.image(image, width=500)

st.title("Registro de labores INIFAR 🧾")

df = cargar_personas()
df_respuestas = cargar_respuestas()

# Normalizar columnas
df.columns = df.columns.str.strip().str.lower()
df_respuestas.columns = df_respuestas.columns.str.strip()

# Normalizar valores de columnas problemáticas (quita espacios raros)
df_respuestas["actividad_norm"] = (
    df_respuestas["Seleccione el tipo de actividad que realizó"]
    .astype(str)
    .str.strip()
    .str.lower()
    .str.replace("\u00a0", " ", regex=False)
)

df_respuestas["proyecto_norm"] = (
    df_respuestas["Indique el proyecto o unidad para el cuál realizó la tarea."]
    .astype(str)
    .str.strip()
    .str.lower()
    .str.replace("\u00a0", " ", regex=False)
)

# Inicializar estado de sesión
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if "nombre_sel" not in st.session_state:
    st.session_state.nombre_sel = None

# Selección de nombre

opciones_nombres = sorted(df["nombre"].dropna().unique())

nombre_sel = st.selectbox("Selecciona un asistente:", opciones_nombres)

# Input de contraseña
password_input = st.text_input("Ingrese su contraseña:", type="password")

# Botón para validar contraseña
if st.button("Validar contraseña"):
    fila_persona = df[df["nombre"] == nombre_sel]

    if not fila_persona.empty:
        contraseña_real = str(fila_persona.iloc[0]["contraseña"]).strip()
        if password_input.strip() == contraseña_real:
            st.success("✅ Contraseña correcta. Ahora puede seleccionar la actividad.")
            st.session_state.autenticado = True
            st.session_state.nombre_sel = nombre_sel
        else:
            st.error("❌ Contraseña incorrecta.")
            st.session_state.autenticado = False
    else:
        st.error("❌ No se encontró el asistente.")

# SOLO SI ESTÁ AUTENTICADO SE MUESTRA EL RESTO
if st.session_state.autenticado and st.session_state.nombre_sel == nombre_sel:

    opciones_actividades = sorted(df["tipo de actividad"].dropna().unique())
    actividad_sel = st.selectbox("Selecciona una actividad:", opciones_actividades)

    if st.button("Generar PDF"):
        
        nombre_norm = nombre_sel.strip().lower()
        actividad_norm_sel = actividad_sel.strip().lower()

        # Si se selecciona un PROYECTO → hacer compilado
        # Si el nombre seleccionado coincide con algún proyecto en las respuestas → es compilado
        if nombre_norm in df_respuestas["proyecto_norm"].unique():
            registros = df_respuestas[
                (df_respuestas["proyecto_norm"] == nombre_norm) &
                (df_respuestas["actividad_norm"] == actividad_norm_sel)
            ].copy()

            registros = registros.sort_values(by=["Nombre del asistente"])

            titulo_pdf = f"Compilado {nombre_sel} - {actividad_sel}"
            nombre_archivo = f"compilado_{nombre_sel}_{actividad_sel}.pdf"

            # Si se selecciona un asistente → reporte individual
        else:

            registros = df_respuestas[
                (df_respuestas["Nombre del asistente"] == nombre_sel) &
                (df_respuestas["actividad_norm"] == actividad_norm_sel)
            ].copy()

            titulo_pdf = f"Registro de {actividad_sel.title()}"
            nombre_archivo = f"reporte_{nombre_sel.replace(' ', '_')}.pdf"
            
        st.write("Cantidad de registros en compilado:", len(registros))
        st.dataframe(registros[[
            "Nombre del asistente",
            "Seleccione el tipo de actividad que realizó",
            "Indique el proyecto o unidad para el cuál realizó la tarea."
    ]])

        if registros.empty:
            st.warning("⚠️ Este estudiante o proyecto no tiene respuestas asociadas a esta actividad aún.")
        else:
            pdf = generar_pdf_respuesta(registros, titulo_pdf, actividad_sel)
            pdf_bytes = pdf.output(dest='S').encode('latin1')
            buffer = io.BytesIO(pdf_bytes)

            st.download_button(
                label="📥 Descargar PDF",
                data=buffer,
                file_name=nombre_archivo,
                mime="application/pdf"
            )

        
