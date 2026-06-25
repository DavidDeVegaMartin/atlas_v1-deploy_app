import streamlit as st
import requests

# URL de la página 1 privada
URL_RAW_PRIVADA = "https://raw.githubusercontent.com/DavidDeVegaMartin/atlas_v1-framework/main/pages/1_%F0%9F%93%8A_Portfolio_Overview.py"

token_github = st.secrets["github"]["token"]
headers = {"Authorization": f"token {token_github}"}

respuesta = requests.get(URL_RAW_PRIVADA, headers=headers)

if respuesta.status_code == 200:
    exec(respuesta.text, globals())
else:
    st.error(f"Error cargando la página privada. Código: {respuesta.status_code}")
