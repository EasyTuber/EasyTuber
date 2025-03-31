import os
from yt_dlp import YoutubeDL
import threading
from modules.utils import get_ffmpeg_path, play_sound
from libs import CTkProgressPopup, CTkNotification
import time


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
        self.total_videos = 0
        self.current_video = 0

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

        # Reset dos contadores
        self.total_videos = 0
        self.current_video = 0

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
                original_extract_info = ydl.extract_info

                def patched_sanitize_info(info_dict, remove_private=True):
                    if self.cancel_download.is_set():
                        raise Exception("download cancelled")
                    return original_sanitize_info(info_dict, remove_private)

                def patched_extract_info(url, download=True, *args, **kwargs):
                    if self.cancel_download.is_set():
                        raise Exception("download cancelled")

                    # Atualiza a interface para mostrar que está baixando informações
                    if self.options_ydlp.get("playlist") and self.total_videos > 1:
                        self.progress_popup.update_label(
                            self.translator.get_text("status")[9].format(
                                index=self.current_video, count=self.total_videos
                            )
                        )
                    else:
                        self.progress_popup.update_label(
                            self.translator.get_text("status")[8]
                        )
                    self.progress_popup.update_progress(0.01)
                    self.progress_popup.update_message("")
                    self.root.update_idletasks()

                    return original_extract_info(url, download, *args, **kwargs)

                ydl.sanitize_info = patched_sanitize_info
                ydl.extract_info = patched_extract_info

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
            "quiet": True,  # Desabilita o modo quieto para receber as mensagens
            "no_warnings": True,  # Permite receber avisos
        }

        # TODO Work in Progress (Advanced)

        # Configurações específicas para playlist
        if self.options_ydlp["playlist"]:
            self.ydl_opts.update(
                {
                    "outtmpl": os.path.join(
                        self.options_ydlp["download_path"],
                        "%(playlist)s/%(playlist_autonumber)s - %(title)s.%(ext)s",
                    ),  # Cria pasta com nome da playlist # TODO colocar como opcional
                    "ignoreerrors": True,  # Continua mesmo se um vídeo falhar
                    "playlist": True,
                    "yes_playlist": True,
                }
            )
            # Se especificado os itens da playlist
            if self.options_ydlp["playlist_items"]:
                self.ydl_opts["playlist_items"] = self.options_ydlp["playlist_items"]
            # Se especificado o reverso da playlist
            if self.options_ydlp["playlist_reverse"]:
                self.ydl_opts["playlistreverse"] = self.options_ydlp["playlist_reverse"]
            # Se especificado o aleatório da playlist
            if self.options_ydlp["playlist_random"]:
                self.ydl_opts["playlistrandom"] = self.options_ydlp["playlist_random"]

        else:
            self.ydl_opts["outtmpl"] = os.path.join(
                self.options_ydlp["download_path"], "%(title)s.%(ext)s"
            )

        # Se é audio
        if self.options_ydlp["media"] in self.translator.get_text("audio"):
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
            self.ydl_opts.update(
                {
                    "format": f'bestvideo[height<={self.options_ydlp["quality"]}]+bestaudio/best[height<={self.options_ydlp["quality"]}]',
                    "merge_output_format": self.options_ydlp["format"],
                }
            )

    def postprocessor_hook(self, d):
        if self.cancel_download.is_set():
            raise Exception("download cancelled")

        elif d["status"] == "finished":
            if self.options_ydlp.get("playlist"):
                message = self.translator.get_text("status")[11].format(
                    index=self.current_video, count=self.total_videos
                )
            else:
                message = self.translator.get_text("status")[10]

            self.progress_popup.update_message(message)
            self.progress_popup.update_progress(1)

        self.root.update_idletasks()

    # Atualiza a barra de progresso e o status de download
    def progress_hooks(self, d):
        if self.cancel_download.is_set():
            raise Exception("download cancelled")

        info_dict = d.get("info_dict", {})
        playlist_index = info_dict.get("playlist_autonumber")
        playlist_count = info_dict.get("n_entries")

        if self.options_ydlp.get("playlist"):
            self.total_videos = playlist_count
            self.current_video = playlist_index + 1

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

            self.progress_popup.update_message("")
            self.progress_popup.update_progress(0.98)

        elif d["status"] == "error":
            # TODO configurar caso erro
            self.progress_popup.update_label(self.translator.get_text("status")[3])
            self.progress_popup.update_progress(0)
            self.root.download_button.configure(state="normal")
            self.root.after(1000, lambda: self.progress_popup.cancel_task())

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
        Remove arquivos parciais do diretório de download.

        Este método verifica o diretório de download e remove arquivos que são:
        - Arquivos .part (downloads parciais)
        - Arquivos .ytdl (arquivos temporários do YouTube-DL)
        - Arquivos vazios (0 bytes)

        A limpeza ajuda a evitar o acúmulo de downloads incompletos.
        """

        def try_remove_file(filepath, max_attempts=5):
            """Tenta remover um arquivo com várias tentativas e delay."""
            for attempt in range(max_attempts):
                try:
                    os.remove(filepath)
                    print(f"Arquivo parcial removido: {os.path.basename(filepath)}")
                    return True
                except PermissionError:
                    print(
                        f"Arquivo em uso, tentativa {attempt + 1} de {max_attempts}: {os.path.basename(filepath)}"
                    )
                    time.sleep(0.5)  # Reduzido para 0.5 segundos
                except Exception as e:
                    print(f"Erro ao tentar remover {os.path.basename(filepath)}: {e}")
                    time.sleep(0.5)
            return False

        try:
            for file in os.listdir(self.options_ydlp["download_path"]):
                full_path = os.path.join(self.options_ydlp["download_path"], file)

                # Verifica se o arquivo é um download parcial
                is_partial = (
                    file.endswith(".part")
                    or file.endswith(".ytdl")
                    or
                    # Adiciona outras extensões de arquivo parcial se necessário
                    (os.path.isfile(full_path) and os.path.getsize(full_path) == 0)
                )

                if is_partial:
                    try_remove_file(full_path)
        except Exception as error:
            print(f"Erro ao limpar downloads: {error}")
