import customtkinter as ctk
from PIL import Image
from CTkToolTip import CTkToolTip

from modules import (
    get_image_path,
    get_thumbnail_img,
)

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ui.settings_tab import SettingsTab
    from interface import MainApplication


class AdvancedTab(ctk.CTkFrame):
    def __init__(
        self,
        master,
        app: "MainApplication",
        translator,
        yt_dlp,
        settings_tab: "SettingsTab",
        **kwargs,
    ):
        super().__init__(master, **kwargs)

        self.translator = translator
        self.yt_dlp = yt_dlp
        self.app = app
        self.settings_tab = settings_tab

        self.format_map = {
            "mp4": ["H.264", "H.265"],
            "mkv": ["H.264", "H.265", "VP9", "AV1"],
            "webm": ["VP9", "AV1"],
            "mov": ["H.264", "H.265"],
            "avi": ["H.264"],
        }
        self.codecs_map = {
            "H.264": "h264",
            "H.265": "h265",
            "VP9": "vp9",
            "AV1": "av1",
        }

        self.advced_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.advced_frame.pack(fill="both", expand=True, pady=5)

        #! Frame de url
        # region URL Entry
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
        # region Botão de Pesquisar
        self.search_button = ctk.CTkButton(
            self.url2_frame,
            text=self.translator.get_text("search"),
            command=self.search,
            width=100,
            font=ctk.CTkFont(size=14),
        )
        self.search_button.grid(row=0, column=2, sticky="w", padx=10)
        # endregion

        #! Frame de Informações
        # region Frame de Informações
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
        # region Thumbnail Image
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

        #! Título e detalhes
        # region Título e Detalhes
        self.info_search_frame = ctk.CTkFrame(
            self.info_frame,
            fg_color="transparent",
        )
        self.info_search_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.info_frame.columnconfigure(1, weight=1)

        self.info_search_frame.grid_propagate(False)

        #! Titulo
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

        #! Linha com canal e visualizações
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

        #! Botão de Download Avançado
        # region Botão de Download
        self.download_advanced_button = ctk.CTkButton(
            self.info_scrollframe,
            text=self.translator.get_text("download_button"),
            command=lambda: self.call_download(),
            width=200,
            font=ctk.CTkFont(size=14),
        )
        self.download_advanced_button.pack(side="top", pady=5)
        self.download_advanced_button.pack_forget()
        # endregion

        #! Frame de Formatos
        # region Frame de Formatos
        self.format_frame = ctk.CTkFrame(
            self.info_scrollframe,
            fg_color=("gray86", "gray20"),
            corner_radius=15,
        )
        self.format_frame.pack(side="top", fill="both", expand=True, padx=5)

        #! Formato Presets
        # region Formato Presets
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
            command=self.format_custom_selected,
            state="disabled",
        )
        self.format_presets_OptionMenu.grid(row=0, column=1, sticky="ew")
        # endregion

        #! Formato Personalizado
        # region Formato Personalizado
        self.format_custom_frame_1 = ctk.CTkFrame(
            self.format_frame, fg_color="transparent"
        )
        self.format_custom_frame_1.pack(
            side="top", expand=True, padx=5, pady=5, fill="x"
        )

        self.format_custom_frame_2 = ctk.CTkFrame(
            self.format_frame, fg_color="transparent"
        )
        self.format_custom_frame_2.pack(side="top", expand=True, padx=5, fill="x")

        #! Tipo de Formato
        # region Tipo de Formato
        self.format_custom_container_frame = ctk.CTkFrame(
            self.format_custom_frame_1, fg_color="transparent"
        )
        self.format_custom_container_frame.pack(side="left", expand=True)

        self.format_custom_container_label = ctk.CTkLabel(
            self.format_custom_container_frame,
            text=self.translator.get_text("format"),
        )
        self.format_custom_container_label.grid(
            row=0, column=0, pady=(0, 1), sticky="ew"
        )

        self.format_custom_container_var = ctk.StringVar(value="mp4")
        self.format_custom_container_OptionMenu = ctk.CTkOptionMenu(
            self.format_custom_container_frame,
            dynamic_resizing=False,
            values=["mp4", "mkv", "webm", "mov", "avi"],
            variable=self.format_custom_container_var,
            width=80,
            state="disabled",
            command=self.format_custom,
        )
        self.format_custom_container_OptionMenu.grid(row=1, column=0, sticky="ew")
        self.format_custom_container_tooltip = CTkToolTip(
            self.format_custom_container_OptionMenu,
            message=self.translator.get_text("format_tooltip"),
            justify="left",
            padding=(10, 10),
            border_width=1,
            x_offset=-50,
            follow=False,
        )
        # endregion

        #! Qualidade do Vídeo
        # region Qualidade do Vídeo
        self.video_quality_frame = ctk.CTkFrame(
            self.format_custom_frame_1, fg_color="transparent"
        )
        self.video_quality_frame.pack(side="left", expand=True)

        self.video_quality_label = ctk.CTkLabel(
            self.video_quality_frame, text=self.translator.get_text("quality")
        )
        self.video_quality_label.grid(row=0, column=0, pady=(0, 1), sticky="ew")
        self.video_quality_var = ctk.StringVar(value=None)
        self.video_quality_OptionMenu = ctk.CTkOptionMenu(
            self.video_quality_frame,
            dynamic_resizing=False,
            values="Best",
            variable=self.video_quality_var,
            width=80,
            state="disabled",
        )
        self.video_quality_OptionMenu.grid(row=1, column=0, sticky="ew")
        # endregion

        #! Codecs de Vídeo
        # region Codecs de Vídeo
        self.video_codec_frame = ctk.CTkFrame(
            self.format_custom_frame_1, fg_color="transparent"
        )
        self.video_codec_frame.pack(side="left", expand=True)

        self.video_codec_label = ctk.CTkLabel(
            self.video_codec_frame, text=self.translator.get_text("video_codec")
        )
        self.video_codec_label.grid(row=0, column=0, pady=(0, 1), sticky="ew")

        self.video_codec_var = ctk.StringVar(value="H.264")
        self.video_codec_OptionMenu = ctk.CTkOptionMenu(
            self.video_codec_frame,
            dynamic_resizing=False,
            values=["H.264", "H.265", "VP9", "AV1"],
            variable=self.video_codec_var,
            width=80,
            state="disabled",
            command=self.codec_selected,
        )
        self.video_codec_OptionMenu.grid(row=1, column=0, sticky="ew")
        self.video_codec_tooltip = CTkToolTip(
            self.video_codec_OptionMenu,
            message=self.translator.get_text("video_codec_tooltip"),
            justify="left",
            padding=(10, 10),
            border_width=1,
            x_offset=-50,
            follow=False,
        )
        # endregion

        #! Codecs de Áudio
        # region Codecs de Áudio
        self.audio_codec_frame = ctk.CTkFrame(
            self.format_custom_frame_1, fg_color="transparent"
        )
        self.audio_codec_frame.pack(side="left", expand=True)
        self.audio_codec_label = ctk.CTkLabel(
            self.audio_codec_frame, text=self.translator.get_text("audio_codec")
        )
        self.audio_codec_label.grid(row=0, column=0, pady=(0, 1), sticky="ew")

        self.audio_codec_var = ctk.StringVar(value="aac")
        self.audio_codec_OptionMenu = ctk.CTkOptionMenu(
            self.audio_codec_frame,
            dynamic_resizing=False,
            values=["aac", "mp3", "opus", "flac"],
            variable=self.audio_codec_var,
            width=80,
            state="disabled",
        )
        self.audio_codec_OptionMenu.grid(row=1, column=0, sticky="ew")
        self.audio_codec_tooltip = CTkToolTip(
            self.audio_codec_OptionMenu,
            message=self.translator.get_text("audio_codec_tooltip"),
            justify="left",
            padding=(10, 10),
            border_width=1,
            x_offset=-50,
            follow=False,
        )
        # endregion

        #! Qualidade de Compressão (CRF)
        # region Qualidade de Compressão (CRF)
        self.compression_quality_frame = ctk.CTkFrame(
            self.format_custom_frame_2, fg_color="transparent"
        )
        self.compression_quality_frame.pack(side="left", expand=True)

        self.compression_quality_label = ctk.CTkLabel(
            self.compression_quality_frame,
            text=self.translator.get_text("compression_quality"),
        )
        self.compression_quality_label.grid(row=0, column=0, pady=(0, 1), sticky="ew")

        self.compression_quality_var = ctk.StringVar(
            value=self.translator.get_text("compression_quality_values")[1]
        )
        self.compression_quality_OptionMenu = ctk.CTkOptionMenu(
            self.compression_quality_frame,
            dynamic_resizing=False,
            values=self.translator.get_text("compression_quality_values"),
            variable=self.compression_quality_var,
            width=80,
            state="disabled",
        )
        self.compression_quality_OptionMenu.grid(row=1, column=0, sticky="ew")

        self.compression_quality_tooltip = CTkToolTip(
            self.compression_quality_OptionMenu,
            message=self.translator.get_text("compression_quality_tooltip"),
            justify="left",
            padding=(10, 10),
            border_width=1,
            x_offset=-50,
            follow=False,
        )
        # endregion

        #! Velocidade de Codificação
        # region Velocidade de Codificação
        self.encoding_speed_frame = ctk.CTkFrame(
            self.format_custom_frame_2, fg_color="transparent"
        )
        self.encoding_speed_frame.pack(side="left", expand=True)
        self.encoding_speed_label = ctk.CTkLabel(
            self.encoding_speed_frame, text=self.translator.get_text("encoding_speed")
        )
        self.encoding_speed_label.grid(row=0, column=0, pady=(0, 1), sticky="ew")
        self.encoding_speed_var = ctk.StringVar(
            value=self.translator.get_text("encoding_speed_values_h264")[2]
        )
        self.encoding_speed_OptionMenu = ctk.CTkOptionMenu(
            self.encoding_speed_frame,
            dynamic_resizing=False,
            values=self.translator.get_text("encoding_speed_values_h264"),
            variable=self.encoding_speed_var,
            width=190,
            state="disabled",
        )
        self.encoding_speed_OptionMenu.grid(row=1, column=0, sticky="ew")
        self.encoding_speed_tooltip = CTkToolTip(
            self.encoding_speed_OptionMenu,
            message=self.translator.get_text("encoding_speed_tooltip"),
            justify="left",
            padding=(10, 10),
            border_width=1,
            x_offset=-50,
            follow=False,
        )
        # endregion

        # endregion

        self.format_frame.pack_forget()
        # endregion

    # region Search
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

            resolucao = sorted(
                {item["resolucao"] for item in self.info_presets},
                reverse=True,
            )

            resolucao_str = [f"{r}p" for r in resolucao]

            self.video_quality_OptionMenu.configure(
                values=resolucao_str,
            )
            self.video_quality_var.set(resolucao_str[0])

        self.yt_dlp.start_search(url, on_complete=on_search_complete)

    # endregion

    def truncate_text(self, text, max_chars=100):
        return text[: max_chars - 3] + "..." if len(text) > max_chars else text

    def format_views(self, count):
        if count >= 1_000_000:
            return f"{count / 1_000_000:.2f}M"
        elif count >= 1_000:
            return f"{count / 1_000:.2f}K"
        else:
            return str(count)

    # region Update Language
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

        self.download_advanced_button.configure(
            text=self.translator.get_text("download_button")
        )

        format_presets_values = self.format_presets_OptionMenu.cget("values")
        if format_presets_values:
            format_presets_values[0] = self.translator.get_text("formats_custom")
            self.format_presets_OptionMenu.configure(values=format_presets_values)

            if self.format_presets_var.get() in self.translator.get_translates(
                "formats_custom"
            ):
                self.format_presets_var.set(self.translator.get_text("formats_custom"))

        self.format_custom_container_label.configure(
            text=self.translator.get_text("format")
        )
        self.format_custom_container_tooltip.configure(
            message=self.translator.get_text("format_tooltip")
        )
        self.video_quality_label.configure(text=self.translator.get_text("quality"))
        self.video_codec_label.configure(text=self.translator.get_text("video_codec"))
        self.video_codec_tooltip.configure(
            message=self.translator.get_text("video_codec_tooltip")
        )
        self.audio_codec_label.configure(text=self.translator.get_text("audio_codec"))
        self.audio_codec_tooltip.configure(
            message=self.translator.get_text("audio_codec_tooltip")
        )
        self.compression_quality_label.configure(
            text=self.translator.get_text("compression_quality")
        )
        self.compression_quality_tooltip.configure(
            message=self.translator.get_text("compression_quality_tooltip")
        )
        self.compression_quality_OptionMenu.configure(
            values=self.translator.get_text("compression_quality_values"),
        )

        compression_quality_value = self.compression_quality_var.get()

        logical_levels = list(
            zip(*self.translator.get_translates("compression_quality_values"))
        )
        index = next(
            (
                i
                for i, group in enumerate(logical_levels)
                if compression_quality_value in group
            ),
            None,
        )
        if index is not None:
            translated_values = self.translator.get_text("compression_quality_values")
            self.compression_quality_var.set(translated_values[index])

        self.encoding_speed_label.configure(
            text=self.translator.get_text("encoding_speed")
        )
        self.encoding_speed_tooltip.configure(
            message=self.translator.get_text("encoding_speed_tooltip")
        )

        codec = self.video_codec_var.get()
        self.encoding_speed_OptionMenu.configure(
            values=self.translator.get_text(
                f"encoding_speed_values_{self.codecs_map[codec]}"
            )
        )

        encoding_speed_value = self.encoding_speed_var.get()
        encoding_speed_values = self.translator.get_translates(
            f"encoding_speed_values_{self.codecs_map[codec]}"
        )

        logical_levels = list(zip(*encoding_speed_values))
        index = next(
            (
                i
                for i, group in enumerate(logical_levels)
                if encoding_speed_value in group
            ),
            None,
        )
        if index is not None:
            translated_values = self.translator.get_text(
                f"encoding_speed_values_{self.codecs_map[codec]}"
            )
            self.encoding_speed_var.set(translated_values[index])

    # region Format Selected
    def format_custom_selected(self, value):
        if value == self.translator.get_text("formats_custom"):
            self.video_quality_OptionMenu.configure(state="normal")
            self.format_custom_container_OptionMenu.configure(state="normal")
            self.video_codec_OptionMenu.configure(state="normal")
            self.audio_codec_OptionMenu.configure(state="normal")
            self.compression_quality_OptionMenu.configure(state="normal")
            self.encoding_speed_OptionMenu.configure(state="normal")

        else:
            self.video_quality_OptionMenu.configure(state="disabled")
            self.format_custom_container_OptionMenu.configure(state="disabled")
            self.video_codec_OptionMenu.configure(state="disabled")
            self.audio_codec_OptionMenu.configure(state="disabled")
            self.compression_quality_OptionMenu.configure(state="disabled")
            self.encoding_speed_OptionMenu.configure(state="disabled")

    # region Codec Selected
    def codec_selected(self, value):

        enconding_speed_values = self.translator.get_text(
            f"encoding_speed_values_{self.codecs_map[value]}"
        )

        self.encoding_speed_OptionMenu.configure(values=enconding_speed_values)
        self.encoding_speed_var.set(
            enconding_speed_values[
                len(enconding_speed_values) // 2
            ]  # Set to the middle value
        )

    def call_download(self):
        self.disable_button()

        if not self.info_preview:
            return

        download_options = {
            "url": self.app.url2_var.get(),
            "download_path": self.settings_tab.default_download_path_entry.get(),
            "ffmpeg_path": self.settings_tab.ffmpeg_path_entry.get(),
        }

        format_desc = self.format_presets_var.get()
        if format_desc == self.translator.get_text("formats_custom"):
            download_options.update(self.get_custom_format_options())

        else:
            format_id = next(
                (
                    item["id"]
                    for item in self.info_presets
                    if item["desc"] == format_desc
                ),
                None,
            )
            if not format_id is None:
                download_options.update(
                    {
                        "format_id": format_id,
                    }
                )

        self.yt_dlp.start_download("advanced", download_options)

    def get_custom_format_options(self):

        codec = self.video_codec_var.get()
        video_codec = self.codecs_map.get(codec, "h264")
        print("Video Codec:", video_codec)

        compression_quality_value = self.compression_quality_var.get()
        compression_quality_values = self.translator.get_translates(
            "compression_quality_values"
        )

        logical_levels = list(zip(*compression_quality_values))
        compression_quality = str(
            next(
                (
                    i
                    for i, group in enumerate(logical_levels)
                    if compression_quality_value in group
                ),
                None,
            )
            + 1
        )  # Adding 1 to match the original code logic

        encoding_speed_value = self.encoding_speed_var.get()
        encoding_speed_values = self.translator.get_translates(
            f"encoding_speed_values_{self.codecs_map[codec]}"
        )

        logical_levels = list(zip(*encoding_speed_values))
        encoding_speed = str(
            next(
                (
                    i
                    for i, group in enumerate(logical_levels)
                    if encoding_speed_value in group
                ),
                None,
            )
        )

        custom_format = {
            "container": self.format_custom_container_var.get(),
            "video_quality": self.video_quality_var.get().replace("p", ""),
            "video_codec": video_codec,
            "audio_codec": self.audio_codec_var.get(),
            "compression_quality": compression_quality,
            "encoding_speed": encoding_speed,
        }

        print("Custom Format Options:", custom_format)
        return {
            "custom_format": custom_format,
        }

    def format_custom(self, value):
        self.video_codec_OptionMenu.configure(values=self.format_map[value])
        self.video_codec_var.set(self.format_map[value][0])

    def restore_button(self):
        self.download_advanced_button.configure(state="normal")
        self.search_button.configure(state="normal")

    def disable_button(self):
        self.download_advanced_button.configure(state="disabled")
        self.search_button.configure(state="disabled")
