#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Aplicativo: EasyTuber
Descrição: Faça download de vídeos e áudios do Youtube
Autor: Gabriel Frais
Versão: 2.0.0-beta
"""

import sys
from interface import MainApplication
import customtkinter as ctk


def main():
    """Função principal que inicializa o aplicativo"""
    app = MainApplication()
    ctk.set_appearance_mode(app.user_prefer.get("theme"))
    app.run()


if __name__ == "__main__":
    main()
