import os
import json
from modules import UserPreferences, resource_path


class TranslationManager:
    def __init__(self):
        self.languages = {}
        self.user_prefer = UserPreferences()
        try:
            self.current_language = self.user_prefer.get("language")
        except Exception as e:
            self.current_language = "pt_BR"  # Idioma padrão
            print(f"Deu um erro: {str(e)}")
        self.load_languages()

    def get_language_path(filename):
        """Retorna caminho para um arquivo de idioma"""
        return resource_path(os.path.join("Data", "languages", filename))

    def load_languages(self):
        # Diretório onde estão os arquivos de tradução
        language_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "Data", "languages"
        )

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

    def change_language(self, language_code):
        """Altera o idioma atual"""
        if language_code in self.languages:
            self.current_language = language_code
            return True
        return False
