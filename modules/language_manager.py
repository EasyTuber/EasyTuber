import os
import json
from .config import UserPreferences
from .utils import resource_path


class TranslationManager:
    def __init__(self, app):

        self.user_prefer = app.user_prefer
        self.languages = {}
        self.load_languages()
        self.available_languages = {v["id"]: v["name"] for v in self.languages.values()}

        try:
            self.current_language = self.user_prefer.get("language")
        except Exception as e:
            self.current_language = "pt_BR"  # Idioma padrão

    def load_languages(self):
        # Diretório onde estão os arquivos de tradução
        language_dir = resource_path(os.path.join("resources", "languages"))

        # Carregar cada arquivo de idioma disponível
        for filename in os.listdir(language_dir):
            if filename.endswith(".json"):
                language_code = filename.split(".")[0]  # Ex: "en_US.json" -> "en_US"
                with open(
                    os.path.join(language_dir, filename), "r", encoding="utf-8"
                ) as file:
                    self.languages[language_code] = json.load(file)

    def get_text(self, key):
        """Retorna o texto traduzido com base na chave e no idioma atual"""
        if key in self.languages.get(self.current_language, {}):
            return self.languages[self.current_language][key]
        # Fallback para o idioma padrão
        elif key in self.languages.get("pt_BR", {}):
            return self.languages["pt_BR"][key]
        # Retorna a chave se não encontrar tradução
        return key

    # Retorna em todos os idiomas
    def get_translates(self, key):
        return [
            lang_dict[key] for lang_dict in self.languages.values() if key in lang_dict
        ]

    def change_language(self, language_code):
        """Altera o idioma atual"""
        if language_code in self.languages:
            self.current_language = language_code
            return True
        return False
