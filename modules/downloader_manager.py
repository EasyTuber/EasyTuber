import os
from yt_dlp import YoutubeDL
import threading
from modules.utils import get_ffmpeg_path, play_sound
from libs import CTkProgressPopup


class YoutubeDownloader:
    def __init__(self, root):

        self.root = root
        self.translator = root.translator
        self.ydl_opts = {}
        self.resolutions_available = set()
        self.info = []
        self.resolutions_list = []
        self.options_ydlp = {}
        self.url = ""
        self.progress_popup = None

        # Flag para controlar o cancelamento
        self.cancel_download = threading.Event()
        self.download_thread = None

    def start_download(self):
        # Janela para mostrar o donwload
        self.progress_popup = None
        self.progress_popup = CTkProgressPopup(
            master=self.root,
            title=self.translator.get_text("downloading"),
            label=self.translator.get_text("status")[1],
            message="",
            side="right_bottom",
        )

        # Reset da flag de cancelamento
        self.cancel_download.clear()

        # Inicia o download em uma thread separada
        self.download_thread = threading.Thread(
            target=self.download_process, daemon=True
        )
        self.download_thread.start()

    def download_process(self):
        try:
            self.config_options()
            url = self.options_ydlp["url"]

            with YoutubeDL(self.ydl_opts) as ydl:
                # Injetar verificação de cancelamento
                original_sanitize_info = ydl.sanitize_info

                def patched_sanitize_info(info_dict, remove_private=True):
                    if self.cancel_download.is_set():
                        raise Exception("Download cancelado pelo usuário")
                    return original_sanitize_info(info_dict, remove_private)

                ydl.sanitize_info = patched_sanitize_info

                ydl.download([url])

            # Se chegou aqui, o download foi concluído
            if not self.cancel_download.is_set():
                # TODO dps criar o update after download para mandar aviso de concluido
                self.update_ui_after_download(success=True)
        except Exception as e:
            # Verificar se foi um cancelamento intencional
            if "cancelado pelo usuário" in str(e):
                pass
                # self.update_ui_after_download(cancelled=True)
            else:
                print(f"Erro durante o download: {e}")
                # self.update_ui_after_download(success=False, error=str(e))

    def config_options(self):
        self.ydl_opts.clear()
        self.options_ydlp.clear()
        self.options_ydlp = {
            "url": self.root.url1_var.get(),
            "media": self.root.media_var.get(),
            "formato": self.root.formato_var.get(),
            "playlist": self.root.playlist_check_var.get(),
            "playlist_items": self.root.playlist_entry.get(),
            "qualidade": self.root.qualidade_var.get().replace("p", ""),
            "download_path": self.root.download_path_entry.get(),
            "ffmpeg_path": self.root.ffmpeg_path_entry.get(),
        }

        # Configurações base comuns
        self.ydl_opts = {
            "progress_hooks": [self.progress_hooks],
            "postprocessor_hooks": [self.check_cancel_hook],
            "ffmpeg_location": self.options_ydlp["ffmpeg_path"],
        }

        # Configurações específicas para playlist
        if self.options_ydlp["playlist"]:
            self.ydl_opts.update(
                {
                    "outtmpl": os.path.join(
                        self.options_ydlp["download_path"],
                        "%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s",
                    ),  # Cria pasta com nome da playlist # TODO colocar como opcional
                    "ignoreerrors": True,  # Continua mesmo se um vídeo falhar
                    "playlist": True,
                    "yes_playlist": True,
                }
            )
            # Se especificado os itens da playlist
            if self.options_ydlp["playlist_items"]:
                self.ydl_opts["playlist_items"] = self.options_ydlp["playlist_items"]
        else:
            self.ydl_opts["outtmpl"] = os.path.join(
                self.options_ydlp["download_path"], "%(title)s.%(ext)s"
            )

        # Se é audio
        if self.options_ydlp["media"] in self.root.localized_audio:
            self.ydl_opts.update(
                {
                    "format": "bestaudio/best",
                    "postprocessors": [
                        {
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": self.options_ydlp["formato"],
                            "preferredquality": "192",
                        }
                    ],
                }
            )
        else:  # Se é video
            # TODO depois colocar um if para pegar das opções avançadas
            # TODO colocar o marge to format para mudar o formati
            self.ydl_opts.update(
                {
                    "format": f"bestvideo[ext={self.options_ydlp["formato"]}][height<={self.options_ydlp["qualidade"]}]+bestaudio[ext=m4a]/best[ext={self.options_ydlp["formato"]}][height<={self.options_ydlp["qualidade"]}]/best[height<={self.options_ydlp["qualidade"]}]/best",
                }
            )

    def check_cancel_hook(self, d):
        if self.cancel_download.is_set():
            raise Exception("Download cancelado pelo usuário")

    # Atualiza a barra de progresso e o status de download
    def progress_hooks(self, d):

        if self.cancel_download.is_set():
            raise Exception("Download cancelado pelo usuário")

        info_dict = d.get("info_dict", {})
        playlist_index = info_dict.get("playlist_index")
        playlist_count = info_dict.get("n_entries")

        if d["status"] == "downloading":
            try:
                if playlist_index is not None and playlist_count is not None:
                    self.progress_popup.update_label(
                        self.translator.get_text("status")[6].format(
                            index=playlist_index, count=playlist_count
                        )
                    )
                else:
                    self.progress_popup.update_label(
                        self.translator.get_text("status")[5]
                    )
                # Obtém o total de bytes
                total_bytes = d.get("total_bytes")

                # Se total_bytes não estiver disponível, tenta total_bytes_estimate
                if total_bytes is None:
                    total_bytes = d.get("total_bytes_estimate", 0)

                # Obtém os bytes baixados
                downloaded_bytes = d.get("downloaded_bytes", 0)

                # Calcula a porcentagem
                if total_bytes > 0:
                    percentage = downloaded_bytes / total_bytes
                    # Atualiza a barra de progresso
                    self.progress_popup.update_progress(percentage)

                    # Calcula velocidade em MB/s
                    speed = d.get("speed", 0)
                    if speed:
                        speed_mb = speed / 1024 / 1024  # Converte para MB/s

                        # Calcula tempo restante
                        eta = d.get("eta", 0)
                        if eta:
                            eta_min = eta // 60
                            eta_sec = eta % 60

                            # Atualiza o texto de status com todas as informações
                            status_text = self.translator.get_text(
                                "downloading_progress"
                            )[0].format(
                                percent=f"{percentage:.1%}",
                                speed=f"{speed_mb:.1f}",
                                eta_min=f"{eta_min:.0f}",
                                eta_sec=f"{eta_sec:.0f}",
                            )
                        else:
                            status_text = self.translator.get_text(
                                "downloading_progress"
                            )[1].format(
                                percent=f"{percentage:.1%}", speed=f"{speed_mb:.1f}"
                            )
                    else:
                        status_text = self.translator.get_text("downloading_progress")[
                            2
                        ].format(percent=f"{percentage:.1%}")

                    self.progress_popup.update_message(status_text)

                self.root.update_idletasks()
            except Exception as e:
                # TODO ver isso aqui
                print(f"Erro ao atualizar progresso: {str(e)}")
                pass

        elif d["status"] == "finished":
            if playlist_index is not None and playlist_count is not None:
                self.progress_popup.update_label(
                    self.translator.get_text("status")[7].format(
                        index=playlist_index, count=playlist_count
                    )
                )
            else:
                self.progress_popup.update_label(self.translator.get_text("status")[2])

            self.progress_popup.update_progress(1)

        elif d["status"] == "error":
            # TODO configurar caso erro
            self.progress_popup.update_label(self.translator.get_text("status")[3])
            self.progress_popup.update_progress(0)
            self.root.download_button.configure(state="normal")
            self.root.after(1000, lambda: self.progress_popup.cancel_task())

    # TODO configurar o que acontece depois de concluido
    def update_ui_after_download(self, success=False, cancelled=False, error=None):
        # Executa na thread principal
        def update():
            if cancelled:
                # self.status_label.configure(text="Download cancelado")
                pass
            elif success:
                self.progress_popup.close_progress_popup()
                # Resetar a variavel
                if self.root.clear_url_var.get():
                    print("Limpar url")
                    self.root.url1_var.set("")
                if self.root.open_folder_var.get():
                    print("Abrir pasta")
                    os.startfile(os.path.realpath(self.options_ydlp["download_path"]))
                if self.root.notify_completed_var.get():
                    if self.root.sound_notification_var.get():
                        play_sound(True)
                    self.root.show_checkmark(self.translator.get_text("success")[0])
                    pass

            else:
                self.progress_popup.close_progress_popup()
                # self.status_label.configure(text=f"Erro: {error}")

            self.progress_popup = None
            self.root.restore_button()

        self.root.after(0, update)
