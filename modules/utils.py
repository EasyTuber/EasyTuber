import os
import json
import shutil
import sys
import re
import subprocess
from PIL import Image
import base64
from io import BytesIO


# Converte Base64 para imagem
def b64_to_image(b64_string):
    img_data = base64.b64decode(b64_string)
    return Image.open(BytesIO(img_data))


# Retorna pasta atual do programa
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


def get_image_path(filename):
    """Retorna caminho para um arquivo de imagem"""
    return resource_path(os.path.join("resources", "images", filename))


def get_theme_path(filename):
    """Retorna caminho para o arquivo do tema"""
    return resource_path(os.path.join("resources", "theme", filename))


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


def read_config(filename):
    with open(get_config_path(filename), "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(filename, dados):
    with open(get_config_path(filename), "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)


def get_ffmpeg_path():
    """
    Encontra o caminho real para o executável do FFmpeg, ignorando shims do Chocolatey.
    Retorna o caminho do executável real ou None se não encontrado.
    """
    # Primeiro verifica se o ffmpeg está no PATH
    ffmpeg_path = shutil.which("ffmpeg")

    if ffmpeg_path:
        # Verifica se é um shim do Chocolatey
        if "chocolatey" in ffmpeg_path.lower():
            # Tenta encontrar o caminho real executando o comando ffmpeg -version
            try:
                result = subprocess.run(
                    ["ffmpeg", "-version"], capture_output=True, text=True
                )
                # Procura por um caminho de arquivo no output
                match = re.search(r"(([A-Z]:\\|/)[^\s]+ffmpeg(\.exe)?)", result.stdout)
                if match:
                    real_path = match.group(1)
                    if os.path.exists(real_path):
                        return real_path
            except Exception:
                pass

            # Se não conseguiu encontrar pelo output, tenta locais comuns do Chocolatey
            choco_paths = [
                os.path.join(
                    os.environ.get("ChocolateyInstall", ""),
                    "lib",
                    "ffmpeg",
                    "tools",
                    "ffmpeg",
                    "bin",
                    "ffmpeg.exe",
                ),
                os.path.join(
                    os.environ.get("ProgramData", ""),
                    "chocolatey",
                    "lib",
                    "ffmpeg",
                    "tools",
                    "ffmpeg",
                    "bin",
                    "ffmpeg.exe",
                ),
                os.path.join(
                    "C:",
                    "ProgramData",
                    "chocolatey",
                    "lib",
                    "ffmpeg",
                    "tools",
                    "ffmpeg",
                    "bin",
                    "ffmpeg.exe",
                ),
            ]

            for path in choco_paths:
                if os.path.exists(path):
                    return path
        else:
            # Se não é do Chocolatey, provavelmente é o executável real
            return ffmpeg_path

    # Se não encontrou pelo PATH, procura em locais comuns
    common_locations = [
        # Windows
        os.path.join(os.getenv("LOCALAPPDATA", ""), "FFmpeg", "ffmpeg.exe"),
        os.path.join(os.getenv("PROGRAMFILES", ""), "FFmpeg", "bin", "ffmpeg.exe"),
        os.path.join(os.getenv("PROGRAMFILES(X86)", ""), "FFmpeg", "bin", "ffmpeg.exe"),
        # Linux
        "/usr/bin/ffmpeg",
        "/usr/local/bin/ffmpeg",
        # macOS
        "/usr/local/bin/ffmpeg",
        "/opt/homebrew/bin/ffmpeg",
    ]

    for location in common_locations:
        if os.path.isfile(location):
            return location

    # Se ainda não encontrou, tenta encontrar pela saída do comando 'where' (Windows)
    try:
        if os.name == "nt":  # Windows
            result = subprocess.run(["where", "ffmpeg"], capture_output=True, text=True)
            paths = result.stdout.strip().split("\n")
            for path in paths:
                path = path.strip()
                if os.path.exists(path) and "chocolatey" not in path.lower():
                    return path
    except Exception:
        pass

    # Se não encontrou em nenhum lugar
    return None
