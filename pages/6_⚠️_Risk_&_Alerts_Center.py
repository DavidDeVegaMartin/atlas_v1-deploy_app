import streamlit as st
import requests

# Apuntamos al archivo correspondiente de la carpeta pages de tu repo PRIVADO
URL_RAW_PRIVADA = "https://raw.githubusercontent.com/DavidDeVegaMartin/atlas_v1-framework/refs/heads/main/pages/6_%E2%9A%A0%EF%B8%8F_Risk_%26_Alerts_Center.py"

token_github = st.secrets["github"]["token"]
headers = {"Authorization": f"token {token_github}"}
respuesta = requests.get(URL_RAW_PRIVADA, headers=headers)

if respuesta.status_code == 200:
    exec(respuesta.text)
else:
    st.error(f"Error cargando la página privada. Código: {respuesta.status_code}")