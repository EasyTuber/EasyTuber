import json
import os
from yt_dlp import YoutubeDL
import threading
from modules.utils import get_ffmpeg_path, play_sound
from libs import CTkProgressPopup, CTkNotification, CTkLoader
import time
import subprocess
import platform


class YoutubeDownloader:
    def __init__(self, root):
        """
        Initializes the YouTube download manager

        Parameters
        ----------
        root : ctk.CTk
            The main application window
        """
        self.app = root
        self.translator = root.translator
        self.ydl_opts = {}
        self.resolutions_available = set()
        self.resolutions_list = []
        self.options_ydlp = {}
        self.url = ""
        self.progress_popup = None
        self.type_download = None
        self.total_videos = 0
        self.current_video = 0

        # Constantes para o avançado
        self.info_preview = []
        self.info_presets = []
        self.info_formats = []
        self.audio_id = None
        self.search_concluded = False

        # Flag para controlar o cancelamento
        self.cancel_download = threading.Event()
        self.download_thread = None

    def start_download(self, type: str, download_options: dict = None):

        self.type_download = type
        self.options_ydlp.clear()
        self.options_ydlp = download_options

        # Janela para mostrar o donwload
        self.progress_popup = None
        self.progress_popup = CTkProgressPopup(
            master=self.app,
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

    # region Iniciar busca
    def start_search(self, url, on_complete=None):
        self.info_preview.clear()
        self.info_presets.clear()
        self.info_formats.clear()
        self.audio_id = None
        self.url = url
        self.search_concluded = False

        loader = CTkLoader(self.app)

        def search_thread_func():
            self.search_process()
            self.app.after(0, lambda: loader.stop_loader())

            if self.search_concluded:
                self.app.after(0, on_complete)

        search_thread = threading.Thread(target=search_thread_func, daemon=True)
        search_thread.start()

    # region Procurar vídeo
    def search_process(self):
        ydl_opts = {"skip_download": True, "quiet": True, "no_warnings": True}

        with YoutubeDL(ydl_opts) as ydl:
            data = ydl.extract_info(self.url, download=False)

            # Criar um dicionário com as informações para preview
            preview_data = {
                "title": data.get("title", "Sem título"),
                "duration": data.get("duration", 0),
                "uploader": data.get("uploader", "Desconhecido"),
                "thumbnail_url": data.get("thumbnail", None),
                "view_count": data.get("view_count", 0),
            }
            self.info_preview = preview_data
            self.extract_video_formats(data)
            self.search_concluded = True

    # region Extrair informações do vídeo
    def extract_video_formats(self, data):
        codec_map = {"vp09": "VP9", "avc": "H.264", "av01": "AV1", "vp8": "VP8"}

        audio_id = None
        for item in data.get("formats", []):
            if (
                item.get("resolution") == "audio only"
                and item.get("format_note") == "Default, high"
            ):
                audio_id = item.get("format_id")
                break

        presets = []
        for item in data.get("formats", []):
            if item.get("video_ext") == "none":
                continue

            vcodec_id = item.get("vcodec", "")
            vcodec = next(
                (codec_map[key] for key in codec_map if key in vcodec_id), "Unknown"
            )

            if not all(k in item for k in ["format_id", "height", "video_ext", "fps"]):
                continue

            video_format = {
                "id": item["format_id"],
                "resolucao": int(item["height"]),
                "ext": item["video_ext"],
                "vcodec": vcodec,
                "FPS": int(item["fps"]),
            }

            video_format["desc"] = (
                f"{video_format['resolucao']}p {video_format['vcodec']} {video_format['FPS']}FPS.{video_format['ext']}"
            )
            presets.append(video_format)

        # Ordenar por resolução (decrescente) e FPS (decrescente)
        presets.sort(key=lambda x: (x["resolucao"], x["FPS"]), reverse=True)

        self.info_formats = data.get("formats", [])
        self.info_presets = presets
        self.audio_id = audio_id

    # region Download do vídeo
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
                    self.app.update_idletasks()

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

    # region Configurações do ydl
    def config_options(self):
        self.ydl_opts.clear()

        # Configurações base comuns
        self.ydl_opts = {
            "progress_hooks": [self.progress_hooks],
            "postprocessor_hooks": [self.postprocessor_hook],
            "ffmpeg_location": self.options_ydlp["ffmpeg_path"],
            "quiet": True,  # Desabilita o modo quieto para receber as mensagens
            "no_warnings": True,  # Permite receber avisos
        }

        if self.type_download == "basic":
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
                    self.ydl_opts["playlist_items"] = self.options_ydlp[
                        "playlist_items"
                    ]
                # Se especificado o reverso da playlist
                if self.options_ydlp["playlist_reverse"]:
                    self.ydl_opts["playlistreverse"] = self.options_ydlp[
                        "playlist_reverse"
                    ]
                # Se especificado o aleatório da playlist
                if self.options_ydlp["playlist_random"]:
                    self.ydl_opts["playlistrandom"] = self.options_ydlp[
                        "playlist_random"
                    ]

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
        elif self.type_download == "advanced":
            # Configurações avançadas

            self.ydl_opts["outtmpl"] = os.path.join(
                self.options_ydlp["download_path"], "%(title)s.%(ext)s"
            )

            if not self.options_ydlp.get("custom_format"):
                self.ydl_opts["format"] = f"{self.options_ydlp['format_id']}+bestaudio"
            else:
                custom_format = self.options_ydlp["custom_format"]

                # Encontrar melhores formatos
                formatos = self.find_best_video_format(
                    int(custom_format["video_quality"]),
                    custom_format["video_codec"],
                    custom_format["container"],
                )

                """
                if formatos:
                    melhor = formatos[0]
                    print(f"Melhor match encontrado:")
                    print(f"  Format ID: {melhor['format_id']}")
                    print(
                        f"  Resolução: {melhor['height']}p {'✓' if melhor['resolucao_match'] else '✗'}"
                    )
                    print(
                        f"  Codec: {melhor['vcodec']} {'✓' if melhor['codec_match'] else '✗'}"
                    )
                    print(
                        f"  Formato: {melhor['ext']} {'✓' if melhor['formato_match'] else '✗'}"
                    )
                    print(f"  Score: {melhor['score']}")
                else:
                    print("Nenhum formato encontrado com os critérios especificados")
                """

                # Construir format string
                format_string = self.construir_format_string(formatos)

                self.ydl_opts.update(
                    {
                        "format": format_string,
                        "postprocessors": [
                            {
                                "key": "FFmpegVideoConvertor",
                                "preferedformat": custom_format["container"],
                            }
                        ],
                        "postprocessor_args": {
                            "FFmpegVideoConvertor": self.postprocessor_args(
                                custom_format
                            ),
                        },
                    }
                )

    def postprocessor_args(self, custom_format):
        """
        Gera os argumentos do postprocessador com base nas configurações avançadas do usuário.

        Args:
            custom_format (dict): Dicionário contendo as configurações personalizadas do usuário.

        Returns:
            list: Lista de argumentos para o postprocessador.
        """
        args = []

        # Codec de vídeo
        codec_map = {
            "h264": "libx264",
            "h265": "libx265",
            "vp9": "libvpx-vp9",
            "av1": "libaom-av1",
        }

        codec = codec_map.get(custom_format["video_codec"], "libx264")
        args.extend(["-codec:v", codec])

        # Codec de áudio
        args.extend(["-codec:a", custom_format["audio_codec"]])

        # Qualidade de compressão
        crf_map = {
            "libx264": {"1": "18", "2": "23", "3": "28"},  # H.264
            "libx265": {"1": "22", "2": "28", "3": "32"},  # H.265
            "libvpx-vp9": {"1": "24", "2": "30", "3": "36"},  # VP9
            "libaom-av1": {"1": "23", "2": "30", "3": "37"},  # AV1
        }

        if codec and custom_format["compression_quality"] in crf_map[codec]:
            crf_value = crf_map[codec][custom_format["compression_quality"]]
            args.extend(["-crf", crf_value])

        # Velocidade de codificação
        encoding_map = {
            "libx264": {
                "0": "ultrafast",
                "1": "fast",
                "2": "medium",
                "3": "slow",
                "4": "veryslow",
            },
            "libx265": {
                "0": "ultrafast",
                "1": "fast",
                "2": "medium",
                "3": "slow",
                "4": "veryslow",
            },
            "libvpx-vp9": {"0": "realtime", "1": "good", "2": "best"},
            "libaom-av1": {"0": "2", "1": "3", "2": "4", "3": "6", "4": "8"},
        }
        encoding_type = {
            "libx264": "preset",
            "libx265": "preset",
            "libvpx-vp9": "deadline",
            "libaom-av1": "cpu-used",
        }

        enconding_speed = encoding_map.get(codec, {}).get(
            str(custom_format["encoding_speed"]), "medium"
        )

        args.extend(["-" + encoding_type[codec], enconding_speed])

        print("Postprocessor args:", args)
        return args

    # region Pós-processamento do download
    def postprocessor_hook(self, d):
        if self.cancel_download.is_set():
            raise Exception("download cancelled")

        elif d["status"] == "finished":
            if self.options_ydlp.get("playlist"):
                message = self.translator.get_text("status")[11].format(
                    index=self.current_video, count=self.total_videos
                )
            else:
                message = self.translator.get_text("status")[12]

            self.progress_popup.update_message(message)
            self.progress_popup.update_progress(1)

        self.app.update_idletasks()

    # region Progress do download
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

                self.app.update_idletasks()
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
            self.app.download_button.configure(state="normal")
            self.app.after(1000, lambda: self.progress_popup.cancel_task())

    # region Atualizar UI após download
    def update_ui_after_download(self, success=False, cancelled=False, error=None):
        # Executa na thread principal
        def update():
            if cancelled:
                CTkNotification(
                    master=self.app,
                    state="info",
                    message=self.translator.get_text("download_cancelled"),
                    side="right_bottom",
                )
            elif success:
                self.progress_popup.close_progress_popup()
                # Resetar a variavel
                if self.app.settings_tab.clear_url_var.get():
                    self.app.url1_var.set("")
                if self.app.settings_tab.open_folder_var.get():
                    download_path = os.path.realpath(self.options_ydlp["download_path"])
                    if platform.system() == "Windows":
                        os.startfile(download_path)
                    elif platform.system() == "Darwin":  # macOS
                        subprocess.run(["open", download_path])
                    else:  # Linux
                        subprocess.run(["xdg-open", download_path])
                if self.app.settings_tab.notify_completed_var.get():
                    self.app.show_checkmark(self.translator.get_text("success")[0])

            else:
                self.progress_popup.close_progress_popup()
                if self.app.settings_tab.sound_notification_var.get():
                    play_sound(False)
                self.app.show_error(f"Erro: {error}")

            self.progress_popup = None
            self.app.download_tab.restore_button()
            self.app.advanced_tab.restore_button()

        self.app.after(0, update)

    # region Limpar downloads parciais
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

    # region Encontrar o melhor formato de vídeo
    def find_best_video_format(
        self, resolucao_desejada, codec_desejado, formato_desejado
    ):
        """
        Encontra o melhor format_id baseado nas preferências do usuário

        Args:
            resolucao_desejada: int (ex: 1080, 720, 480)
            codec_desejado: str ('h264', 'h265', 'vp9', 'av1')
            formato_desejado: str ('mp4', 'mkv', 'webm')
        """

        # Mapeamento de codecs para identificação
        codec_map = {
            "h264": ["avc", "h264"],
            "h265": ["hev", "h265", "hevc"],
            "vp9": ["vp9"],
            "av1": ["av01", "av1"],
        }

        formatos_validos = []

        for fmt in self.info_formats:
            vcodec = fmt.get("vcodec", "").lower()
            altura = fmt.get("height", 0)
            ext = fmt.get("ext", "").lower()

            # Skip formatos só de áudio
            if vcodec == "none" or not altura:
                continue

            # Verificar se atende aos critérios
            codec_match = False
            if codec_desejado.lower() in codec_map:
                for codec_termo in codec_map[codec_desejado.lower()]:
                    if codec_termo in vcodec:
                        codec_match = True
                        break

            resolucao_match = altura == resolucao_desejada
            formato_match = ext == formato_desejado.lower()

            # Calcular pontuação (priorizar matches exatos)
            score = 0
            if resolucao_match:
                score += 100
            if codec_match:
                score += 50
            if formato_match:
                score += 25

            # Adicionar pontos por qualidade geral
            score += altura * 0.01  # Pequeno bonus por resolução

            if score > 0:  # Pelo menos um critério deve ser atendido
                formatos_validos.append(
                    {
                        "format_id": fmt.get("format_id"),
                        "height": altura,
                        "vcodec": vcodec,
                        "ext": ext,
                        "score": score,
                        "resolucao_match": resolucao_match,
                        "codec_match": codec_match,
                        "formato_match": formato_match,
                    }
                )

            # Ordenar por pontuação (maior primeiro)
            formatos_validos.sort(key=lambda x: x["score"], reverse=True)

        return formatos_validos

    # region Construir a string de formato
    def construir_format_string(self, formatos_ordenados, incluir_audio=True):
        """Constrói a string de format baseada nos melhores matches"""

        if not formatos_ordenados:
            return "best"

        # Pegar os top 3 melhores formatos como fallback
        top_formats = [f["format_id"] for f in formatos_ordenados[:3]]

        if incluir_audio:
            # Combinar com áudio
            format_string = "+bestaudio/".join(top_formats) + "+bestaudio"
            format_string += "/" + "/".join(top_formats)  # Fallback sem áudio
            format_string += "/best"  # Fallback final
        else:
            format_string = "/".join(top_formats) + "/best"

        return format_string
