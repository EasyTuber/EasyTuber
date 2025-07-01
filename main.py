#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Aplicativo: EasyTuber
Descrição: Faça download de vídeos e áudios do Youtube
Autor: Gabriel Frais
Versão: 3.0.0
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
    ctk.set_appearance_mode(app.user_prefer.get("appearance"))
    app.run()


if __name__ == "__main__":
    main()
