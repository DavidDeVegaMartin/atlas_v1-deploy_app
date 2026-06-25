import streamlit as st
import requests
import os

# 1. Comprobación chivata (para ver qué ruta real está detectando el contenedor)
ruta_archivo = os.path.abspath("data/forecast_master.parquet")
if not os.path.exists(ruta_archivo):
    st.warning(f"Ojo: Desde esta página, la ruta relativa 'data/...' no se encuentra. Buscando en: {ruta_archivo}")
    # Si el archivo está en la raíz, listamos qué ve Python para ayudarte a debuguear:
    st.write("Directorios visibles:", os.listdir("."))

# 2. Tu código de carga normal
URL_RAW_PRIVADA = "https://raw.githubusercontent.com/DavidDeVegaMartin/atlas_v1-framework/main/pages/1_%F0%9F%93%8A_Portfolio_Overview.py"
token_github = st.secrets["github"]["token"]
headers = {"Authorization": f"token {token_github}"}

respuesta = requests.get(URL_RAW_PRIVADA, headers=headers)

if respuesta.status_code == 200:
    # Inyectamos __file__ explícitamente en el contexto global de la página por si acaso
    contexto = globals().copy()
    contexto["__file__"] = __file__
    exec(respuesta.text, contexto)
else:
    st.error(f"Error cargando la página privada. Código: {respuesta.status_code}")
