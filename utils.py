import streamlit as st
import requests
import sys
import types

# 1. URL RAW de tu archivo utils.py real en el repositorio privado
URL_UTILS_PRIVADA = "https://raw.githubusercontent.com/DavidDeVegaMartin/atlas_v1-framework/main/utils.py"

token_github = st.secrets["github"]["token"]
headers = {"Authorization": f"token {token_github}"}

# Descargamos el contenido de las utilidades privadas
respuesta = requests.get(URL_UTILS_PRIVADA, headers=headers)

if respuesta.status_code == 200:
    # Ejecutamos el contenido dentro del entorno de este archivo
    exec(respuesta.text, globals())
else:
    st.error(f"Error crítico cargando las funciones de utilidad. Código: {respuesta.status_code}")
