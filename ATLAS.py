# Atlas Puente

# Este archivo ejecuta el repositorio privado en GitHub que contiene Atlas_v1-Strategic Pricing Intelligence

import streamlit as st
import requests

# 1. URL real en crudo (RAW) de tu repositorio privado
# Fíjate que cambia "github.com" por "raw.githubusercontent.com" y desaparece el "/blob/"
URL_RAW_PRIVADA = "https://raw.githubusercontent.com/DavidDeVegaMartin/atlas_v1-framework/main/ATLAS.py"

# 2. Leemos de forma segura el token que vas a meter en los Secrets de Streamlit
token_github = st.secrets["github"]["token"]

# 3. Descargamos el código real usando el token para saltarnos el muro privado
headers = {"Authorization": f"token {token_github}"}
respuesta = requests.get(URL_RAW_PRIVADA, headers=headers)

if respuesta.status_code == 200:
    # Ejecutamos el contenido del ATLAS privado de forma invisible
    exec(respuesta.text)
else:
    st.error(f"Error de conexión segura con el repositorio privado. Código: {respuesta.status_code}")
