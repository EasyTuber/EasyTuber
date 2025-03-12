import sys
import os
from modules.utils import get_executable_dir

# Adiciona o caminho da pasta 'libs' ao sys.path
app_dir = get_executable_dir()
libs_path = os.path.join(app_dir, "libs", "ctk_components")
sys.path.append(libs_path)

from ctk_components import CTkAlert, CTkNotification, CTkProgressPopup
