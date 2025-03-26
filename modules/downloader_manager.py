import os
from yt_dlp import YoutubeDL
import threading
from modules.utils import get_ffmpeg_path, play_sound
from libs import CTkProgressPopup, CTkNotification


class YoutubeDownloader:
    def __init__(self, root):
        """
        Initializes the YouTube download manager

        Parameters
        ----------
        root : ctk.CTk
            The main application window
        """
        self.root = root
        self.translator = root.translator
        self.ydl_opts = {}
        self.resolutions_available = set()
        self.info = []
        self.resolutions_list = []
        self.options_ydlp = {}
        self.url = ""
        self.progress_popup = None
        self.type_download = None

        # Flag para controlar o cancelamento
        self.cancel_download = threading.Event()
        self.download_thread = None

    def start_download(self, type: str):

        self.type_download = type

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
                        raise Exception("download cancelled")
                    return original_sanitize_info(info_dict, remove_private)

                ydl.sanitize_info = patched_sanitize_info

                ydl.download([url])

            # Se chegou aqui, o download foi concluído
            if not self.cancel_download.is_set():
                self.update_ui_after_download(success=True)
        except Exception as e:
            # Verificar se foi um cancelamento intencional
            if "download cancelled" in str(e):
                self.update_ui_after_download(cancelled=True)
                self.cleanup_partial_downloads()
            else:
                self.update_ui_after_download(success=False, error=str(e))

    def config_options(self):
        self.ydl_opts.clear()
        self.options_ydlp.clear()

        self.options_ydlp = self.root.download_options

        # Configurações base comuns
        self.ydl_opts = {
            "progress_hooks": [self.progress_hooks],
            "postprocessor_hooks": [self.postprocessor_hook],
            "ffmpeg_location": self.options_ydlp["ffmpeg_path"],
        }

        # TODO Configurações específicas para playlist
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
                            "preferredcodec": self.options_ydlp["format"],
                            "preferredquality": "192",
                        }
                    ],
                }
            )
        else:  # Se é video
            # TODO depois colocar um if para pegar das opções avançadas
            self.ydl_opts.update(
                {
                    "format": f'bestvideo[height<={self.options_ydlp["quality"]}]+bestaudio/best[height<={self.options_ydlp["quality"]}]',
                    "merge_output_format": self.options_ydlp["format"],
                }
            )

    def postprocessor_hook(self, d):
        if self.cancel_download.is_set():
            raise Exception("download cancelled")

        # TODO: atualizar a interface
        if d["status"] == "started":
            print(
                f"Iniciando pós-processamento: {d.get('postprocessor', 'desconhecido')}"
            )
        elif d["status"] == "processing":
            print(f"Processando arquivo {d.get('filename')}")
        elif d["status"] == "finished":
            print(f"Pós-processamento concluído: {d.get('filename')}")
            print(f"Tipo: {d.get('postprocessor')}")
            print(f"Tamanho final: {d.get('filesize', 'desconhecido')} bytes")
        elif d["status"] == "error":
            print(f"Erro no pós-processamento: {d.get('error')}")

    # Atualiza a barra de progresso e o status de download
    def progress_hooks(self, d):

        if self.cancel_download.is_set():
            raise Exception("download cancelled")

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
                CTkNotification(
                    master=self.root,
                    state="info",
                    message=self.translator.get_text("download_cancelled"),
                    side="right_bottom",
                )
            elif success:
                self.progress_popup.close_progress_popup()
                # Resetar a variavel
                if self.root.clear_url_var.get():
                    self.root.url1_var.set("")
                if self.root.open_folder_var.get():
                    os.startfile(os.path.realpath(self.options_ydlp["download_path"]))
                if self.root.notify_completed_var.get():
                    if self.root.sound_notification_var.get():
                        play_sound(True)
                    self.root.show_checkmark(self.translator.get_text("success")[0])

            else:
                self.progress_popup.close_progress_popup()
                if self.root.sound_notification_var.get():
                    play_sound(False)
                self.root.show_error(f"Erro: {error}")

            self.progress_popup = None
            self.root.restore_button()

        self.root.after(0, update)

    def cleanup_partial_downloads(self):
        """
        Removes partial download files from the download directory.

        This method scans the download directory and removes any files that are:
        - .part files (partial downloads)
        - .ytdl files (YouTube-DL temporary files)
        - Empty files (0 bytes)

        The cleanup helps prevent accumulation of incomplete downloads.
        """
        try:
            for file in os.listdir(self.options_ydlp["download_path"]):
                full_path = os.path.join(self.options_ydlp["download_path"], file)

                # Check if file is a partial download
                is_partial = (
                    file.endswith(".part")
                    or file.endswith(".ytdl")
                    or
                    # Add other partial file extensions if needed
                    (os.path.isfile(full_path) and os.path.getsize(full_path) == 0)
                )

                if is_partial:
                    try:
                        os.remove(full_path)
                        print(f"Partial file removed: {file}")
                    except Exception as e:
                        print(f"Error removing {file}: {e}")
        except Exception as error:
            print(f"Error cleaning downloads: {error}")
