# Atlas Puente
# Este archivo ejecuta el repositorio privado en GitHub que contiene Atlas_v1-Strategic Pricing Intelligence

import streamlit as st
import requests
import sys
import types

# --- NUEVO: DESCARGA DINÁMICA DE UTILS ---
# 1. URL RAW de tu archivo utils.py en el repositorio privado
URL_UTILS_PRIVADA = "https://raw.githubusercontent.com/DavidDeVegaMartin/atlas_v1-framework/main/utils.py"

token_github = st.secrets["github"]["token"]
headers = {"Authorization": f"token {token_github}"}

# Descargamos utils.py privado e inyectamos el módulo en Python
if "utils" not in sys.modules:
    resp_utils = requests.get(URL_UTILS_PRIVADA, headers=headers)
    if resp_utils.status_code == 200:
        mod_utils = types.ModuleType("utils")
        exec(resp_utils.text, mod_utils.__dict__)
        sys.modules["utils"] = mod_utils
    else:
        st.error(f"Error crítico: No se pudo mapear el archivo de utilidades. Código: {resp_utils.status_code}")
# ----------------------------------------

# 2. URL de tu archivo ATLAS.py privado principal
URL_RAW_PRIVADA = "https://raw.githubusercontent.com/DavidDeVegaMartin/atlas_v1-framework/main/ATLAS.py"

respuesta = requests.get(URL_RAW_PRIVADA, headers=headers)

if respuesta.status_code == 200:
    exec(respuesta.text)
else:
    st.error(f"Error de conexión segura con el repositorio privado. Código: {respuesta.status_code}")
