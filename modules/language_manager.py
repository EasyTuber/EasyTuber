import os
import json
from .config import UserPreferences
from .utils import resource_path


class TranslationManager:
    def __init__(self, app):
        """
        Initializes the translation manager.

        Args:
            app: The application instance containing the user's preferences.
        """
        try:
            self.user_prefer = app.user_prefer
        except Exception as e:
            pass

        self.languages = {}
        self.load_languages()
        self.available_languages = {v["id"]: v["name"] for v in self.languages.values()}

        try:
            self.current_language = self.user_prefer.get("language")
        except Exception as e:
            self.current_language = "pt_BR"  # Default language in case of an error

    def load_languages(self):
        """
        Loads the available language files from the resources directory.

        Each JSON file must contain translations in the appropriate format to be loaded.
        """
        language_dir = resource_path(os.path.join("resources", "languages"))

        # Check if the language directory exists
        if not os.path.exists(language_dir):
            raise FileNotFoundError(f"Language directory not found: {language_dir}")

        # Load each available language file
        for filename in os.listdir(language_dir):
            if filename.endswith(".json"):
                language_code = filename.split(".")[
                    0
                ]  # Example: "en_US.json" -> "en_US"
                try:
                    with open(
                        os.path.join(language_dir, filename), "r", encoding="utf-8"
                    ) as file:
                        self.languages[language_code] = json.load(file)
                except Exception as e:
                    print(f"Error loading translation file {filename}: {e}")

    def get_text(self, key: str, language: str = None) -> str:
        """
        Returns the translated text based on the key and the current language.

        Args:
            key (str): The translation key to look up.

        Returns:
            str: The translated text or the key if not found.
        """
        if language is None:
            language = self.current_language
        if key in self.languages.get(language, {}):
            return self.languages[language][key]
        # Fallback to the default language
        elif key in self.languages.get("pt_BR", {}):
            return self.languages["pt_BR"][key]
        # Return the key if no translation is found
        return key

    # Retorna em todos os idiomas
    def get_translates(self, key: str) -> list:
        """
        Returns the translations for a key in all available languages.

        Args:
            key (str): The translation key to look up in all languages.

        Returns:
            list: A list of translations for the key in all languages.
        """
        return [
            lang_dict[key] for lang_dict in self.languages.values() if key in lang_dict
        ]

    def get_all_translation_keys_list(self, category_key: str) -> list:
        """
        Returns a list of lists with all the keys corresponding in each language for a specific category.

        Args:
            category_key (str): The key of the category whose translations will be collected.

        Returns:
            list: A list of lists with the translation keys by category in each language.
        """
        # Create a temporary dictionary to map universal values to their names in different languages
        translation_map = {}

        for lang, translations in self.languages.items():
            for key, value in translations[category_key].items():
                if value not in translation_map:
                    translation_map[value] = {}
                translation_map[value][lang] = key

        # Convert to a list of lists with only the translation keys
        return [list(values.values()) for values in translation_map.values()]

    def get_key_by_value(self, dictionary: dict, target_value: str) -> str | None:
        """
        Retorna a chave correspondente a um valor específico no dicionário.

        Args:
            dictionary (dict): O dicionário a ser pesquisado.
            target_value (str): O valor a ser procurado no dicionário.

        Returns:
            str | None: A chave correspondente ao valor, ou None se não encontrado.
        """
        for key, value in dictionary.items():
            if value == target_value:
                return key
        return None

    def change_language(self, language_code: str) -> bool:
        """
        Changes the current language.

        Args:
            language_code (str): The language code to switch to (e.g., "en_US").

        Returns:
            bool: Returns True if the language change was successful, False otherwise.
        """
        if language_code in self.languages:
            self.current_language = language_code
            return True
        return False
