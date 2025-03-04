import yt_dlp
import os


class YoutubeDonwloader:
    def __init__(self, app):

        self.app = app
        self.ydl_opts = {}
        self.resolutions_available = set()
        self.info = []
        self.resolutions_list = []
        self.options_ydlp = {}
        self.url = ""

    def get_format_options(self):

        # Configurações base comuns
        self.ydl_opts.update(
            {
                "ffmpeg_location": self.options_ydlp["ffmpeg_location"],
            }
        )

        # Configurações específicas para playlist
        if self.options_ydlp["playlist"] == "on":
            self.ydl_opts.update(
                {
                    "outtmpl": os.path.join(
                        self.options_ydlp["download_path"],
                        "%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s",
                    ),  # Cria pasta com nome da playlist
                    "ignoreerrors": True,  # Continua mesmo se um vídeo falhar
                    "playlist": True,
                    "yes_playlist": True,
                }
            )
        else:
            self.ydl_opts["outtmpl"] = os.path.join(
                self.options_ydlp["download_path"], "%(title)s.%(ext)s"
            )

        if (
            self.options_ydlp["midia"]
            in self.app.translator.get_text("media_values")[1]
        ):
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
        else:
            self.ydl_opts.update(
                {
                    "format": f"bestvideo[ext={self.options_ydlp["formato"]}][height<={self.options_ydlp["qualidade"]}]+bestaudio[ext=m4a]/best[ext={self.options_ydlp["formato"]}][height<={self.options_ydlp["qualidade"]}]/best[height<={self.options_ydlp["qualidade"]}]/best",
                }
            )

    # Atualiza a barra de progresso e o status de download
    def update_progress(self, d):
        if d["status"] == "downloading":
            try:
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
                    self.app.progress.set(percentage)

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
                            status_text = self.app.translator.get_text(
                                "downloading_progress"
                            )[0].format(
                                percent=f"{percentage:.1%}",
                                speed=f"{speed_mb:.1f}",
                                eta_min=f"{eta_min:.0f}",
                                eta_sec=f"{eta_sec:.0f}",
                            )
                        else:
                            status_text = self.app.translator.get_text(
                                "downloading_progress"
                            )[1].format(
                                percent=f"{percentage:.1%}", speed=f"{speed_mb:.1f}"
                            )
                    else:
                        status_text = self.app.translator.get_text(
                            "downloading_progress"
                        )[2].format(percent=f"{percentage:.1%}")

                    self.app.status_label.configure(text=status_text)

                self.app.update_idletasks()
            except Exception as e:
                print(f"Erro ao atualizar progresso: {str(e)}")
                pass

        elif d["status"] == "finished":
            self.app.status_label.configure(
                text=self.app.translator.get_text("status")[2]
            )
            self.app.progress.set(1)

        elif d["status"] == "error":
            self.app.status_label.configure(
                text=self.app.translator.get_text("status")[3]
            )
            self.app.progress.set(0)
            self.app.download_button.configure(state="normal")

    def config_options(self):
        self.ydl_opts.clear()
        self.options_ydlp = {
            "url": self.app.url_entry.get(),
            "midia": self.app.midia_var.get(),
            "formato": self.app.formato_var.get(),
            "playlist": self.app.playlist_check_var.get(),
            "qualidade": self.app.qualidade_var.get().replace("p", ""),
            "download_path": self.app.download_path_entry.get(),
            "ffmpeg_location": self.app.ffmpeg_path_entry.get(),
        }

        self.ydl_opts = {
            "progress_hooks": [self.update_progress],
        }

        # Adiciona opções de formato
        self.get_format_options()

    def start_download(self):
        # Mostra a barra de progresso e o statuss

        self.config_options()

        self.url = self.options_ydlp["url"]
        print(self.url)

        self.app.progress.grid(row=0, column=0, sticky="ew", pady=(10, 0), padx=10)
        self.app.status_label.grid(row=1, column=0, pady=(5, 0))

        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            ydl.download([self.url])

        self.app.status_label.configure(text=self.app.translator.get_text("status")[4])
        self.app.progress.set(1)
        self.app.download_button.configure(state="normal")
        self.app.show_checkmark(self.app.translator.get_text("success")[0])
