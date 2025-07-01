import customtkinter as ctk
from tkinter import filedialog
from CTkMessagebox import CTkMessagebox
from CTkToolTip import CTkToolTip

from modules import (
    get_ffmpeg_path,
)


class SettingsTab(ctk.CTkFrame):
    def __init__(self, master, app, translator, user_prefer, **kwargs):
        super().__init__(master, **kwargs)

        self.translator = translator
        self.user_prefer = user_prefer
        self.app = app

        self.settings_frame = ctk.CTkFrame(self, fg_color="transparent")
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

        self.appearance_var = ctk.StringVar(
            value=self.translator.get_text("appearance_values")[
                self.user_prefer.get("appearance")
            ]
        )

        self.appearance_dropdown = ctk.CTkOptionMenu(
            self.appearance_frame,
            values=list(self.translator.get_text("appearance_values").values()),
            variable=self.appearance_var,
            command=lambda choice: ctk.set_appearance_mode(
                self.translator.get_key_by_value(
                    self.translator.get_text("appearance_values"), choice
                )
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

        self.available_languages = self.app.available_languages

        self.language_var = ctk.StringVar(
            value=self.available_languages[self.user_prefer.get("language")]
        )

        self.language_dropdown = ctk.CTkOptionMenu(
            self.language_frame,
            values=sorted(list(self.available_languages.values())),
            variable=self.language_var,
            command=self.app.change_language,
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
        self.sound_notification_tooltip = CTkToolTip(
            self.sound_notification_checkbox,
            justify="left",
            padding=(10, 10),
            border_width=1,
            x_offset=-50,
            follow=False,
            message=self.translator.get_text("sound_notification_tooltip"),
        )

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

        self.open_folder_tooltip = CTkToolTip(
            self.open_folder_checkbox,
            justify="left",
            padding=(10, 10),
            border_width=1,
            x_offset=-50,
            follow=False,
            message=self.translator.get_text("check_open_folder_tooltip"),
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
            message=self.translator.get_text("check_notify_completed_tooltip"),
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
                self.app.after(10, self.app.ffmpeg_popup)
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
            command=lambda: self.app.download_path_select(self.default_download_path_entry),
        )
        self.default_download_path_button.pack(side="left")
        # endregion

        #! Botão de Reset
        # region Reset Button
        self.reset_settings_button = ctk.CTkButton(
            self.settings_frame_bottom,
            text=self.translator.get_text("reset_settings"),
            command=self.reset_settings,
            width=200,
            font=ctk.CTkFont(size=14),
        )
        self.reset_settings_button.pack(side="bottom", pady=10)
        # endregion

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

    def reset_settings(self):
        """Reseta todas as configurações para os valores padrão"""
        title = self.translator.get_text("popup_reset_title")
        message = self.translator.get_text("popup_reset_msg")
        option = list(self.translator.get_text("popup_reset_options").keys())

        msg = CTkMessagebox(
            width=440,
            title=title,
            message=message,
            icon="warning",
            wraplength=360,
            option_1=option[0],
            option_2=option[1],
        )
        response = msg.get()

        if response == option[0]:
            # Resetar todas as configurações para o padrão
            self.save_current_settings()
            self.user_prefer.reset_preferences(self.translator)

            # Atualizar a interface com os valores padrão
            self.app.media_var.set(
                self.translator.get_text("media_values")[self.user_prefer.get("media")]
            )
            self.app.formato_var.set(self.user_prefer.get("format"))
            self.app.qualidade_var.set(self.user_prefer.get("quality"))
            self.appearance_var.set(
                self.translator.get_text("appearance_values")[
                    self.user_prefer.get("appearance")
                ]
            )
            self.language_var.set(
                self.available_languages[self.user_prefer.get("language")]
            )
            self.sound_notification_var.set(self.user_prefer.get("sound_notification"))
            self.clear_url_var.set(self.user_prefer.get("clear_url"))
            self.open_folder_var.set(self.user_prefer.get("open_folder"))
            self.notify_completed_var.set(self.user_prefer.get("notify_completed"))

            # Atualizar os caminhos
            self.ffmpeg_path_entry.delete(0, "end")
            ffmpeg_path = get_ffmpeg_path()
            if ffmpeg_path:
                self.ffmpeg_path_entry.insert(0, ffmpeg_path.replace("\\", "/"))

            self.default_download_path_entry.delete(0, "end")
            self.default_download_path_entry.insert(
                0, self.user_prefer.get("default_download_path")
            )

            self.download_path_entry.delete(0, "end")
            self.download_path_entry.insert(
                0, self.user_prefer.get("default_download_path")
            )

            # Atualizar aparência
            ctk.set_appearance_mode(self.user_prefer.get("appearance"))

            # Mostrar mensagem de sucesso após um pequeno delay
            self.after(
                100,
                lambda: self.show_checkmark(self.translator.get_text("reset_success")),
            )

    def update_language(self):
        self.language_label.configure(text=self.translator.get_text("language") + ":")
        self.appearance_label.configure(
            text=self.translator.get_text("appearance") + ":"
        )
        self.appearance_dropdown.configure(
            values=list(self.translator.get_text("appearance_values").values())
        )

        self.appearance_var.set(
            self.translator.get_text("appearance_values")[
                self.user_prefer.get("appearance")
            ]
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
        self.open_folder_tooltip.configure(
            message=self.translator.get_text("check_open_folder_tooltip")
        )
        self.notify_completed_checkbox.configure(
            text=self.translator.get_text("check_notify_completed")
        )
        self.notify_completed_tooltip.configure(
            message=self.translator.get_text("check_notify_completed_tooltip")
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

        self.reset_settings_button.configure(
            text=self.translator.get_text("reset_settings")
        )
