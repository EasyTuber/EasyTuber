import sys
import webbrowser
import customtkinter as ctk
from PIL import Image, ImageTk
from tkinter import filedialog
from CTkMessagebox import CTkMessagebox
from CTkToolTip import CTkToolTip

from modules import (
    YoutubeDownloader,
    UserPreferences,
    DefaultConfig,
    TranslationManager,
    UpdateChecker,
    get_image_path,
    get_ffmpeg_path,
    play_sound,
    center_window,
    get_thumbnail_img,
    create_rounded_image,
)

from ui import DownloadTab, AdvancedTab, SettingsTab, AboutTab

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
            fg_color=("gray90", "gray17"),
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
        self.update_checker = UpdateChecker(self)

        # Variaveis de tradução
        self.available_languages = self.translator.available_languages
        self.available_languages_inverted = {
            v: k for k, v in self.available_languages.items()
        }
        self.last_language = self.user_prefer.get("language")

        # Variaveis de url para compartilhar entre elas
        self.url1_var = ctk.StringVar()
        self.url2_var = ctk.StringVar()

        # Registrar os traces iniciais (com escopo global para poder removê-los)
        self.trace_url1 = self.url1_var.trace_add("write", self.sync_var1_to_var2)
        self.trace_url2 = self.url2_var.trace_add("write", self.sync_var2_to_var1)

        self.title(f"{self.default_config.APP_NAME} v{self.default_config.APP_VERSION}")

        self.width = self.default_config.DEFAULT_WINDOW_WIDTH
        self.height = self.default_config.DEFAULT_WINDOW_HEIGHT
        center_window(self, self.width, self.height)
        self.resizable(False, False)
        self.lift()


        if sys.platform.startswith("win"):
            self.after(250, lambda: self.iconbitmap(get_image_path("icon.ico")))
        else:
            icon = ImageTk.PhotoImage(file=get_image_path("logo.png"))
            self.after(250, lambda: self.wm_iconphoto(True, icon))
        

        # Outras variaveis
        self.download_options = {}
        self.info_preview = {}
        self.info_presets = {}
        self.audio_id = None

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
        self.tab2 = self.tabview.add(
            "advanced_options", self.translator.get_text("advanced_options")
        )  # Advanced
        self.tab3 = self.tabview.add(
            "settings", self.translator.get_text("settings")
        )  # Settings
        self.tab4 = self.tabview.add(
            "about", self.translator.get_text("about")
        )  # About
        # endregion
        
        self.advanced_tab = AdvancedTab(self.tab2, app=self, translator=self.translator, yt_dlp=self.yt_dlp, fg_color="transparent")
        self.advanced_tab.pack(fill="both", expand=True)
        
        self.settings_tab = SettingsTab(self.tab3, app=self, translator=self.translator, user_prefer=self.user_prefer, fg_color="transparent")
        self.settings_tab.pack(fill="both", expand=True)
        
        self.about_tab = AboutTab(self.tab4, app=self, translator=self.translator, default_config=self.default_config, fg_color="transparent")
        self.about_tab.pack(fill="both", expand=True)

        self.download_tab = DownloadTab(self.tab1, app=self, translator=self.translator, user_prefer=self.user_prefer, yt_dlp=self.yt_dlp, default_config=self.default_config, advanced_tab=self.advanced_tab, settings_tab=self.settings_tab, fg_color="transparent")
        self.download_tab.pack(fill="both", expand=True)

        # Quando a janela é fechada, ele executa a função
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

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

    # TODO Work in Progress (Language)
    def change_language(self, language_name):
        # Obter código do idioma
        language_code = self.available_languages_inverted[language_name]

        # Alterar idioma
        if self.translator.change_language(language_code):
            # Atualizar todos os textos da interface
            self.update_interface_texts()

            self.last_language = language_code

    def update_interface_texts(self):
        self.save_current_settings()
        self.tabview.update_button_text()

        self.download_tab.update_language()
        self.advanced_tab.update_language()
        self.settings_tab.update_language()
        self.about_tab.update_language()

    def save_current_settings(self):
        """Salva as configurações atuais"""
        self.user_prefer.set("last_download_path", self.download_tab.download_path_entry.get())
        self.user_prefer.set(
            "default_download_path", self.settings_tab.default_download_path_entry.get()
        )
        self.user_prefer.set("ffmpeg_path", self.settings_tab.ffmpeg_path_entry.get())
        self.user_prefer.set(
            "media",
            self.translator.get_key_by_value(
                self.translator.get_text("media_values", self.last_language),
                self.download_tab.media_var.get(),
            ),
        )
        self.user_prefer.set("format", self.download_tab.formato_var.get())
        self.user_prefer.set("quality", self.download_tab.qualidade_var.get())
        self.user_prefer.set(
            "appearance",
            self.translator.get_key_by_value(
                self.translator.get_text("appearance_values", self.last_language),
                self.settings_tab.appearance_var.get(),
            ),
        )
        self.user_prefer.set(
            "language", self.available_languages_inverted[self.settings_tab.language_var.get()]
        )
        self.user_prefer.set("sound_notification", self.settings_tab.sound_notification_var.get())
        self.user_prefer.set("clear_url", self.settings_tab.clear_url_var.get())
        self.user_prefer.set("open_folder", self.settings_tab.open_folder_var.get())
        self.user_prefer.set("notify_completed", self.settings_tab.notify_completed_var.get())

    def on_closing(self):
        """Chamado quando a janela é fechada"""
        self.save_current_settings()
        self.user_prefer.save_preferences()
        self.quit()

    def show_error(self, message):
        CTkMessagebox(title="Error", message=message, icon="cancel")

    def show_checkmark(self, message):
        msg = CTkMessagebox(
            title=self.translator.get_text("success")[1],
            message=message,
            icon="check",
            wraplength=400,
            sound=self.sound_notification_var.get(),
        )
        msg.get()

    def show_update_available(self, update_info):
        title = self.translator.get_text("popup_update_title")
        message = self.translator.get_text("popup_update_msg").format(
            version=update_info["latest_version"]
        )
        option = list(self.translator.get_text("popup_update_options").keys())

        msg = CTkMessagebox(
            width=450,
            title=title,
            message=message,
            icon="info",
            option_1=option[0],
            option_2=option[1],
            wraplength=400,
        )
        response = msg.get()

        if response == option[0]:
            self.open_link(update_info["release_url"])

    def ffmpeg_popup(self):
        title = self.translator.get_text("popup_ffmpeg_title")
        text = self.translator.get_text("popup_ffmpeg_msg")
        option = self.translator.get_text("popup_ffmpeg_options")

        msg = CTkMessagebox(
            width=600,
            title=title,
            message=text,
            icon="warning",
            wraplength=500,
            option_1=option["ffmpeg_path"],
            option_2=option["chocolatey"],
            option_3=option["manually"],
        )
        response = msg.get()

        if response == option["ffmpeg_path"]:
            self.settings_tab.ffmpeg_path_select()
        elif response == option["chocolatey"]:
            self.open_link("https://community.chocolatey.org/packages/ffmpeg")
        elif response == option["manually"]:
            self.open_link(
                "https://github.com/EasyTuber/EasyTuber?tab=readme-ov-file#-pr%C3%A9-requisitos"
            )
            
    def open_link(self, url):
        webbrowser.open(url)

    def run(self):
        self.mainloop()