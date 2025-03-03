import os
from utils import read_config, save_config


class DefaultConfig:
    def __init__(self):

        # Informações do aplicativo
        self.APP_NAME = "EasyTuber"
        self.APP_VERSION = "0.1.0-alpha"
        self.APP_AUTHOR = "Gabriel Frais"
        self.APP_DESCRIPTION = "Faça download de vídeos e áudios do Youtube"

        # Configurações de aparência
        self.DEFAULT_THEME = "dark"  # ou "light", "system"
        # TODO mudar dps
        self.DEFAULT_COLOR = "red"  # cor primária para elementos da interface

        # Configurações de tamanho da janela
        self.DEFAULT_WINDOW_WIDTH = 700
        self.DEFAULT_WINDOW_HEIGHT = 500
        self.MIN_WINDOW_WIDTH = 700
        self.MIN_WINDOW_HEIGHT = 500

        # Configurações de idioma
        self.DEFAULT_LANGUAGE = "pt_BR"
        self.AVAILABLE_LANGUAGES = {
            "pt_BR": "Português (Brasil)",
            "en_US": "English (US)",
        }


class UserPreferences:
    def __init__(self):

        # Configurações padrão
        self.default_config = {
            "download_path": os.path.expanduser("~/Downloads").replace("\\", "/"),
            "ffmpeg_path": "",
            "language": "pt_BR",
            "midia": "Vídeo",
            "format": "mp4",
            "quality": "1080p",
            "theme": "Dark",
        }

        # Carrega ou cria as configurações
        self.config = self.load_preferences()

    def load_preferences(self):
        """Carrega as configurações do arquivo"""
        try:
            preferences = read_config("user_preferences.json")
            if not preferences:
                return self.default_config.copy()
            else:
                return preferences
        except Exception as e:
            print(f"Erro ao carregar configurações: {e}")
            return self.default_config.copy()

    def save_preferences(self):
        """Salva as configurações no arquivo"""
        try:
            save_config("user_preferences.json", self.config)
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")

    def get(self, key):
        """Obtém um valor da configuração"""
        return self.config.get(key, self.default_config.get(key))

    def set(self, key, value):
        """Define um valor na configuração"""
        self.config[key] = value
