import os
import json
import shutil
import sys
from PIL import Image
import base64
from io import BytesIO


# Converte Base64 para imagem
def b64_to_image(b64_string):
    img_data = base64.b64decode(b64_string)
    return Image.open(BytesIO(img_data))


def get_executable_dir():
    """Retorna o diretório onde o executável está"""
    if getattr(sys, "frozen", False):
        # Se estamos em um executável PyInstaller
        return os.path.dirname(sys.executable)
    else:
        # Se estamos em modo de desenvolvimento
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def resource_path(relative_path):
    """Obtém o caminho para arquivos empacotados"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def get_config_path(filename):
    """Retorna caminho para um arquivo de configuração, copiando-o se necessário"""
    app_dir = get_executable_dir()
    config_dir = os.path.join(app_dir, "resources", "config")

    # Cria o diretório de configuração se não existir
    os.makedirs(config_dir, exist_ok=True)

    config_path = os.path.join(config_dir, filename)

    # Se o arquivo não existir no diretório de configuração, copia do recurso empacotado
    if not os.path.exists(config_path):
        try:
            source_path = resource_path(os.path.join("resources", "config", filename))
            if os.path.exists(source_path):
                shutil.copy2(source_path, config_path)
            else:
                # Cria um arquivo JSON vazio caso o arquivo de origem não exista
                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump({}, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao criar o arquivo de configuração: {e}")

    return config_path


def get_image_path(filename):
    """Retorna caminho para um arquivo de imagem"""
    return resource_path(os.path.join("resources", "images", filename))


# Funções de utilidade para trabalhar com arquivos JSON
def read_config(filename):
    with open(get_config_path(filename), "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(filename, dados):
    with open(get_config_path(filename), "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)
