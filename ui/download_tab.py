import customtkinter as ctk
from tkinter import filedialog
from CTkMessagebox import CTkMessagebox
from CTkToolTip import CTkToolTip
from PIL import Image
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ui.advanced_tab import AdvancedTab
    from ui.settings_tab import SettingsTab
    from interface import MainApplication

from modules import (
    get_image_path,
    play_sound,
)


class DownloadTab(ctk.CTkFrame):
    def __init__(
        self,
        master,
        app: "MainApplication",
        translator,
        user_prefer,
        yt_dlp,
        default_config,
        advanced_tab: "AdvancedTab",
        settings_tab: "SettingsTab",
        **kwargs
    ):
        super().__init__(master, **kwargs)

        self.translator = translator
        self.user_prefer = user_prefer
        self.yt_dlp = yt_dlp
        self.default_config = default_config
        self.app = app
        self.advanced_tab = advanced_tab
        self.settings_tab = settings_tab

        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, pady=10)

        self.main_frame_top = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.main_frame_top.pack(side="top", fill="both")

        self.main_frame_bottom = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.main_frame_bottom.pack(side="bottom", fill="x")

        # * Frame configuração de download
        self.config_download_frame = ctk.CTkFrame(
            self.main_frame_top, fg_color="transparent"
        )
        self.config_download_frame.pack(side="top", expand=True, fill="x", padx=15)

        self.config_download_frame_top = ctk.CTkFrame(
            self.config_download_frame, fg_color="transparent"
        )
        self.config_download_frame_top.pack(side="top", fill="x")

        self.config_download_frame_bottom = ctk.CTkFrame(
            self.config_download_frame, fg_color="transparent"
        )
        self.config_download_frame_bottom.pack(side="bottom", fill="x")

        #! Tipo de Mídia
        # region Tipo de Mídia
        self.media_frame = ctk.CTkFrame(
            self.config_download_frame_top, fg_color="transparent"
        )
        self.media_frame.pack(side="left", expand=True, padx=5)

        self.media_label = ctk.CTkLabel(
            self.media_frame, text=self.translator.get_text("media_type")
        )
        self.media_label.grid(row=0, column=0, pady=(0, 1), sticky="ew")

        self.media_var = ctk.StringVar(
            value=self.translator.get_text("media_values")[
                self.user_prefer.get("media")
            ]
        )
        self.media_SegButton = ctk.CTkSegmentedButton(
            self.media_frame,
            values=list(self.translator.get_text("media_values").values()),
            variable=self.media_var,
            command=self.media_selected,
        )
        self.media_SegButton.grid(row=1, column=0, sticky="ew")
        # endregion

        #! Formato do arquivo
        # region Formato
        self.formato_frame = ctk.CTkFrame(
            self.config_download_frame_top, fg_color="transparent"
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
            self.config_download_frame_top, fg_color="transparent"
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

        #! Playlist
        # region Playlist

        self.playlist_check_var = ctk.BooleanVar(value=False)
        self.playlist_check = ctk.CTkCheckBox(
            self.config_download_frame_bottom,
            text=self.translator.get_text("playlist"),
            width=1,
            variable=self.playlist_check_var,
            onvalue=True,
            offvalue=False,
            command=self.toggle_playlist_options,
        )
        self.playlist_check.pack(side="top", pady=(10, 5))

        self.playlist_check_tooltip = CTkToolTip(
            self.playlist_check,
            justify="left",
            padding=(10, 10),
            border_width=1,
            x_offset=-50,
            follow=False,
            message=self.translator.get_text("playlist_check_tooltip"),
        )

        self.playlist_options_frame = ctk.CTkFrame(
            self.config_download_frame_bottom,
            fg_color="transparent",
            border_width=2,
            border_color=("#D03434", "#A11D1D"),
            corner_radius=10,
        )
        self.playlist_options_frame.pack(side="top", fill="x", expand=True)

        # Playlist Items
        self.playlist_items_frame = ctk.CTkFrame(
            self.playlist_options_frame, fg_color="transparent"
        )
        self.playlist_items_frame.pack(side="left", expand=True)

        self.playlist_items_label = ctk.CTkLabel(
            self.playlist_items_frame, text=self.translator.get_text("playlist_items")
        )
        self.playlist_items_label.pack(side="left", padx=(0, 5))

        self.playlist_items_entry = ctk.CTkEntry(
            self.playlist_items_frame,
            width=100,
            placeholder_text=self.translator.get_text("playlist_placeholder"),
        )
        self.playlist_items_entry.pack(side="left")

        self.playlist_items_tooltip = CTkToolTip(
            self.playlist_items_entry,
            message=self.translator.get_text("playlist_items_tooltip"),
            justify="left",
            padding=(10, 10),
            border_width=1,
            x_offset=-70,
            follow=False,
        )

        # Playlist Reverse
        self.playlist_reverse_var = ctk.BooleanVar(value=False)
        self.playlist_reverse_check = ctk.CTkCheckBox(
            self.playlist_options_frame,
            text=self.translator.get_text("playlist_reverse"),
            variable=self.playlist_reverse_var,
            command=self.toggle_playlist_reverse,
            onvalue=True,
            offvalue=False,
        )
        self.playlist_reverse_check.pack(side="left", expand=True)

        self.playlist_reverse_tooltip = CTkToolTip(
            self.playlist_reverse_check,
            message=self.translator.get_text("playlist_reverse_tooltip"),
            justify="left",
            padding=(10, 10),
            border_width=1,
            x_offset=-50,
            follow=False,
        )

        # Playlist Random
        self.playlist_random_var = ctk.BooleanVar(value=False)
        self.playlist_random_check = ctk.CTkCheckBox(
            self.playlist_options_frame,
            text=self.translator.get_text("playlist_random"),
            variable=self.playlist_random_var,
            command=self.toggle_playlist_random,
            onvalue=True,
            offvalue=False,
        )
        self.playlist_random_check.pack(side="left", expand=True)

        self.playlist_random_tooltip = CTkToolTip(
            self.playlist_random_check,
            message=self.translator.get_text("playlist_random_tooltip"),
            justify="left",
            padding=(10, 10),
            border_width=1,
            x_offset=-50,
            follow=False,
        )

        # Inicialmente esconde as opções
        self.playlist_options_frame.pack_forget()
        # endregion

        #! Frame de url
        # region URL entry
        self.url1_frame = ctk.CTkFrame(self.main_frame_top, fg_color="transparent")
        self.url1_frame.pack(
            side="top", fill="x", expand=True, ipadx=5, ipady=5, padx=15, pady=10
        )
        self.url1_frame.columnconfigure(1, weight=1)

        self.url1_label = ctk.CTkLabel(self.url1_frame, text="Url:", font=("Arial", 14))
        self.url1_label.grid(row=0, column=0, sticky="e", padx=(0, 10))

        self.url1_entry = ctk.CTkEntry(
            self.url1_frame,
            textvariable=self.app.url1_var,
            placeholder_text=self.translator.get_text("url_placeholder"),
        )
        self.url1_entry.grid(row=0, column=1, sticky="nsew")
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
            pady=(0, 5),
            padx=10,
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

    def call_download(self, type: str):
        self.disable_button()

        if not self.app.check_errors(self.url1_entry.get(), "basic", self):
            return
        else:
            download_options = {
                "url": self.url1_entry.get(),
                "download_path": self.download_path_entry.get(),
                "ffmpeg_path": self.settings_tab.ffmpeg_path_entry.get(),
            }
            download_options.update(
                {
                    "media": self.media_var.get(),
                    "format": self.formato_var.get(),
                    "quality": self.qualidade_var.get().replace("p", ""),
                    "playlist": self.playlist_check_var.get(),
                    "playlist_items": (
                        self.playlist_items_entry.get()
                        if self.playlist_check_var.get()
                        else ""
                    ),
                    "playlist_reverse": bool(self.playlist_reverse_var.get()),
                    "playlist_random": bool(self.playlist_random_var.get()),
                }
            )
            self.yt_dlp.start_download(type, download_options)

    def media_selected(self, valor, init=False):
        if valor == self.translator.get_text("video"):
            self.formato_OptionMenu.configure(values=self.default_config.FORMAT_VIDEOS)
            self.qualidade_menu.configure(state="normal")
            if not init:
                self.user_prefer.set("last_format_audio", self.formato_var.get())
                self.formato_var.set(self.user_prefer.get("last_format_video"))
        elif valor == self.translator.get_text("audio"):
            self.formato_OptionMenu.configure(values=self.default_config.FORMAT_AUDIOS)
            self.qualidade_menu.configure(state="disabled")
            if not init:
                self.user_prefer.set("last_format_video", self.formato_var.get())
                self.formato_var.set(self.user_prefer.get("last_format_audio"))

    def toggle_playlist_options(self):
        """Controla a visibilidade das opções avançadas de playlist"""
        if self.playlist_check_var.get():
            self.playlist_options_frame.pack(
                side="top", fill="x", expand=True, ipadx=5, ipady=5
            )
        else:
            self.playlist_options_frame.pack_forget()

    def toggle_playlist_reverse(self):
        if self.playlist_reverse_var.get():
            self.playlist_random_check.configure(
                state="disabled", border_color=["#A7B4B9", "#55595D"]
            )
        else:
            self.playlist_random_check.configure(
                state="normal", border_color=["#3E454A", "#949A9F"]
            )

    def toggle_playlist_random(self):
        if self.playlist_random_var.get():
            self.playlist_reverse_check.configure(
                state="disabled", border_color=["#A7B4B9", "#55595D"]
            )
        else:
            self.playlist_reverse_check.configure(
                state="normal", border_color=["#3E454A", "#949A9F"]
            )

    def reset_download_path(self):
        path = self.settings_tab.default_download_path_entry.get()
        self.download_path_entry.delete(0, "end")
        self.download_path_entry.insert(0, path)

    # region Update Language
    def update_language(self):
        self.playlist_check.configure(text=self.translator.get_text("playlist"))
        self.playlist_check_tooltip.configure(
            message=self.translator.get_text("playlist_check_tooltip")
        )
        self.playlist_items_label.configure(
            text=self.translator.get_text("playlist_items")
        )
        self.playlist_items_entry.configure(
            placeholder_text=self.translator.get_text("playlist_placeholder")
        )
        self.playlist_reverse_check.configure(
            text=self.translator.get_text("playlist_reverse")
        )
        self.playlist_random_check.configure(
            text=self.translator.get_text("playlist_random")
        )
        self.playlist_items_tooltip.configure(
            message=self.translator.get_text("playlist_items_tooltip")
        )
        self.playlist_reverse_tooltip.configure(
            message=self.translator.get_text("playlist_reverse_tooltip")
        )
        self.playlist_random_tooltip.configure(
            message=self.translator.get_text("playlist_random_tooltip")
        )

        self.media_label.configure(text=self.translator.get_text("media_type"))

        self.media_var.set(
            self.translator.get_text("media_values")[self.user_prefer.get("media")]
        )
        self.media_SegButton.configure(
            values=list(self.translator.get_text("media_values").values())
        )
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

    def restore_button(self):
        self.download_button.configure(state="normal")

    def disable_button(self):
        self.download_button.configure(state="disabled")
