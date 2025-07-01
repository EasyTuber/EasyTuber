
import customtkinter as ctk
from PIL import Image
import webbrowser

from modules import (
    get_image_path,
)

class AboutTab(ctk.CTkFrame):
    def __init__(self, master, app, translator, default_config, **kwargs):
        super().__init__(master, **kwargs)

        self.translator = translator
        self.default_config = default_config
        self.app = app
        
        self.about_frame = ctk.CTkFrame(self, fg_color="transparent")
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
        # endregion

        #! Versão
        # region VERSÃO
        self.version_label = ctk.CTkLabel(
            self.about_frame_top,
            text=self.translator.get_text("version").format(
                version=self.default_config.APP_VERSION
            ),
            font=ctk.CTkFont(size=14),
        )
        self.version_label.pack(side="top", pady=(20, 5))
        # endregion

        #! Links
        # region Links
        self.github_button = ctk.CTkButton(
            self.about_frame_top,
            text="GitHub",
            command=lambda: self.open_link(self.default_config.APP_WEBSITE),
            width=120,
            font=ctk.CTkFont(size=13),
        )
        self.github_button.pack(side="top", pady=5)
        # endregion

        #! Ferramentas
        # region Ferramentas
        self.tools_label = ctk.CTkLabel(
            self.about_frame_top,
            text=self.translator.get_text("tools"),
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.tools_label.pack(side="top", pady=(20, 5))

        #! Principais
        # region Principais
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
        # endregion

        #! Componentes
        # region Componentes
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
        # endregion
        # endregion
        
    def open_link(self, url):
        webbrowser.open(url)

    def update_language(self):
        self.dev_label.configure(text=self.translator.get_text("developed_by"))
        self.version_label.configure(
            text=self.translator.get_text("version").format(
                version=self.default_config.APP_VERSION
            )
        )
        self.tools_label.configure(text=self.translator.get_text("tools"))
