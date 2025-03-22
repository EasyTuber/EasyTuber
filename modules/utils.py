import os
import json
import shutil
import sys
import re
import subprocess
import threading
import winsound
from PIL import Image
from io import BytesIO
from typing import Literal


def center_window(root, width: int, height: int) -> None:
    """Centers the window on the screen.

    Args:
        root (ctk.CTk or ctk.Toplevel): The main application window or frame.
        width (int): The desired width of the window.
        height (int): The desired height of the window.
    """
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = int((screen_width / 2) - (width / 2))
    window_height = int((screen_height / 2) - (height / 2))
    root.geometry(f"{width}x{height}+{window_width}+{window_height}")


def play_sound(success: bool) -> None:
    """Plays a notification sound.

    Args:
        success (bool): If True, plays the 'SystemAsterisk' sound.
                        If False, plays the 'SystemHand' sound.
    """
    sound = "SystemAsterisk" if success else "SystemHand"

    def play_in_thread():
        try:
            winsound.PlaySound(sound, winsound.SND_ALIAS)
        except RuntimeError as e:
            print(f"Sound playback error: {e}")

    # Iniciar a reprodução em uma thread separada
    sound_thread = threading.Thread(target=play_in_thread)
    sound_thread.daemon = True  # Isso garante que a thread será encerrada quando o programa principal terminar
    sound_thread.start()


def get_executable_dir() -> str:
    """Returns the directory where the executable is located.

    In case the application is packaged with PyInstaller, it returns the directory of the executable.
    Otherwise, it returns the directory of the script in development mode.
    """
    if getattr(sys, "frozen", False):
        # If running as a PyInstaller executable
        return os.path.dirname(sys.executable)
    else:
        # If running in development mode
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def resource_path(relative_path: str) -> str:
    """Gets the path to resources in a packaged application.

    If the application is bundled with PyInstaller, it returns the path to the resource inside the bundle.
    Otherwise, it returns the path relative to the script's location in development mode.

    Args:
        relative_path (str): The relative path to the resource.

    Returns:
        str: The full path to the resource.
    """

    try:
        base_path = sys._MEIPASS  # Path for PyInstaller bundle
    except Exception:
        base_path = get_executable_dir()  # Path in development mode

    return os.path.join(base_path, relative_path)


def get_image_path(filename: str) -> str:
    """Returns the path to an image file.

    The image file is expected to be located in the 'resources/images' directory.

    Args:
        filename (str): The name of the image file.

    Returns:
        str: The full path to the image file.
    """
    return resource_path(os.path.join("resources", "images", filename))


def get_theme_path(filename: str) -> str:
    """Returns the path to a theme file.

    The theme file is expected to be located in the 'resources/theme' directory.

    Args:
        filename (str): The name of the theme file.

    Returns:
        str: The full path to the theme file.
    """
    return resource_path(os.path.join("resources", "theme", filename))


def get_config_path(filename: str) -> str:
    """Returns the path to a configuration file, creating it if necessary.

    If the configuration file does not exist in the expected directory,
    it will be copied from the bundled resource or a new empty JSON file will be created.

    Args:
        filename (str): The name of the configuration file.

    Returns:
        str: The full path to the configuration file.
    """
    app_dir = get_executable_dir()
    config_dir = os.path.join(app_dir, "resources", "config")

    # Create the configuration directory if it does not exist
    os.makedirs(config_dir, exist_ok=True)

    config_path = os.path.join(config_dir, filename)

    # If the configuration file doesn't exist, copy from the resource or create it
    if not os.path.exists(config_path):
        try:
            source_path = resource_path(os.path.join("resources", "config", filename))
            if os.path.exists(source_path):
                shutil.copy2(source_path, config_path)
            else:
                # Create an empty JSON file if the source doesn't exist
                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump({}, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error creating the configuration file: {e}")

    return config_path


def read_config(filename: str) -> dict:
    """Reads a configuration file and returns its content.

    This function reads the specified configuration file (in JSON format)
    from the application's config directory.

    Args:
        filename (str): The name of the configuration file to read.

    Returns:
        dict: The content of the configuration file as a dictionary.

    Raises:
        FileNotFoundError: If the configuration file does not exist.
        json.JSONDecodeError: If the file content is not valid JSON.
    """
    try:
        with open(get_config_path(filename), "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError as e:
        print(f"Error: Configuration file '{filename}' not found.")
        raise e
    except json.JSONDecodeError as e:
        print(f"Error: Failed to decode JSON from '{filename}'.")
        raise e


def save_config(filename: str, dados: dict) -> None:
    """Saves data to a configuration file in JSON format.

    This function writes the provided data (in JSON format) to the specified
    configuration file in the application's config directory.

    Args:
        filename (str): The name of the configuration file to save the data.
        dados (dict): The data to be saved in the configuration file.

    Returns:
        None

    Raises:
        IOError: If an error occurs while writing to the file.
    """
    try:
        with open(get_config_path(filename), "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
    except IOError as e:
        print(f"Error: Failed to write to configuration file '{filename}'.")
        raise e


def get_ffmpeg_path() -> str:
    """
    Finds the real path to the FFmpeg executable, avoiding Chocolatey shims.

    This function first checks if FFmpeg is available in the system PATH. If it is,
    it ensures that it isn't a Chocolatey shim by running the 'ffmpeg -version' command
    to extract the real path. If the executable is not found via the PATH, the function
    checks common locations for FFmpeg on different operating systems. If the executable
    is not found, it attempts to locate FFmpeg using the 'where' command (Windows only).

    Returns:
        str: The real path to the FFmpeg executable if found, or None if not found.
    """

    # First, check if ffmpeg is in the PATH
    ffmpeg_path = shutil.which("ffmpeg")

    if ffmpeg_path:
        # If it's a Chocolatey shim, try to find the real path
        if "chocolatey" in ffmpeg_path.lower():
            try:
                result = subprocess.run(
                    ["ffmpeg", "-version"], capture_output=True, text=True
                )
                # Look for a file path in the output
                match = re.search(r"(([A-Z]:\\|/)[^\s]+ffmpeg(\.exe)?)", result.stdout)
                if match:
                    real_path = match.group(1)
                    if os.path.exists(real_path):
                        return real_path
            except Exception:
                pass

            # If the output doesn't contain the real path, check common Chocolatey paths
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
            # If it's not a Chocolatey shim, return the path
            return ffmpeg_path

    # If FFmpeg is not found in the PATH, check common locations
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

    # If not found, try to locate using the 'where' command (Windows)
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

    # If the executable is still not found, return None
    return None
