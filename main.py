#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Aplicativo: EasyTuber
Descrição: Faça download de vídeos e áudios do Youtube
Autor: Gabriel Frais
Versão: 2.2.0
"""

from interface import MainApplication
import customtkinter as ctk
from modules import get_theme_path


def main():
    """Função principal que inicializa o aplicativo"""
    ctk.set_default_color_theme(get_theme_path("red.json"))

    # Fechar o splash screen antes de inicializar a aplicação principal
    try:
        import pyi_splash  # type: ignore

        pyi_splash.close()
    except ImportError:
        pass

    app = MainApplication()
    appearance_key = app.translator.get_key_by_value(
        app.translator.get_text("appearance_values"),
        app.user_prefer.get("appearance"),
    )
    ctk.set_appearance_mode(appearance_key)
    app.run()


if __name__ == "__main__":
    main()
