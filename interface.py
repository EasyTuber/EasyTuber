import webbrowser
import customtkinter as ctk
from PIL import Image
from tkinter import filedialog
from CTkMessagebox import CTkMessagebox
from CTkToolTip import CTkToolTip


from modules import (
    YoutubeDownloader,
    UserPreferences,
    DefaultConfig,
    TranslationManager,
    get_image_path,
    get_ffmpeg_path,
    play_sound,
    center_window,
)


class CustomTabview(ctk.CTkFrame):
    """
    Custom tab view widget with dynamic button and content frames.

    Attributes
    ----------
    master : ctk.CTk
        The parent widget.
    button_frame : ctk.CTkFrame
        Frame containing the tab buttons.
    content_frame : ctk.CTkFrame
        Frame containing the tab content.
    buttons : dict
        Dictionary mapping tab names to their respective buttons.
    tabs : dict
        Dictionary mapping tab names to their respective content frames.
    current_tab : str
        The currently selected tab.
    """

    def __init__(self, master, **kwargs):
        """
        Initializes the CustomTabview widget.

        Parameters
        ----------
        master : ctk.CTk
            The parent widget.
        **kwargs
            Additional keyword arguments passed to ctk.CTkFrame.
        """
        super().__init__(master, **kwargs)

        # Create frame for buttons
        self.button_frame = ctk.CTkFrame(self, corner_radius=10)
        self.button_frame.pack(side="top", fill="x", padx=10)
        self.button_frame.rowconfigure(0, weight=1)

        # Create frame for content
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        # Dictionaries to store buttons and frames
        self.buttons = {}
        self.tabs = {}
        self.current_tab = None

    def add(self, name, text):
        """
        Adds a new tab with the given name and button text.

        Parameters
        ----------
        name : str
            Unique identifier for the tab.
        text : str
            Text displayed on the tab button.

        Returns
        -------
        ctk.CTkFrame
            The content frame for the newly added tab.
        """
        # Calculate position for the new button
        button_position = len(self.buttons)

        # Create button for the tab
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

        # Create frame for the tab content
        tab_frame = ctk.CTkFrame(
            self.content_frame,
            corner_radius=10,
            fg_color=("gray95", "gray17"),
        )

        # Store references
        self.buttons[name] = button
        self.tabs[name] = tab_frame

        # If this is the first tab, select it
        if not self.current_tab:
            self.select(name)

        return tab_frame

    def select(self, name):
        """
        Selects the tab with the given name.

        Parameters
        ----------
        name : str
            The name of the tab to select.
        """
        # Hide the currently visible tab
        if self.current_tab:
            self.tabs[self.current_tab].pack_forget()

            # Restore appearance of the unselected button
            self.buttons[self.current_tab].configure(
                fg_color="transparent",
                hover_color=("gray90", "gray30"),
                text_color=("gray50", "gray70"),
            )

        # Show the selected tab
        self.tabs[name].pack(fill="both", expand=True)

        # Highlight the selected button
        self.buttons[name].configure(
            fg_color=("#D03434", "#A11D1D"),
            hover_color=("#AE2727", "#B81D1D"),
            text_color=("#DCE4EE", "#DCE4EE"),
        )

        # Update the current tab
        self.current_tab = name

    def update_button_text(self):
        """
        Updates the text of all tab buttons based on the master's translator.
        """
        # Check if the button exists
        for name in self.buttons:
            new_text = self.master.translator.get_text(name)
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

        # TODO Work in Progress (Advanced)
        """
        # Registrar os traces iniciais (com escopo global para poder removê-los)
        self.trace_url1 = self.url1_var.trace_add("write", self.sync_var1_to_var2)
        self.trace_url2 = self.url2_var.trace_add("write", self.sync_var2_to_var1)
        """

        self.title(f"{self.default_config.APP_NAME} v{self.default_config.APP_VERSION}")

        self.width = self.default_config.DEFAULT_WINDOW_WIDTH
        self.height = self.default_config.DEFAULT_WINDOW_HEIGHT
        center_window(self, self.width, self.height)
        self.resizable(False, False)
        self.lift()

        self.after(250, lambda: self.iconbitmap(get_image_path("icon.ico")))

        # Outras variaveis
        self.download_options = {}

        # endregion

        #! Logo e título lado a lado
        # region Logo e título
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

        #! Criar o tabview personalizado
        # region TabView
        self.tabview = CustomTabview(self, fg_color="transparent")
        self.tabview.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Adicionar abas
        self.tab1 = self.tabview.add(
            "download", self.translator.get_text("download")
        )  # Download
        # TODO Work in Progress (Advanced)
        """
        self.tab2 = self.tabview.add(
            "advanced_options", self.translator.get_text("advanced_options")
        )  # Advanced
        """
        self.tab3 = self.tabview.add(
            "settings", self.translator.get_text("settings")
        )  # Settings
        self.tab4 = self.tabview.add(
            "about", self.translator.get_text("about")
        )  # About
        # endregion

        #! Área principal do conteúdo
        # region Área principal do conteúdo
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
        # region Playlist
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
        # endregion

        #! Tipo de Mídia
        # region Tipo de Mídia
        self.media_frame = ctk.CTkFrame(
            self.config_download_frame, fg_color="transparent"
        )
        self.media_frame.pack(side="left", expand=True, padx=5)

        self.media_label = ctk.CTkLabel(
            self.media_frame, text=self.translator.get_text("media_type")
        )
        self.media_label.grid(row=0, column=0, pady=(0, 1), sticky="ew")

        self.media_var = ctk.StringVar(value=self.user_prefer.get("media"))
        self.media_SegButton = ctk.CTkSegmentedButton(
            self.media_frame,
            values=self.translator.get_text("media_values"),
            variable=self.media_var,
            command=self.media_selected,
        )
        self.media_SegButton.grid(row=1, column=0, sticky="ew")
        # endregion

        #! Formato do arquivo
        # region Formato
        self.formato_frame = ctk.CTkFrame(
            self.config_download_frame, fg_color="transparent"
        )
        self.formato_frame.pack(side="left", expand=True, padx=5)

        self.formato_label = ctk.CTkLabel(
            self.formato_frame, text=self.translator.get_text("format")
        )
        self.formato_label.grid(row=0, column=0, pady=(0, 1), sticky="ew")

        self.formato_var = ctk.StringVar(value=self.user_prefer.get("format"))
        self.formato_OptionMenu = ctk.CTkOptionMenu(
            self.formato_frame,
            dynamic_resizing=False,
            values=["mp4", "mkv", "webm"],
            variable=self.formato_var,
            width=80,
        )
        self.formato_OptionMenu.grid(row=1, column=0, sticky="ew")
        # endregion

        #! Qualidade do Video
        # region Qualidade do Video
        self.qualidade_frame = ctk.CTkFrame(
            self.config_download_frame, fg_color="transparent"
        )
        self.qualidade_frame.pack(side="left", expand=True, padx=5)

        self.qualidade_var = ctk.StringVar(value=self.user_prefer.get("quality"))
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
        self.media_selected(self.media_var.get(), True)
        # endregion

        #! Frame de url
        # region URL entry
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
        # endregion

        #! Botão de Download
        # region Botão Download
        self.download_button = ctk.CTkButton(
            self.main_frame_top,
            text=self.translator.get_text("download_button"),
            command=lambda: self.call_download("basic"),
            width=200,
            font=ctk.CTkFont(size=14),
        )
        self.download_button.pack(side="top")
        # endregion

        #! Frame para seleção de pasta de donwload
        # region Download Path
        self.download_path_frame = ctk.CTkFrame(
            self.main_frame_bottom, fg_color="transparent"
        )
        self.download_path_frame.pack(
            side="top",
            fill="x",
            pady=(20, 10),
            padx=25,
        )

        self.download_path_frame_top = ctk.CTkFrame(
            self.download_path_frame, fg_color="transparent"
        )
        self.download_path_frame_top.pack(side="top", fill="x")

        self.download_path_frame_buttom = ctk.CTkFrame(
            self.download_path_frame, fg_color="transparent"
        )
        self.download_path_frame_buttom.pack(side="top", fill="x")

        self.download_path_label = ctk.CTkLabel(
            self.download_path_frame_top,
            width=130,
            anchor="w",
            text=self.translator.get_text("download_path"),
        )
        self.download_path_label.pack(side="left", fill="x")

        self.download_path_entry = ctk.CTkEntry(
            self.download_path_frame_buttom,
            placeholder_text=self.translator.get_text("folder_path"),
        )
        self.download_path_entry.pack(side="left", expand=True, fill="x", padx=(0, 5))

        last_download_path = self.user_prefer.get("last_download_path")
        if last_download_path:
            self.download_path_entry.insert(0, last_download_path)
        else:
            self.download_path_entry.insert(
                0, self.user_prefer.get("default_download_path")
            )

        self.download_path_button = ctk.CTkButton(
            self.download_path_frame_buttom,
            text=self.translator.get_text("select_folder"),
            command=lambda: self.download_path_select(self.download_path_entry),
        )
        self.download_path_button.pack(side="left")

        self.download_path_reset_icon = ctk.CTkImage(
            Image.open(get_image_path("reset_icon.png")),
            size=(16, 16),
        )

        self.download_path_reset = ctk.CTkButton(
            self.download_path_frame_buttom,
            text="",
            image=self.download_path_reset_icon,
            command=lambda: self.reset_download_path(),
            width=28,
            corner_radius=5,
        )
        self.download_path_reset.pack(side="left", padx=(2, 0))
        # endregion

        # endregion

        #! Advanced Options
        # TODO Work in Progress (Advanced)
        """ 
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
        """

        #! Settings
        # region Janela Configurações
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
        self.appearance_frame.pack(side="left", expand=True)

        self.appearance_label = ctk.CTkLabel(
            self.appearance_frame,
            # width=100,
            text=self.translator.get_text("appearance") + ":",
            anchor="e",
        )
        self.appearance_label.pack(side="left")

        self.appearance_var = ctk.StringVar(value=self.user_prefer.get("appearance"))

        self.appearance_dropdown = ctk.CTkOptionMenu(
            self.appearance_frame,
            values=list(self.translator.get_text("appearance_values").keys()),
            variable=self.appearance_var,
            command=lambda choice: ctk.set_appearance_mode(
                self.translator.get_text("appearance_values")[choice]
            ),
            width=100,
        )
        self.appearance_dropdown.pack(side="left", padx=(5, 0))

        # endregion

        #! Idioma
        # region IDIOMA
        self.language_frame = ctk.CTkFrame(self.interface_frame, fg_color="transparent")
        self.language_frame.pack(side="left", expand=True)

        self.language_label = ctk.CTkLabel(
            self.language_frame,
            # width=100,
            text=self.translator.get_text("language") + ":",
            anchor="e",
        )
        self.language_label.pack(side="left")

        self.language_var = ctk.StringVar(
            value=self.available_languages[self.user_prefer.get("language")]
        )

        self.language_dropdown = ctk.CTkOptionMenu(
            self.language_frame,
            values=list(self.available_languages.values()),
            variable=self.language_var,
            command=self.change_language,
            width=140,
        )
        self.language_dropdown.pack(side="left", padx=(5, 0))

        # endregion

        #! Notificação Sonora
        # region NOTIFICAÇÂO SONORA
        self.sound_notification_var = ctk.BooleanVar(
            value=self.user_prefer.get("sound_notification")
        )
        self.sound_notification_checkbox = ctk.CTkCheckBox(
            self.interface_frame,
            text=self.translator.get_text("sound_notification"),
            variable=self.sound_notification_var,
            onvalue=True,
            offvalue=False,
        )
        self.sound_notification_checkbox.pack(side="left", expand=True, padx=5)

        # endregion

        # endregion

        #! Pós download
        # region Pós-Download
        self.post_download_label = ctk.CTkLabel(
            self.settings_frame_top,
            text=self.translator.get_text("post_download"),
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        self.post_download_label.pack(side="top")

        self.post_download_div = ctk.CTkFrame(
            self.settings_frame_top, height=2, fg_color=("#D03434", "#A11D1D")
        )
        self.post_download_div.pack(side="top", fill="x")

        self.post_download_frame = ctk.CTkFrame(
            self.settings_frame_top, fg_color="transparent"
        )
        self.post_download_frame.pack(side="top", fill="x", pady=10)

        self.clear_url_var = ctk.BooleanVar(value=self.user_prefer.get("clear_url"))
        self.open_folder_var = ctk.BooleanVar(value=self.user_prefer.get("open_folder"))
        self.notify_completed_var = ctk.BooleanVar(
            value=self.user_prefer.get("notify_completed")
        )

        # Limpar url
        self.clear_url_checkbox = ctk.CTkCheckBox(
            self.post_download_frame,
            text=self.translator.get_text("check_clear_url"),
            variable=self.clear_url_var,
            onvalue=True,
            offvalue=False,
        )
        self.clear_url_checkbox.pack(side="left", expand=True, padx=5)

        # Abrir pasta
        self.open_folder_checkbox = ctk.CTkCheckBox(
            self.post_download_frame,
            text=self.translator.get_text("check_open_folder"),
            variable=self.open_folder_var,
            onvalue=True,
            offvalue=False,
        )
        self.open_folder_checkbox.pack(side="left", expand=True, padx=5)

        self.open_folder_tolltip = CTkToolTip(
            self.open_folder_checkbox,
            justify="left",
            padding=(10, 10),
            border_width=1,
            x_offset=-50,
            follow=False,
            message=self.translator.get_text("check_open_folder_tolltip"),
        )

        # Notificar quando concluido
        self.notify_completed_checkbox = ctk.CTkCheckBox(
            self.post_download_frame,
            text=self.translator.get_text("check_notify_completed"),
            variable=self.notify_completed_var,
            onvalue=True,
            offvalue=False,
        )
        self.notify_completed_checkbox.pack(side="left", expand=True, padx=5)

        self.notify_completed_tooltip = CTkToolTip(
            self.notify_completed_checkbox,
            justify="left",
            padding=(10, 10),
            border_width=1,
            x_offset=-50,
            follow=False,
            message=self.translator.get_text("check_notify_completed_tolltip"),
        )

        # endregion

        #! Caminhos Padrão
        # region Default Paths
        self.default_label = ctk.CTkLabel(
            self.settings_frame_top,
            text=self.translator.get_text("default_paths"),
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        self.default_label.pack(side="top")

        self.default_div = ctk.CTkFrame(
            self.settings_frame_top, height=2, fg_color=("#D03434", "#A11D1D")
        )
        self.default_div.pack(side="top", fill="x")

        self.default_frame = ctk.CTkFrame(
            self.settings_frame_top, fg_color="transparent"
        )
        self.default_frame.pack(side="top", fill="x", pady=10)

        #! Frame para seleção de arquivo .exe
        # region FFMPEG
        self.ffmpeg_path_frame = ctk.CTkFrame(
            self.default_frame, fg_color="transparent"
        )
        self.ffmpeg_path_frame.pack(side="top", expand=True, fill="x", pady=(0, 10))

        self.ffmpeg_path_label = ctk.CTkLabel(
            self.ffmpeg_path_frame,
            text="FFmpeg:",
            anchor="w",
        )
        self.ffmpeg_path_label.pack(side="left")

        self.ffmpeg_path_entry = ctk.CTkEntry(
            self.ffmpeg_path_frame,
            placeholder_text=self.translator.get_text("exe_path"),
        )
        self.ffmpeg_path_entry.pack(side="left", expand=True, fill="x", padx=5)

        self.ffmpeg_path_button = ctk.CTkButton(
            self.ffmpeg_path_frame,
            text=self.translator.get_text("search_ffmpeg"),
            command=self.ffmpeg_path_select,
        )
        self.ffmpeg_path_button.pack(side="left")

        ffmpeg_path = self.user_prefer.get("ffmpeg_path")
        if not ffmpeg_path:
            ffmpeg_path = get_ffmpeg_path()
            if ffmpeg_path:
                self.ffmpeg_path_entry.insert(0, ffmpeg_path.replace("\\", "/"))
            else:
                self.ffmpeg_popup()
        else:
            self.ffmpeg_path_entry.insert(0, ffmpeg_path)
        # endregion

        #! Frame para seleção de pasta de donwload
        # region Download Default
        self.default_download_path_frame = ctk.CTkFrame(
            self.default_frame, fg_color="transparent"
        )
        self.default_download_path_frame.pack(side="top", expand=True, fill="x")

        self.default_download_path_label = ctk.CTkLabel(
            self.default_download_path_frame,
            text="Download:",
            width=50,
            anchor="w",
        )
        self.default_download_path_label.pack(side="left")

        self.default_download_path_entry = ctk.CTkEntry(
            self.default_download_path_frame,
            placeholder_text=self.translator.get_text("folder_path"),
        )
        self.default_download_path_entry.pack(
            side="left", expand=True, fill="x", padx=5
        )
        self.default_download_path_entry.insert(
            0, self.user_prefer.get("default_download_path")
        )

        self.default_download_tooltip = CTkToolTip(
            self.default_download_path_entry,
            justify="left",
            padding=(5, 5),
            border_width=1,
            x_offset=-50,
            y_offset=-55,
            follow=False,
            message=self.translator.get_text("donwload_path_tooltip"),
        )

        self.default_download_path_button = ctk.CTkButton(
            self.default_download_path_frame,
            text=self.translator.get_text("select_folder"),
            command=lambda: self.download_path_select(self.default_download_path_entry),
        )
        self.default_download_path_button.pack(side="left")
        # endregion

        # endregion

        # endregion

        #! About
        # region Janela Sobre
        self.about_frame = ctk.CTkFrame(self.tab4, fg_color="transparent")
        self.about_frame.pack(fill="both", expand=True, pady=10)

        self.about_frame_top = ctk.CTkFrame(self.about_frame, fg_color="transparent")
        self.about_frame_top.pack(side="top", fill="both", padx=15)

        self.about_frame_bottom = ctk.CTkFrame(self.about_frame, fg_color="transparent")
        self.about_frame_bottom.pack(side="bottom", fill="x")

        #! Informações do Desenvolvedor
        # region DESENVOLVEDOR
        self.dev_label = ctk.CTkLabel(
            self.about_frame_top,
            text=self.translator.get_text("developed_by"),
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        self.dev_label.pack(side="top", pady=(0, 5))

        self.dev_div = ctk.CTkFrame(
            self.about_frame_top, height=2, fg_color=("#D03434", "#A11D1D")
        )
        self.dev_div.pack(side="top", fill="x")

        #! Versão
        self.version_label = ctk.CTkLabel(
            self.about_frame_top,
            text=self.translator.get_text("version").format(
                version=self.default_config.APP_VERSION
            ),
            font=ctk.CTkFont(size=14),
        )
        self.version_label.pack(side="top", pady=(20, 5))

        #! Links
        self.github_button = ctk.CTkButton(
            self.about_frame_top,
            text="GitHub",
            command=lambda: self.open_link(self.default_config.APP_WEBSITE),
            width=120,
            font=ctk.CTkFont(size=13),
        )
        self.github_button.pack(side="top", pady=5)

        #! Ferramentas
        self.tools_label = ctk.CTkLabel(
            self.about_frame_top,
            text=self.translator.get_text("tools"),
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.tools_label.pack(side="top", pady=(20, 5))

        #! Principais
        self.main_tools_frame = ctk.CTkFrame(
            self.about_frame_top, fg_color="transparent"
        )
        self.main_tools_frame.pack(side="top", fill="x", pady=5)

        self.python_logo = ctk.CTkImage(
            light_image=Image.open(get_image_path("python_logo.png")),
            dark_image=Image.open(get_image_path("python_logo.png")),
            size=(80, 25),  # Mantém proporção original de 498x155
        )

        self.python_button = ctk.CTkButton(
            self.main_tools_frame,
            text="",
            image=self.python_logo,
            command=lambda: self.open_link("https://www.python.org/"),
            width=150,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.python_button.pack(side="left", padx=5, expand=True)

        self.ytdlp_logo = ctk.CTkImage(
            light_image=Image.open(get_image_path("ytdlp_logo.png")),
            dark_image=Image.open(get_image_path("ytdlp_logo.png")),
            size=(25, 25),
        )

        self.ytdlp_button = ctk.CTkButton(
            self.main_tools_frame,
            text="yt-dlp",
            image=self.ytdlp_logo,
            command=lambda: self.open_link("https://github.com/yt-dlp/yt-dlp"),
            width=150,
        )
        self.ytdlp_button.pack(side="left", padx=5, expand=True)

        self.customtkinter_logo = ctk.CTkImage(
            light_image=Image.open(get_image_path("customtkinter_logo.png")),
            dark_image=Image.open(get_image_path("customtkinter_logo.png")),
            size=(116, 25),  # Mantém proporção original de 1231x264
        )

        self.customtkinter_button = ctk.CTkButton(
            self.main_tools_frame,
            text="",
            image=self.customtkinter_logo,
            command=lambda: self.open_link(
                "https://github.com/TomSchimansky/CustomTkinter"
            ),
            width=150,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.customtkinter_button.pack(side="left", padx=5, expand=True)

        #! Componentes
        self.tools_frame = ctk.CTkFrame(self.about_frame_top, fg_color="transparent")
        self.tools_frame.pack(side="top", fill="x", pady=5)

        self.ctkmsg_button = ctk.CTkButton(
            self.tools_frame,
            text="CTkMessagebox",
            command=lambda: self.open_link("https://github.com/Akascape/CTkMessagebox"),
            width=120,
            font=ctk.CTkFont(size=13),
        )
        self.ctkmsg_button.pack(side="left", padx=5, expand=True)

        self.ctktool_button = ctk.CTkButton(
            self.tools_frame,
            text="CTkToolTip",
            command=lambda: self.open_link("https://github.com/Akascape/CTkToolTip"),
            width=120,
            font=ctk.CTkFont(size=13),
        )
        self.ctktool_button.pack(side="left", padx=5, expand=True)

        self.ctktheme_button = ctk.CTkButton(
            self.tools_frame,
            text="CTkThemesPack",
            command=lambda: self.open_link("https://github.com/a13xe/CTkThemesPack"),
            width=120,
            font=ctk.CTkFont(size=13),
        )
        self.ctktheme_button.pack(side="left", padx=5, expand=True)

        self.ctkcomp_button = ctk.CTkButton(
            self.tools_frame,
            text="ctk_components",
            command=lambda: self.open_link(
                "https://github.com/rudymohammadbali/ctk_components"
            ),
            width=120,
            font=ctk.CTkFont(size=13),
        )
        self.ctkcomp_button.pack(side="left", padx=5, expand=True)

        # Quando a janela é fechada, ele executa a função
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    # TODO Work in Progress (Advanced)
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
    """

    def change_language(self, language_name):
        # Obter código do idioma
        language_code = self.available_languages_inverted[language_name]

        # Alterar idioma
        if self.translator.change_language(language_code):
            # Atualizar todos os textos da interface
            self.update_interface_texts()

    def update_interface_texts(self):
        self.tabview.update_button_text()

        # region Traduzir Download
        self.playlist_entry_tooltip.configure(
            message=self.translator.get_text("playlist_tolltip")
        )
        self.playlist_check_tooltip.configure(
            message=self.translator.get_text("playlist_check_tolltip")
        )

        self.media_label.configure(text=self.translator.get_text("media_type"))
        self.media_var.set(
            self.translator.get_text("media_values")[0]
            if self.media_var.get() in self.localized_video
            else self.translator.get_text("media_values")[1]
        )
        self.media_SegButton.configure(values=self.translator.get_text("media_values"))
        self.formato_label.configure(text=self.translator.get_text("format"))
        self.qualidade_label.configure(text=self.translator.get_text("quality"))
        self.url1_entry.configure(
            placeholder_text=self.translator.get_text("url_placeholder")
        )
        self.download_button.configure(text=self.translator.get_text("download_button"))
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
        self.sound_notification_checkbox.configure(
            text=self.translator.get_text("sound_notification")
        )

        self.post_download_label.configure(
            text=self.translator.get_text("post_download")
        )
        self.clear_url_checkbox.configure(
            text=self.translator.get_text("check_clear_url")
        )
        self.open_folder_checkbox.configure(
            text=self.translator.get_text("check_open_folder")
        )
        self.open_folder_tolltip.configure(
            message=self.translator.get_text("check_open_folder_tolltip")
        )
        self.notify_completed_checkbox.configure(
            text=self.translator.get_text("check_notify_completed")
        )
        self.notify_completed_tooltip.configure(
            message=self.translator.get_text("check_notify_completed_tolltip")
        )

        self.default_label.configure(text=self.translator.get_text("default_paths"))
        self.ffmpeg_path_entry.configure(
            placeholder_text=self.translator.get_text("exe_path")
        )
        self.ffmpeg_path_button.configure(
            text=self.translator.get_text("search_ffmpeg")
        )
        self.default_download_path_entry.configure(
            placeholder_text=self.translator.get_text("folder_path")
        )
        self.default_download_path_button.configure(
            text=self.translator.get_text("select_folder")
        )
        self.default_download_tooltip.configure(
            message=self.translator.get_text("donwload_path_tooltip")
        )

        self.dev_label.configure(text=self.translator.get_text("developed_by"))
        self.version_label.configure(
            text=self.translator.get_text("version").format(
                version=self.default_config.APP_VERSION
            )
        )
        self.tools_label.configure(text=self.translator.get_text("tools"))

        # endregion

    def save_current_settings(self):
        """Salva as configurações atuais"""
        self.user_prefer.set("last_download_path", self.download_path_entry.get())
        self.user_prefer.set(
            "default_download_path", self.default_download_path_entry.get()
        )
        self.user_prefer.set("ffmpeg_path", self.ffmpeg_path_entry.get())
        self.user_prefer.set("media", self.media_var.get())
        self.user_prefer.set("format", self.formato_var.get())
        self.user_prefer.set("quality", self.qualidade_var.get())
        self.user_prefer.set("appearance", self.appearance_var.get())
        self.user_prefer.set(
            "language", self.available_languages_inverted[self.language_var.get()]
        )
        self.user_prefer.set("sound_notification", self.sound_notification_var.get())
        self.user_prefer.set("clear_url", self.clear_url_var.get())
        self.user_prefer.set("open_folder", self.open_folder_var.get())
        self.user_prefer.set("notify_completed", self.notify_completed_var.get())
        self.user_prefer.save_preferences()

    def on_closing(self):
        """Chamado quando a janela é fechada"""
        self.save_current_settings()
        self.quit()

    def reset_download_path(self):
        path = self.default_download_path_entry.get()
        self.download_path_entry.delete(0, "end")
        self.download_path_entry.insert(0, path)

    # Muda as opções de extensão de acordo do tipo de multimida selecionado
    def media_selected(self, valor, init=False):
        if valor in self.localized_audio:
            self.formato_OptionMenu.configure(values=self.default_config.FORMAT_AUDIOS)
            if not init:
                self.formato_var.set("mp3")
                self.qualidade_menu.configure(state="disabled")
        elif valor in self.localized_video:
            self.formato_OptionMenu.configure(values=self.default_config.FORMAT_VIDEOS)
            if not init:
                self.formato_var.set("mp4")
                self.qualidade_menu.configure(state="normal")

    def call_download(self, type: str):
        self.disable_button()

        erros = []
        if not self.url1_entry.get():
            erros.append(self.translator.get_text("errors")[0])
        if not self.download_path_entry.get():
            erros.append(self.translator.get_text("errors")[1])
        if not self.ffmpeg_path_entry.get():
            self.ffmpeg_popup()

        if erros:
            for erro in erros:
                if self.sound_notification_var.get():
                    play_sound(False)
                self.show_error(erro)  # Exibir cada erro
            self.restore_button()
            return
        else:
            self.download_options.clear()
            self.download_options = {
                "url": self.url1_entry.get(),
                "download_path": self.download_path_entry.get(),
                "ffmpeg_path": self.ffmpeg_path_entry.get(),
            }
            if type == "basic":
                self.download_options.update(
                    {
                        "media": self.media_var.get(),
                        "format": self.formato_var.get(),
                        "quality": self.qualidade_var.get().replace("p", ""),
                        "playlist": self.playlist_check_var.get(),
                        "playlist_items": self.playlist_entry.get(),
                    }
                )
            elif type == "advanced":
                # TODO Work in Progress (Advanced)
                pass
            self.yt_dlp.start_download(type)

    def restore_button(self):
        self.download_button.configure(state="normal")

    def disable_button(self):
        self.download_button.configure(state="disabled")

    # Copia o caminho da pasta selecionada
    def download_path_select(self, path_entry):
        folder_path = filedialog.askdirectory()
        if folder_path:
            path_entry.delete(0, "end")
            path_entry.insert(0, folder_path)

    # Copia o caminho do .exe selecionado
    def ffmpeg_path_select(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                (self.translator.get_text("filetypes")[0], "*.exe"),
                (self.translator.get_text("filetypes")[1], "*.*"),
            ]
        )
        if file_path:
            self.ffmpeg_path_entry.delete(0, "end")
            self.ffmpeg_path_entry.insert(0, file_path)

    # Mostra mensagem de erro
    def show_error(self, message):
        CTkMessagebox(title="Error", message=message, icon="cancel")

    # Mostra mensagem de sucesso
    def show_checkmark(self, message):
        CTkMessagebox(
            title=self.translator.get_text("success")[1], message=message, icon="check"
        )

    def ffmpeg_popup(self):
        title = self.translator.get_text("popup_ffmpeg_title")
        text = self.translator.get_text("popup_ffmpeg_msg")
        option = list(self.translator.get_text("popup_ffmpeg_options").keys())

        msg = CTkMessagebox(
            width=600,
            title=title,
            message=text,
            icon="warning",
            option_1=option[0],
            option_2=option[1],
            option_3=option[2],
        )
        response = msg.get()

        if response == option[0]:
            self.ffmpeg_path_select()
        elif response == option[1]:
            self.open_link("https://community.chocolatey.org/packages/ffmpeg")
        elif response == option[2]:
            self.open_link(
                "https://github.com/EasyTuber/EasyTuber?tab=readme-ov-file#-pr%C3%A9-requisitos"
            )

    def open_link(self, url):
        webbrowser.open(url)

    def run(self):
        self.mainloop()
