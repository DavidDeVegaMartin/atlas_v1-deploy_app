import streamlit as st
import requests
import sys
import types

# 1. Forzar la carga virtual de 'utils' para que esta página la reconozca al hacer exec()
URL_UTILS_PRIVADA = "https://raw.githubusercontent.com/DavidDeVegaMartin/atlas_v1-framework/main/utils.py"

token_github = st.secrets["github"]["token"]
headers = {"Authorization": f"token {token_github}"}

if "utils" not in sys.modules:
    resp_utils = requests.get(URL_UTILS_PRIVADA, headers=headers)
    if resp_utils.status_code == 200:
        mod_utils = types.ModuleType("utils")
        exec(resp_utils.text, mod_utils.__dict__)
        sys.modules["utils"] = mod_utils

# 2. Ahora sí, cargamos y ejecutamos de forma segura la página 1 privada
URL_RAW_PRIVADA = "https://raw.githubusercontent.com/DavidDeVegaMartin/atlas_v1-framework/refs/heads/main/pages/3_%F0%9F%93%85_Commercial_Planning.py"

respuesta = requests.get(URL_RAW_PRIVADA, headers=headers)

if respuesta.status_code == 200:
    exec(respuesta.text)
else:
    st.error(f"Error cargando la página privada. Código: {respuesta.status_code}")
