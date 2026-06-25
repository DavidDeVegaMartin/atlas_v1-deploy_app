import sys
import types
import requests
import streamlit as st

class GitHubModuleFinder:
    """Intercepta las importaciones de 'utils.X' y las descarga dinámicamente de GitHub."""
    def __init__(self):
        self.base_url = "https://raw.githubusercontent.com/DavidDeVegaMartin/atlas_v1-framework/main/utils"
        self.token = st.secrets["github"]["token"]
        self.headers = {"Authorization": f"token {self.token}"}

    def find_spec(self, fullname, path, target=None):
        # Si alguien intenta importar algo que empiece por 'utils.', entramos en acción
        if fullname.startswith("utils."):
            from importlib.machinery import ModuleSpec
            return ModuleSpec(fullname, self)
        return None

    def create_module(self, spec):
        # Retorna None para que Python cree el objeto de módulo estándar
        return None

    def exec_module(self, module):
        # Obtenemos el nombre del archivo (ej: 'utils.data_loader' -> 'data_loader.py')
        submodule_name = module.__name__.split(".")[-1]
        url = f"{self.base_url}/{submodule_name}.py"
        
        # Descargamos el código desde el repositorio privado
        respuesta = requests.get(url, headers=self.headers)
        
        if respuesta.status_code == 200:
            # Ejecutamos el código privado dentro del contexto del nuevo módulo
            exec(respuesta.text, module.__dict__)
        else:
            raise ModuleNotFoundError(
                f"No se pudo descargar el submódulo privado '{submodule_name}' desde GitHub (Código: {respuesta.status_code})."
            )

# Registramos este buscador dinámico en el sistema de importaciones de Python
if not any(isinstance(x, GitHubModuleFinder) for x in sys.meta_path):
    sys.meta_path.insert(0, GitHubModuleFinder())
