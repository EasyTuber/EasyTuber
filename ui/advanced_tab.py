
import customtkinter as ctk
from PIL import Image

from modules import (
    get_image_path,
    get_thumbnail_img,
)

class AdvancedTab(ctk.CTkFrame):
    def __init__(self, master, app, translator, yt_dlp, **kwargs):
        super().__init__(master, **kwargs)

        self.translator = translator
        self.yt_dlp = yt_dlp
        self.app = app
        
        self.advced_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.advced_frame.pack(fill="both", expand=True, pady=10)

        #! Frame de url
        # region
        self.url2_frame = ctk.CTkFrame(self.advced_frame, fg_color="transparent")
        self.url2_frame.pack(side="top", fill="x", expand=True, ipadx=5, padx=15)
        self.url2_frame.columnconfigure(1, weight=1)

        self.url2_label = ctk.CTkLabel(self.url2_frame, text="Url:", font=("Arial", 14))
        self.url2_label.grid(row=0, column=0, sticky="e", padx=10)

        self.url2_entry = ctk.CTkEntry(
            self.url2_frame,
            textvariable=self.app.url2_var,
            placeholder_text=self.translator.get_text("url_placeholder"),
        )
        self.url2_entry.grid(row=0, column=1, sticky="nsew")
        # endregion

        #! Botão de Pesquisar
        # region
        self.search_button = ctk.CTkButton(
            self.url2_frame,
            text=self.translator.get_text("search"),
            command=self.search,
            width=100,
            font=ctk.CTkFont(size=14),
        )
        self.search_button.grid(row=0, column=2, sticky="w", padx=10)
        # endregion

        self.info_scrollframe = ctk.CTkScrollableFrame(
            self.advced_frame,
            fg_color="transparent",
        )
        self.info_scrollframe.pack(
            side="top",
            fill="both",
            expand=True,
            padx=10,
        )

        # region Informações da url
        self.info_frame = ctk.CTkFrame(
            self.info_scrollframe,
            fg_color=("gray86", "gray20"),
            corner_radius=15,
            height=110,
        )
        self.info_frame.pack(
            side="top",
            fill="x",
            expand=True,
            padx=5,
        )
        self.info_frame.pack_propagate(False)

        #! Thumbnail image
        # region
        self.thumbnail_frame = ctk.CTkFrame(
            self.info_frame,
            fg_color="transparent",
            width=160,
            height=90,
        )
        self.thumbnail_frame.grid(row=0, column=0, padx=(10, 0), pady=10, sticky="w")
        self.thumbnail_frame.grid_propagate(False)

        self.default_thumbnail = Image.open(get_image_path("photo_icon.png"))
        self.thumbnail_img = ctk.CTkImage(self.default_thumbnail, size=(160, 90))

        self.thumbnail_label = ctk.CTkLabel(
            self.thumbnail_frame,
            text="",
            image=self.thumbnail_img,
        )
        self.thumbnail_label.place(relx=0.5, rely=0.5, anchor="center")

        # endregion

        #! Texto e detalhes
        self.info_search_frame = ctk.CTkFrame(
            self.info_frame,
            fg_color="transparent",
        )
        self.info_search_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.info_frame.columnconfigure(1, weight=1)

        self.info_search_frame.grid_propagate(False)

        # Titulo
        self.details_search_frame = ctk.CTkFrame(
            self.info_search_frame,
            fg_color="transparent",
        )
        self.details_search_frame.pack(expand=True, fill="both")

        self.details_title_label = ctk.CTkLabel(
            self.details_search_frame,
            text=self.translator.get_text("search_title"),
            font=ctk.CTkFont(weight="bold"),
            wraplength=420,
            justify="left",
            anchor="w",
        )
        self.details_title_label.pack(side="top", fill="x", anchor="w")

        # Linha com canal e visualizações
        self.channel_and_views_frame = ctk.CTkFrame(
            self.details_search_frame,
            fg_color="transparent",
        )
        self.channel_and_views_frame.pack(side="top", fill="x", pady=(2, 0))

        self.details_channel_label = ctk.CTkLabel(
            self.channel_and_views_frame,
            text=self.translator.get_text("search_channel"),
            anchor="w",
        )
        self.details_channel_label.pack(side="left", fill="x", expand=True)

        self.view_icon = ctk.CTkImage(
            light_image=Image.open(get_image_path("view_light.png")),
            dark_image=Image.open(get_image_path("view_dark.png")),
            size=(16, 16),
        )

        self.details_view_label = ctk.CTkLabel(
            self.channel_and_views_frame,
            text="0 ",
            anchor="e",
            image=self.view_icon,
            compound="right",
        )
        self.details_view_label.pack(side="right")
        # endregion
        
        
        self.download_advanced_button = ctk.CTkButton(
            self.info_scrollframe,
            text=self.translator.get_text("download_button"),
            command=lambda: self.call_download("advanced"),
            width=200,
            font=ctk.CTkFont(size=14),
        )
        self.download_advanced_button.pack(side="top", pady=(10, 5))
        self.download_advanced_button.pack_forget()

        self.format_frame = ctk.CTkFrame(
            self.info_scrollframe,
            fg_color=("gray86", "gray20"),
            corner_radius=15,
        )
        self.format_frame.pack(side="top", fill="both", expand=True, padx=5, pady=5)

        self.format_presets_frame = ctk.CTkFrame(
            self.format_frame, fg_color="transparent"
        )
        self.format_presets_frame.pack(side="top", expand=True, padx=5, pady=5)

        self.format_presets_label = ctk.CTkLabel(
            self.format_presets_frame, text=self.translator.get_text("formats_detected")
        )
        self.format_presets_label.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        self.format_presets_var = ctk.StringVar(value=None)
        self.format_presets_OptionMenu = ctk.CTkOptionMenu(
            self.format_presets_frame,
            dynamic_resizing=False,
            values="",
            variable=self.format_presets_var,
            width=180,
            state="disabled",
        )
        self.format_presets_OptionMenu.grid(row=0, column=1, sticky="ew")
        
        self.format_frame.pack_forget()
        
    def search(self):
        self.info_preview = {}
        self.info_presets = {}
        self.audio_id = None

        url = self.app.url2_var.get()

        def on_search_complete():
            self.info_preview = self.yt_dlp.info_preview
            self.info_presets = self.yt_dlp.info_presets
            self.audio_id = self.yt_dlp.audio_id

            thumbnail_url = self.info_preview["thumbnail_url"]
            duration_url = self.info_preview["duration"]

            if thumbnail_url in "youtube":
                thumbnail_url = f"https://img.youtube.com/vi/{thumbnail_url.split("?v=", 1)[1]}/mqdefault.jpg"

            self.thumbnail_img.configure(
                light_image=get_thumbnail_img(thumbnail_url, duration_url)
            )

            titulo = self.truncate_text(self.info_preview["title"])

            self.details_title_label.configure(text=titulo)
            self.details_channel_label.configure(text=self.info_preview["uploader"])

            view_count = self.format_views(self.info_preview["view_count"])
            self.details_view_label.configure(text=f"{view_count} ")

            desc_list = [self.translator.get_text("formats_custom")] + [
                item["desc"] for item in self.info_presets
            ]
            self.format_presets_OptionMenu.configure(
                values=desc_list,
                state="normal",
            )
            self.format_presets_var.set(desc_list[1])
            
            self.download_advanced_button.pack(side="top", pady=(10, 5))
            self.format_frame.pack(side="top", fill="both", expand=True, padx=5, pady=5)

        self.yt_dlp.start_search(url, on_complete=on_search_complete)
        
    def truncate_text(self, text, max_chars=100):
        return text[: max_chars - 3] + "..." if len(text) > max_chars else text

    def format_views(self, count):
        if count >= 1_000_000:
            return f"{count / 1_000_000:.2f}M"
        elif count >= 1_000:
            return f"{count / 1_000:.2f}K"
        else:
            return str(count)

    def update_language(self):
        self.search_button.configure(text=self.translator.get_text("search"))

        if self.details_title_label.cget("text") in self.translator.get_translates(
            "search_title"
        ):
            self.details_title_label.configure(
                text=self.translator.get_text("search_title")
            )

        if self.details_channel_label.cget("text") in self.translator.get_translates(
            "search_channel"
        ):
            self.details_channel_label.configure(
                text=self.translator.get_text("search_channel")
            )

        self.format_presets_label.configure(
            text=self.translator.get_text("formats_detected")
        )
        
        self.download_advanced_button.configure(text=self.translator.get_text("download_button"))

        format_presets_values = self.format_presets_OptionMenu.cget("values")
        if format_presets_values:
            format_presets_values[0] = self.translator.get_text("formats_custom")
            self.format_presets_OptionMenu.configure(values=format_presets_values)

            if self.format_presets_var.get() in self.translator.get_translates(
                "formats_custom"
            ):
                self.format_presets_var.set(self.translator.get_text("formats_custom"))
