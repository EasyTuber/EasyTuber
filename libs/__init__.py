"""
import sys
import os


# Adiciona o caminho da pasta 'libs' ao sys.path
def get_executable_dir():
    ""Retorna o diretório onde o executável está""
    if getattr(sys, "frozen", False):
        # Se estamos em um executável PyInstaller
        return os.path.dirname(sys.executable)
    else:
        # Se estamos em modo de desenvolvimento
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


app_dir = get_executable_dir()
libs_path = os.path.join(app_dir, "libs", "ctk_components")
sys.path.append(libs_path)

from ctk_components import CTkAlert, CTkNotification, CTkProgressPopup
"""

from .ctk_components.ctk_components import CTkAlert, CTkNotification, CTkProgressPopup
