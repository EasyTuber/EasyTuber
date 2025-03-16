import threading
import webbrowser
import customtkinter as ctk

from PIL import Image
from tkinter import filedialog
from CTkMessagebox import CTkMessagebox
from CTkToolTip import *

from libs import CTkProgressPopup, CTkAlert, CTkNotification


from modules import (
    YoutubeDownloader,
    UserPreferences,
    DefaultConfig,
    TranslationManager,
    get_image_path,
    b64_to_image,
    get_theme_path,
)


class CustomTabview(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Criar frame para os botões
        self.button_frame = ctk.CTkFrame(self, corner_radius=10)
        self.button_frame.pack(side="top", fill="x", padx=10)
        self.button_frame.rowconfigure(0, weight=1)

        # Criar frame para o conteúdo
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        # Dicionários para armazenar botões e frames
        self.buttons = {}
        self.tabs = {}
        self.current_tab = None

    def add(self, name, text):
        # Calcular a posição para o novo botão
        button_position = len(self.buttons)

        # Criar botão para a aba
        button = ctk.CTkButton(
            self.button_frame,
            text=text,
            corner_radius=12,
            fg_color="transparent",
            text_color=("gray50", "gray70"),
            hover_color=("gray90", "gray30"),
            height=35,
            border_width=0,
            command=lambda n=name: self.select(n),
        )
        button.grid(row=0, column=button_position, sticky="nsew", padx=5, pady=5)
        self.button_frame.grid_columnconfigure(button_position, weight=1)

        # Criar frame para o conteúdo da aba
        tab_frame = ctk.CTkFrame(
            self.content_frame,
            corner_radius=10,
            fg_color=("gray95", "gray17"),
        )

        # Armazenar referências
        self.buttons[name] = button
        self.tabs[name] = tab_frame

        # Se for a primeira aba, selecione-a
        if not self.current_tab:
            self.select(name)

        return tab_frame

    def select(self, name):
        # Esconder a aba atualmente visível
        if self.current_tab:
            self.tabs[self.current_tab].pack_forget()

            # Restaurar aparência do botão não selecionado
            self.buttons[self.current_tab].configure(
                fg_color="transparent",
                hover_color=("gray90", "gray30"),
                text_color=("gray50", "gray70"),
            )

        # Mostrar a aba selecionada
        self.tabs[name].pack(fill="both", expand=True)

        # Destacar o botão selecionado
        self.buttons[name].configure(
            fg_color=("#D03434", "#A11D1D"),
            hover_color=("#AE2727", "#B81D1D"),
            text_color=("#DCE4EE", "#DCE4EE"),
        )

        # Atualizar a aba atual
        self.current_tab = name

    def update_button_text(self):
        # Verificar se o botão existe
        for index, name in enumerate(self.buttons):
            new_text = self.master.translator.get_text("tabs_names")[index]
            self.buttons[name].configure(text=new_text)


class MainApplication(ctk.CTk):
    def __init__(self):
        super().__init__()

        # region setup
        # Inicializa o gerenciador de configurações
        self.user_prefer = UserPreferences()
        self.translator = TranslationManager(self)
        self.default_config = DefaultConfig()
        self.yt_dlp = YoutubeDownloader(self)

        # Variaveis de tradução
        self.localized_audio = self.translator.get_translates("audio")
        self.localized_video = self.translator.get_translates("video")
        self.localized_appearance = self.translator.get_all_translation_keys_list(
            "appearance_values"
        )

        self.available_languages = self.translator.available_languages
        self.available_languages_inverted = {
            v: k for k, v in self.available_languages.items()
        }

        # Variaveis de url para compartilhar entre elas
        self.url1_var = ctk.StringVar()
        self.url2_var = ctk.StringVar()

        # Registrar os traces iniciais (com escopo global para poder removê-los)
        self.trace_url1 = self.url1_var.trace_add("write", self.sync_var1_to_var2)
        self.trace_url2 = self.url2_var.trace_add("write", self.sync_var2_to_var1)

        self.title(f"{self.default_config.APP_NAME} v{self.default_config.APP_VERSION}")
        self.geometry(
            f"{self.default_config.DEFAULT_WINDOW_WIDTH}x{self.default_config.DEFAULT_WINDOW_HEIGHT}"
        )
        self.minsize(
            self.default_config.MIN_WINDOW_WIDTH, self.default_config.MIN_WINDOW_HEIGHT
        )

        self.after(250, lambda: self.iconbitmap(get_image_path("icon.ico")))

        # Outras variaveis

        # endregion

        # region Logo e título
        #! Logo e título lado a lado
        # Frame para logo e título
        self.title_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.title_frame.pack(side="top", fill="x", pady=10)
        # Centralizar a logo
        self.title_frame.columnconfigure(
            (0, 3), weight=1
        )  # Espaço à esquerda e direita
        self.title_frame.columnconfigure((1, 2), weight=0)  # Logo não expansível

        # Carregar e configurar o ícone do programa
        self.logo = ctk.CTkImage(
            light_image=Image.open(get_image_path("logo.png")),
            dark_image=Image.open(get_image_path("logo.png")),
            size=(50, 50),
        )

        # Logo e título lado a lado
        self.logo_label = ctk.CTkLabel(
            self.title_frame, text="", image=self.logo, compound="left"
        )
        self.logo_label.grid(row=0, column=1, padx=(0, 10))

        self.title_label = ctk.CTkLabel(
            self.title_frame,
            text=self.translator.get_text("app_title"),
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        self.title_label.grid(row=0, column=2)
        # endregion

        # region TabView
        #! Criar o tabview personalizado
        self.tabview = CustomTabview(self, fg_color="transparent")
        self.tabview.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Adicionar abas
        self.tab1 = self.tabview.add(
            "tab1", self.translator.get_text("tabs_names")[0]
        )  # Download
        self.tab2 = self.tabview.add(
            "tab2", self.translator.get_text("tabs_names")[1]
        )  # Advanced
        self.tab3 = self.tabview.add(
            "tab3", self.translator.get_text("tabs_names")[2]
        )  # Settings
        self.tab4 = self.tabview.add(
            "tab4", self.translator.get_text("tabs_names")[3]
        )  # About
        # endregion

        # region Área principal do conteúdo
        #! Área principal do conteúdo
        self.main_frame = ctk.CTkFrame(self.tab1, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, pady=10)

        self.main_frame_top = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.main_frame_top.pack(side="top", fill="both")

        self.main_frame_bottom = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.main_frame_bottom.pack(side="bottom", fill="x")

        # * Frame configuração de download
        self.config_download_frame = ctk.CTkFrame(
            self.main_frame_top, fg_color="transparent"
        )
        self.config_download_frame.pack(side="top", expand=True, fill="x")

        #! Playlist
        self.playlist_frame = ctk.CTkFrame(
            self.config_download_frame, fg_color="transparent"
        )
        self.playlist_frame.pack(side="left", expand=True, padx=5)

        self.playlist_label = ctk.CTkLabel(self.playlist_frame, text="Playlist")
        self.playlist_label.grid(row=0, column=0, pady=(0, 1), sticky="ew")

        self.playlist_imput_frame = ctk.CTkFrame(
            self.playlist_frame, fg_color="transparent"
        )
        self.playlist_imput_frame.grid(row=1, column=0, sticky="ew")

        self.playlist_check_var = ctk.BooleanVar(value=False)
        self.playlist_check = ctk.CTkCheckBox(
            self.playlist_imput_frame,
            text="",
            width=1,
            variable=self.playlist_check_var,
            onvalue=True,
            offvalue=False,
        )
        self.playlist_check.pack(side="left", padx=(0, 2))

        self.playlist_check_tooltip = CTkToolTip(
            self.playlist_check,
            justify="left",
            padding=(10, 10),
            border_width=1,
            x_offset=-50,
            follow=False,
            message=self.translator.get_text("playlist_check_tolltip"),
        )

        self.playlist_entry = ctk.CTkEntry(
            self.playlist_imput_frame,
            width=100,
            corner_radius=10,
            placeholder_text=self.translator.get_text("playlist_placeholder"),
        )
        self.playlist_entry.pack(side="left")

        self.playlist_entry_tooltip = CTkToolTip(
            self.playlist_entry,
            justify="left",
            padding=(10, 10),
            border_width=1,
            x_offset=-70,
            follow=False,
            message=self.translator.get_text("playlist_tolltip"),
        )

        #! Tipo de Mídia
        self.midia_frame = ctk.CTkFrame(
            self.config_download_frame, fg_color="transparent"
        )
        self.midia_frame.pack(side="left", expand=True, padx=5)

        self.midia_label = ctk.CTkLabel(
            self.midia_frame, text=self.translator.get_text("media_type")
        )
        self.midia_label.grid(row=0, column=0, pady=(0, 1), sticky="ew")

        self.midia_var = ctk.StringVar(
            value=self.translator.get_text("media_values")[0]
        )
        self.midia_SegButton = ctk.CTkSegmentedButton(
            self.midia_frame,
            values=self.translator.get_text("media_values"),
            variable=self.midia_var,
            command=self.midia_selected,
        )
        self.midia_SegButton.grid(row=1, column=0, sticky="ew")

        #! Formato do arquivo
        self.formato_frame = ctk.CTkFrame(
            self.config_download_frame, fg_color="transparent"
        )
        self.formato_frame.pack(side="left", expand=True, padx=5)

        self.formato_label = ctk.CTkLabel(
            self.formato_frame, text=self.translator.get_text("format")
        )
        self.formato_label.grid(row=0, column=0, pady=(0, 1), sticky="ew")

        self.formato_var = ctk.StringVar(value="mp4")
        self.formato_OptionMenu = ctk.CTkOptionMenu(
            self.formato_frame,
            dynamic_resizing=False,
            values=["mp4", "mkv", "webm"],
            variable=self.formato_var,
            width=80,
        )
        self.formato_OptionMenu.grid(row=1, column=0, sticky="ew")

        #! Qualidade do Video
        self.qualidade_frame = ctk.CTkFrame(
            self.config_download_frame, fg_color="transparent"
        )
        self.qualidade_frame.pack(side="left", expand=True, padx=5)

        self.qualidade_var = ctk.StringVar(value="1080p")
        self.qualidade_label = ctk.CTkLabel(
            self.qualidade_frame, text=self.translator.get_text("quality")
        )
        self.qualidade_label.grid(row=0, column=0, pady=(0, 1), sticky="ew")

        self.qualidade_menu = ctk.CTkOptionMenu(
            self.qualidade_frame,
            dynamic_resizing=False,
            values=["1080p", "720p", "480p", "360p"],
            variable=self.qualidade_var,
            width=80,
        )
        self.qualidade_menu.grid(row=1, column=0, sticky="ew")

        #! Frame de url
        self.url1_frame = ctk.CTkFrame(self.main_frame_top, fg_color="transparent")
        self.url1_frame.pack(
            side="top", fill="x", expand=True, ipadx=5, ipady=5, pady=(40, 10), padx=15
        )
        self.url1_frame.columnconfigure(1, weight=1)

        self.url1_label = ctk.CTkLabel(self.url1_frame, text="Url:", font=("Arial", 14))
        self.url1_label.grid(row=0, column=0, sticky="e", padx=(10, 0))

        self.url1_entry = ctk.CTkEntry(
            self.url1_frame,
            textvariable=self.url1_var,
            placeholder_text=self.translator.get_text("url_placeholder"),
        )
        self.url1_entry.grid(row=0, column=1, sticky="nsew", padx=10)

        #! Botão de Download
        self.download_button = ctk.CTkButton(
            self.main_frame_top,
            text=self.translator.get_text("download"),
            command=self.call_download,
            width=200,
            font=ctk.CTkFont(size=14),
        )
        self.download_button.pack(side="top")

        #! Frame para seleção de pasta de donwload
        self.download_path_frame = ctk.CTkFrame(
            self.main_frame_bottom, fg_color="transparent"
        )
        self.download_path_frame.pack(
            ipadx=5,
            fill="x",
            pady=(20, 10),
            padx=15,
        )
        self.download_path_frame.columnconfigure(0, weight=1)

        self.download_path_label = ctk.CTkLabel(
            self.download_path_frame, text=self.translator.get_text("download_path")
        )
        self.download_path_label.grid(row=0, column=0, padx=5, sticky="w")

        self.download_path_entry = ctk.CTkEntry(
            self.download_path_frame,
            placeholder_text=self.translator.get_text("folder_path"),
        )
        self.download_path_entry.grid(row=1, column=0, padx=5, pady=(2, 0), sticky="ew")

        self.download_path_button = ctk.CTkButton(
            self.download_path_frame,
            text=self.translator.get_text("select_folder"),
            command=self.download_path_select,
        )
        self.download_path_button.grid(row=1, column=1, padx=10, pady=(2, 0))

        # endregion

        #! Advanced Options
        # region Janela de Opções Avançadas
        self.advced_frame = ctk.CTkFrame(self.tab2, fg_color="transparent")
        self.advced_frame.pack(fill="both", expand=True, pady=10)

        self.advced_frame_top = ctk.CTkFrame(self.advced_frame, fg_color="transparent")
        self.advced_frame_top.pack(side="top", fill="both")

        self.advced_frame_bottom = ctk.CTkFrame(
            self.advced_frame, fg_color="transparent"
        )
        self.advced_frame_bottom.pack(side="bottom", fill="x")

        #! Frame de url
        # region
        self.url2_frame = ctk.CTkFrame(self.advced_frame_top, fg_color="transparent")
        self.url2_frame.pack(
            side="top", fill="x", expand=True, ipadx=5, ipady=5, pady=(10, 10), padx=15
        )
        self.url2_frame.columnconfigure(1, weight=1)

        self.url2_label = ctk.CTkLabel(self.url2_frame, text="Url:", font=("Arial", 14))
        self.url2_label.grid(row=0, column=0, sticky="e", padx=10)

        self.url2_entry = ctk.CTkEntry(
            self.url2_frame,
            textvariable=self.url2_var,
            placeholder_text=self.translator.get_text("url_placeholder"),
        )
        self.url2_entry.grid(row=0, column=1, sticky="nsew")
        # endregion

        #! Botão de Pesquisar
        # region
        self.search_button = ctk.CTkButton(
            self.url2_frame,
            text=self.translator.get_text("search"),
            command=self.call_download,
            width=100,
            font=ctk.CTkFont(size=14),
        )
        self.search_button.grid(row=0, column=2, sticky="w", padx=10)
        # endregion

        # endregion

        #! Settings
        # region Janela de Configurações
        self.settings_frame = ctk.CTkFrame(self.tab3, fg_color="transparent")
        self.settings_frame.pack(fill="both", expand=True, pady=10)

        self.settings_frame_top = ctk.CTkFrame(
            self.settings_frame, fg_color="transparent"
        )
        self.settings_frame_top.pack(side="top", fill="both", padx=15)

        self.settings_frame_bottom = ctk.CTkFrame(
            self.settings_frame, fg_color="transparent"
        )
        self.settings_frame_bottom.pack(side="bottom", fill="x")

        #! interface
        # region INTERFACE
        self.interface_label = ctk.CTkLabel(
            self.settings_frame_top,
            text=self.translator.get_text("interface"),
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        self.interface_label.pack(side="top")

        self.interface_div = ctk.CTkFrame(
            self.settings_frame_top, height=2, fg_color=("#D03434", "#A11D1D")
        )
        self.interface_div.pack(side="top", fill="x")

        self.interface_frame = ctk.CTkFrame(
            self.settings_frame_top, fg_color="transparent"
        )
        self.interface_frame.pack(side="top", fill="x", pady=10)

        #! Aparência
        # region APARÊNCIA
        self.appearance_frame = ctk.CTkFrame(
            self.interface_frame, fg_color="transparent"
        )
        self.appearance_frame.pack(side="left", expand=True, fill="x")

        self.appearance_label = ctk.CTkLabel(
            self.appearance_frame,
            width=100,
            text=self.translator.get_text("appearance") + ":",
            anchor="e",
        )
        self.appearance_label.pack(side="left")

        self.appearance_var = ctk.StringVar(value="Sistema")  # TODO pegar valor padrão

        self.appearance_dropdown = ctk.CTkOptionMenu(
            self.appearance_frame,
            values=list(self.translator.get_text("appearance_values").keys()),
            variable=self.appearance_var,
            command=lambda choice: ctk.set_appearance_mode(
                self.translator.get_text("appearance_values")[choice]
            ),
            width=120,
        )
        self.appearance_dropdown.pack(side="left", padx=(5, 0))

        # endregion

        #! Idioma
        # region IDIOMA
        self.language_frame = ctk.CTkFrame(self.interface_frame, fg_color="transparent")
        self.language_frame.pack(side="left", expand=True, fill="x")

        self.language_label = ctk.CTkLabel(
            self.language_frame,
            width=100,
            text=self.translator.get_text("language") + ":",
            anchor="e",
        )
        self.language_label.pack(side="left")

        self.language_var = ctk.StringVar(
            value=self.available_languages[self.default_config.DEFAULT_LANGUAGE]
        )

        self.language_dropdown = ctk.CTkOptionMenu(
            self.language_frame,
            values=list(self.available_languages.values()),
            variable=self.language_var,
            command=self.change_language,
            width=180,
        )
        self.language_dropdown.pack(side="left", padx=(5, 0))

        # endregion

        # endregion
        # endregion

        """
        #! Frame para seleção de arquivo .exe
        self.ffmpeg_path_frame = ctk.CTkFrame(self.bottom_frame, fg_color="transparent")
        self.ffmpeg_path_frame.grid(row=1, column=0, padx=5, pady=(0, 10), sticky="ew")
        self.ffmpeg_path_frame.grid_columnconfigure(0, weight=1)

        self.ffmpeg_path_label = ctk.CTkLabel(
            self.ffmpeg_path_frame, text=self.translator.get_text("ffmpeg_path")
        )
        self.ffmpeg_path_label.grid(row=0, column=0, padx=5, sticky="w")

        self.ffmpeg_path_entry = ctk.CTkEntry(
            self.ffmpeg_path_frame,
            placeholder_text=self.translator.get_text("exe_path"),
        )
        self.ffmpeg_path_entry.grid(row=1, column=0, padx=5, pady=(2, 0), sticky="ew")

        self.ffmpeg_path_button = ctk.CTkButton(
            self.ffmpeg_path_frame,
            text=self.translator.get_text("search_ffmpeg"),
            command=self.ffmpeg_path_select,
        )
        self.ffmpeg_path_button.grid(row=1, column=1, padx=(5, 3), pady=(2, 0))

        # Botão que redireciona para baixar o FFMPEG
        DOWNLOAD_ICON = "iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAACXBIWXMAAAsTAAALEwEAmpwYAAABEElEQVR4nO3WQW7CMBRF0bekshuGtKMuo8Muuu2tkMjgGwg2LcH2f0fKgEnid4MEkpmZmdnGKCgbHCBSNjhApGxwgEjZ4ACRssEBImWDA0TKBgeIlA0OECkbHCBSNjhApGyYMQDw8ugALc/YFPAB/ADvjwoAvALfwKc6HL+oikChYfyijwjArjgYp89v/xXgeK8rz9ipB5y/nZvfhNoA99z7KWg8aE2AYcbfc+BbAYYb33rwtQDDjm8ZcC3A8ONrh1wKMM34xdqgMsB04yt+w0vN/yWGweW3u2b8N/+HCPONb4gw7/iKCPOPX4mQZ/wCOABfp+ugjID98Xr2OcysHZ3R1uiMA2yN7AHMzMxMo/sFG0lNHgCxAKIAAAAASUVORK5CYII="
        self.ffmpeg_download_icon = ctk.CTkImage(
            b64_to_image(DOWNLOAD_ICON), size=(16, 16)
        )

        self.ffmpeg_download_button = ctk.CTkButton(
            self.ffmpeg_path_frame,
            text="",
            image=self.ffmpeg_download_icon,
            command=lambda: self.abrir_link("https://ffmpeg.org/download.html"),
            width=20,
        )
        self.ffmpeg_download_button.grid(row=1, column=2, padx=(0, 10), pady=(2, 0))

        # Carrega as configurações salvas
        self.load_saved_settings()

        # Quando a janela é fechada, ele executa a função
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        """

    # Função para atualizar var2 quando var1 mudar (sem causar loop infinito)
    def sync_var1_to_var2(self, *args):
        # Temporariamente remover o trace de var2 para evitar loop
        self.url2_var.trace_remove("write", self.trace_url2)

        # Copiar o valor
        self.url2_var.set(self.url1_var.get())

        # Reativar o trace
        self.trace_url2 = self.url2_var.trace_add("write", self.sync_var2_to_var1)

    # Função para atualizar var1 quando var2 mudar
    def sync_var2_to_var1(self, *args):
        # Temporariamente remover o trace de var1 para evitar loop
        self.url1_var.trace_remove("write", self.trace_url1)

        # Copiar o valor
        self.url1_var.set(self.url2_var.get())

        # Reativar o trace
        self.trace_url1 = self.url1_var.trace_add("write", self.sync_var1_to_var2)

    def change_language(self, language_name):
        # Obter código do idioma
        language_code = self.available_languages_inverted[language_name]

        # Alterar idioma
        if self.translator.change_language(language_code):
            # Atualizar todos os textos da interface
            self.update_interface_texts()

    def update_interface_texts(self):  # TODO Atualizar
        self.tabview.update_button_text()

        # region Traduzir Download
        self.playlist_entry_tooltip.configure(
            message=self.translator.get_text("playlist_tolltip")
        )
        self.playlist_check_tooltip.configure(
            message=self.translator.get_text("playlist_check_tolltip")
        )

        self.midia_label.configure(text=self.translator.get_text("media_type"))
        self.midia_var.set(
            self.translator.get_text("media_values")[0]
            if self.midia_var.get() in self.localized_video
            else self.translator.get_text("media_values")[1]
        )
        self.midia_SegButton.configure(values=self.translator.get_text("media_values"))
        self.formato_label.configure(text=self.translator.get_text("format"))
        self.qualidade_label.configure(text=self.translator.get_text("quality"))
        self.url1_entry.configure(
            placeholder_text=self.translator.get_text("url_placeholder")
        )
        self.download_button.configure(text=self.translator.get_text("download"))
        self.download_path_label.configure(
            text=self.translator.get_text("download_path")
        )
        self.download_path_entry.configure(
            placeholder_text=self.translator.get_text("folder_path")
        )
        self.download_path_button.configure(
            text=self.translator.get_text("select_folder")
        )

        # endregion

        # region Traduzir Config
        self.language_label.configure(text=self.translator.get_text("language") + ":")
        self.appearance_label.configure(
            text=self.translator.get_text("appearance") + ":"
        )
        self.appearance_dropdown.configure(
            values=self.translator.get_text("appearance_values")
        )
        for index, keys in enumerate(self.localized_appearance):
            if self.appearance_var.get() in keys:
                self.appearance_var.set(
                    list(self.translator.get_text("appearance_values").keys())[index]
                )

        # endregion

    def load_saved_settings(self):
        """Carrega as configurações salvas nos widgets"""
        # Carrega o caminho de download
        saved_download_path = self.user_prefer.get("download_path")
        self.download_path_entry.delete(0, "end")
        self.download_path_entry.insert(0, saved_download_path)

        """
        # Carrega o caminho do FFmpeg
        saved_ffmpeg_saved = self.user_prefer.get("ffmpeg_path")
        if saved_ffmpeg_saved:
            self.ffmpeg_path_entry.delete(0, "end")
            self.ffmpeg_path_entry.insert(0, saved_ffmpeg_saved)
        """

        # Carrega outras configurações
        self.midia_var.set(self.user_prefer.get("midia"))
        self.qualidade_var.set(self.user_prefer.get("quality"))
        self.switch_var.set(self.user_prefer.get("theme"))
        if self.midia_var.get() in self.localized_audio:
            self.midia_selected(self.midia_var.get())
        self.formato_var.set(self.user_prefer.get("format"))
        self.language_var.set(
            self.available_languages[self.user_prefer.get("language")]
        )

    def save_current_settings(self):
        """Salva as configurações atuais"""
        self.user_prefer.set("download_path", self.download_path_entry.get())
        # self.user_prefer.set("ffmpeg_path", self.ffmpeg_path_entry.get())
        self.user_prefer.set("midia", self.midia_var.get())
        self.user_prefer.set("format", self.formato_var.get())
        self.user_prefer.set("quality", self.qualidade_var.get())
        self.user_prefer.set("appearance", self.switch_var.get())
        self.user_prefer.set(
            "language", self.available_languages_inverted[self.language_var.get()]
        )
        self.user_prefer.save_preferences()

    def on_closing(self):
        """Chamado quando a janela é fechada"""
        self.save_current_settings()
        self.quit()

    # Mudar tema
    def toggle_theme(self):
        ctk.set_appearance_mode(self.appearance_var.get())

    # Muda as opções de extensão de acordo do tipo de multimida selecionado
    def midia_selected(self, valor):
        if valor in self.localized_audio:
            self.formato_OptionMenu.configure(values=["mp3", "m4a", "aac"])
            self.formato_var.set("mp3")
            self.qualidade_menu.configure(state="disabled")
        elif valor in self.localized_video:
            self.formato_OptionMenu.configure(values=["mp4", "mkv", "webm"])
            self.formato_var.set("mp4")
            self.qualidade_menu.configure(state="normal")

    def call_download(self):
        self.disable_button()

        erros = []
        if not self.url1_entry.get():
            erros.append(self.translator.get_text("errors")[0])
        if not self.download_path_entry.get():
            erros.append(self.translator.get_text("errors")[1])

        if erros:
            for erro in erros:
                self.show_error(erro)  # Exibir cada erro
            self.restore_button()
            return
        else:
            self.yt_dlp.start_download()

    def restore_button(self):
        self.download_button.configure(state="normal")

    def disable_button(self):
        self.download_button.configure(state="disabled")

    # Copia o caminho da pasta selecionada
    def download_path_select(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.download_path_entry.delete(0, "end")
            self.download_path_entry.insert(0, folder_path)

    """
    # Copia o caminho do .exe selecionado
    def ffmpeg_path_select(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Arquivos Executáveis", "*.exe"), ("Todos os Arquivos", "*.*")]
        )
        if file_path:
            self.ffmpeg_path_entry.delete(0, "end")
            self.ffmpeg_path_entry.insert(0, file_path)
    """

    # Mostra mensagem de erro
    def show_error(self, message):
        CTkMessagebox(title="Error", message=message, icon="cancel")

    # Mostra mensagem de sucesso
    def show_checkmark(self, message):
        CTkMessagebox(
            title=self.translator.get_text("success")[1], message=message, icon="check"
        )

    def abrir_link(self, url):
        webbrowser.open(url)

    def run(self):
        self.mainloop()


def main():
    """Função principal que inicializa o aplicativo"""
    ctk.set_default_color_theme(get_theme_path("red.json"))
    app = MainApplication()
    ctk.set_appearance_mode(app.user_prefer.get("appearance"))
    app.run()


if __name__ == "__main__":
    main()
