import os
from .utils import read_config, save_config, get_ffmpeg_path


class DefaultConfig:
    def __init__(self):

        # Informações do aplicativo
        self.APP_NAME = "EasyTuber"
        self.APP_VERSION = "2.0.1"
        self.APP_AUTHOR = "Gabriel Frais"
        self.APP_DESCRIPTION = "Faça download de vídeos e áudios do Youtube"
        self.APP_LICENSE = "GPLv3"
        self.APP_WEBSITE = "https://github.com/EasyTuber/EasyTuber"

        # Configurações de tamanho da janela
        self.DEFAULT_WINDOW_WIDTH = 700
        self.DEFAULT_WINDOW_HEIGHT = 500
        self.MIN_WINDOW_WIDTH = 700
        self.MIN_WINDOW_HEIGHT = 500

        # Configurações de Valores
        self.FORMAT_VIDEOS = ["mp4", "mkv", "webm"]  # TODO adicionar mais formatos
        self.FORMAT_AUDIOS = ["mp3", "m4a", "aac"]  # TODO adicionar mais formatos


class UserPreferences:
    """
    A class to manage user preferences, including loading, saving, and retrieving
    configuration settings such as language, download path, media format, and quality.

    This class uses a default configuration and attempts to load preferences from
    a file. If the file doesn't exist or an error occurs, it falls back to the default configuration.
    """

    def __init__(self):
        """
        Initializes the UserPreferences instance, setting up default configuration values
        and attempting to load existing preferences from a configuration file.

        If a valid FFmpeg path is found, it is added to the configuration.
        """
        # Default configuration values
        self.default_config = {
            "default_download_path": os.path.expanduser("~/Downloads").replace(
                "\\", "/"
            ),
            "language": "pt_BR",  # Default language (Portuguese)
            "media": "Vídeo",  # Default media type
            "format": "mp4",  # Default media format
            "quality": "1080p",  # Default quality
            "appearance": "Sistema",  # Default appearance setting
            "sound_notification": True,  # Default sound notification
            "open_folder": False,  # Default open folder after download
            "clear_url": False,  # Default clear url after download
            "notify_completed": True,  # Default notify completed
        }

        # Attempt to get the FFmpeg executable path and add it to the config if available
        ffmpeg_path = get_ffmpeg_path()
        if ffmpeg_path:
            self.default_config["ffmpeg_path"] = ffmpeg_path.replace("\\", "/")

        # Load preferences or create them if they don't exist
        self.config = self.load_preferences()

    def load_preferences(self) -> dict:
        """
        Loads user preferences from the 'user_preferences.json' file.

        If the file is not found or an error occurs during loading, the default configuration
        is returned instead.

        Returns:
            dict: A dictionary containing user preferences.
        """
        try:
            preferences = read_config("user_preferences.json")
            if not preferences:
                return (
                    self.default_config.copy()
                )  # Return a copy of the default config if no preferences are found
            return preferences
        except Exception as e:
            print(f"Error loading preferences: {e}")
            return self.default_config.copy()

    def save_preferences(self):
        """
        Saves the current user preferences to the 'user_preferences.json' file.

        If an error occurs during saving, it will print an error message but not raise an exception.
        """
        try:
            save_config("user_preferences.json", self.config)
        except Exception as e:
            print(f"Error saving preferences: {e}")

    def get(self, key: str):
        """
        Retrieves the value of a given configuration key.

        If the key doesn't exist in the current preferences, the method will return the
        corresponding value from the default configuration.

        Args:
            key (str): The configuration key whose value is to be retrieved.

        Returns:
            The value of the configuration key.
        """
        return self.config.get(key, self.default_config.get(key))

    def set(self, key: str, value):
        """
        Sets the value for a given configuration key.

        Args:
            key (str): The configuration key to set the value for.
            value: The value to be assigned to the key.
        """
        self.config[key] = value
