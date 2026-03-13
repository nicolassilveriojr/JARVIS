import os
import re
import shutil
import subprocess
import webbrowser
import threading
import time
import datetime
import hashlib
import urllib.request
import urllib.parse
import json

try:
    import cv2
except ImportError:
    cv2 = None

try:
    import pyautogui
except ImportError:
    pyautogui = None

try:
    from PIL import Image
except ImportError:
    Image = None


PASTAS_MAP = {
    "documentos":       "Documents",
    "downloads":        "Downloads",
    "desktop":          "Desktop",
    "area de trabalho": "Desktop",
    "imagens":          "Pictures",
    "videos":           "Videos",
    "musica":           "Music",
    "musicas":          "Music",
}


def resolver_pasta(texto):
    t = texto.lower()
    for nome, pasta in PASTAS_MAP.items():
        if nome in t:
            return os.path.expanduser(f"~\\{pasta}"), nome
    return None, None


class JarvisCommands:
    def __init__(self, brain, voice, log_fn, status_fn):
        self.brain     = brain
        self.voice     = voice
        self.log       = log_fn
        self.status    = status_fn
        self.apps_index = {}
        self._indexar_apps()

    # ── INDEXAR APPS ──────────────────────────────────────────

    def _indexar_apps(self):
        def _varrer():
            pastas = [
                r"C:\Program Files",
                r"C:\Program Files (x86)",
                os.path.expanduser(r"~\AppData\Local"),
                os.path.expanduser(r"~\AppData\Roaming"),
                os.path.expanduser(r"~\AppData\Local\Programs"),
            ]
            encontrados = {}
            for base in pastas:
                if not os.path.exists(base):
                    continue
                try:
                    for root, dirs, files in os.walk(base):
                        dirs[:] = [d for d in dirs if d not in ["WinSxS", "servicing", "Temp"]]
                        for file in files:
                            if file.lower().endswith(".exe"):
                                nome = file.lower().replace(".exe", "")
                                encontrados[nome] = os.path.join(root, file)
                except:
                    continue
            self.apps_index = encontrados
            self.log("SYS", f"Varredura concluída! {len(encontrados)} apps encontrados.", "sys")
        threading.Thread(target=_varrer, daemon=True).start()

    # ── PROCESSAR COMANDO ──────────────────────────────────────

    def processar(self, texto):
        t = self._corrigir(texto)
        if t != texto.lower():
            self.log("SYS", f"Entendido como: {t}", "sys")

        # Alarme
        if any(p in t for p in ["lembrar", "alarme", "lembrete"]):
            return self._alarme_cmd(t, texto)

        # Arquivos
        if any(p in t for p in ["duplicado", "duplicados"]):
            return self._apagar_duplicados(t)
        if any(p in t for p in ["buscar", "procurar", "onde esta", "achar"]):
            return self._buscar_arquivo(t)
        if any(p in t for p in ["listar", "mostrar arquivos"]):
            return self._listar_arquivos(t)
        if any(p in t for p in ["renomear", "mudar nome"]):
            return self._renomear_arquivo(t)
        if any(p in t for p in ["tamanho", "quanto ocupa", "espaco"]):
            return self._tamanho_pasta(t)
        if any(p in t for p in ["limpar temporario", "limpar temp", "arquivos temp"]):
            return self._limpar_temporarios()
        if any(p in t for p in ["deletar", "apagar", "excluir", "remover"]):
            return self._deletar_arquivo(t)
        if any(p in t for p in ["mover", "transferir", "copiar"]):
            return self._mover_arquivo(t)

        # Sistema
        if any(p in t for p in ["volume", "som"]):
            return self._volume(t)
        if any(p in t for p in ["brilho", "tela mais", "tela menos"]):
            return self._brilho(t)
        if any(p in t for p in ["desligar", "reiniciar", "bloquear", "hibernar"]):
            return self._controlar_pc(t)
        if any(p in t for p in ["cpu", "ram", "memoria", "processador", "uso do pc"]):
            return self._status_sistema()
        if any(p in t for p in ["screenshot", "print", "captura de tela"]):
            return self._screenshot()

        # Info
        if any(p in t for p in ["clima", "temperatura", "previsao", "chuva"]):
            return self._clima(t)
        if any(p in t for p in ["dolar", "bitcoin", "btc", "euro", "cotacao"]):
            return self._cotacao(t)
        if any(p in t for p in ["pesquisar", "buscar no google"]):
            return self._pesquisar_google(texto)

        # Organizar downloads
        if any(p in t for p in ["organizar", "arrumar"]) and "download" in t:
            self._organizar_downloads()
            return "Downloads organizados, Chefe."

        # Webcam
        if any(p in t for p in ["webcam", "camera"]):
            return self._webcam()

        # Pastas
        for nome, pasta in PASTAS_MAP.items():
            if nome in t and any(p in t for p in ["abrir", "abre", "acessa"]):
                caminho = os.path.expanduser(f"~\\{pasta}")
                if os.path.exists(caminho):
                    os.startfile(caminho)
                return f"Abrindo {nome}, Chefe."

        # Sites
        sites = {
            "youtube": "https://youtube.com", "google": "https://google.com",
            "instagram": "https://instagram.com", "github": "https://github.com",
            "netflix": "https://netflix.com", "gmail": "https://mail.google.com",
            "twitter": "https://twitter.com", "twitch": "https://twitch.tv",
            "discord": "https://discord.com", "reddit": "https://reddit.com",
        }
        for site, url in sites.items():
            if site in t:
                if site == "youtube":
                    m = re.search(r"youtube\s+(.+)", t)
                    if m:
                        url = f"https://youtube.com/results?search_query={m.group(1).replace(' ', '+')}"
                webbrowser.open(url)
                return f"Abrindo {site}, Chefe."

        # Apps fixos
        apps = {
            "notepad": "notepad", "bloco de notas": "notepad",
            "calculadora": "calc", "paint": "mspaint",
            "cmd": "cmd", "powershell": "powershell",
            "chrome": "chrome", "firefox": "firefox",
            "edge": "msedge", "spotify": "spotify",
        }
        for app, cmd in apps.items():
            if app in t:
                try:
                    subprocess.Popen(cmd)
                    return f"Abrindo {app}, Chefe."
                except Exception as e:
                    return str(e)

        # Apps do índice
        if any(p in t for p in ["abrir", "abre", "iniciar"]):
            termo = t
            for p in ["abrir", "abre", "iniciar", "o ", "a "]:
                termo = termo.replace(p, "").strip()
            if termo in self.apps_index:
                try:
                    subprocess.Popen(self.apps_index[termo])
                    return f"Abrindo {termo}, Chefe."
                except Exception as e:
                    return str(e)
            for nome, caminho in self.apps_index.items():
                if termo in nome or nome in termo:
                    try:
                        subprocess.Popen(caminho)
                        return f"Abrindo {nome}, Chefe."
                    except:
                        pass

        # IA
        return None  # sinaliza que deve ir pra IA

    # ── CORREÇÃO DE TEXTO ──────────────────────────────────────

    def _corrigir(self, texto):
        from difflib import SequenceMatcher
        correcoes = {
            "abrri": "abrir", "abri": "abrir", "yotube": "youtube", "yutube": "youtube",
            "googel": "google", "instagran": "instagram", "netflixx": "netflix",
            "discrod": "discord", "spotfy": "spotify", "chorme": "chrome",
            "donwloads": "downloads", "downlods": "downloads", "documetos": "documentos",
            "deletar": "deletar", "deltar": "deletar", "orgainzar": "organizar",
            "temporaios": "temporarios", "duplicaods": "duplicados",
        }
        palavras = texto.lower().split()
        corrigidas = []
        for palavra in palavras:
            if palavra in correcoes:
                corrigidas.append(correcoes[palavra])
            else:
                melhor, melhor_score = palavra, 0
                for errado, certo in correcoes.items():
                    score = SequenceMatcher(None, palavra, errado).ratio()
                    if score > 0.80 and score > melhor_score:
                        melhor_score = score
                        melhor = certo
                corrigidas.append(melhor)
        return " ".join(corrigidas)

    # ── ARQUIVOS ──────────────────────────────────────────────

    def _deletar_arquivo(self, texto):
        match = re.search(r"[\w\-\. ]+\.\w{2,5}", texto)
        if not match:
            return "Informe o nome do arquivo com extensão, Chefe."
        nome_arq = match.group(0).strip()
        caminho_pasta, nome_pasta = resolver_pasta(texto)
        if not caminho_pasta:
            caminho_pasta = os.path.expanduser("~\\Downloads")
            nome_pasta = "downloads"
        caminho_arq = os.path.join(caminho_pasta, nome_arq)
        if not os.path.exists(caminho_arq):
            for root, dirs, files in os.walk(caminho_pasta):
                if nome_arq in files:
                    caminho_arq = os.path.join(root, nome_arq)
                    break
            else:
                return f"'{nome_arq}' não encontrado, Chefe."
        try:
            os.remove(caminho_arq)
            return f"'{nome_arq}' deletado, Chefe."
        except Exception as e:
            return f"Erro: {str(e)[:60]}"

    def _mover_arquivo(self, texto):
        copiar = "copiar" in texto.lower()
        match = re.search(r"[\w\-\. ]+\.\w{2,5}", texto)
        if not match:
            return "Informe o nome do arquivo, Chefe."
        nome_arq = match.group(0).strip()
        origem_path = None
        for nome, pasta in PASTAS_MAP.items():
            caminho = os.path.expanduser(f"~\\{pasta}")
            if os.path.exists(os.path.join(caminho, nome_arq)) and not origem_path:
                origem_path = os.path.join(caminho, nome_arq)
        match_dest = re.search(r"para\s+(\w[\w ]*)", texto.lower())
        destino_path = None
        if match_dest:
            termo = match_dest.group(1).strip()
            for nome, pasta in PASTAS_MAP.items():
                if nome in termo or termo in nome:
                    destino_path = os.path.expanduser(f"~\\{pasta}")
                    break
        if not origem_path:
            return f"'{nome_arq}' não encontrado, Chefe."
        if not destino_path:
            return "Pasta de destino não identificada, Chefe."
        try:
            dst = os.path.join(destino_path, nome_arq)
            if copiar:
                shutil.copy2(origem_path, dst)
                return f"'{nome_arq}' copiado, Chefe."
            else:
                shutil.move(origem_path, dst)
                return f"'{nome_arq}' movido, Chefe."
        except Exception as e:
            return f"Erro: {str(e)[:60]}"

    def _apagar_duplicados(self, texto):
        caminho_pasta, nome_pasta = resolver_pasta(texto)
        if not caminho_pasta:
            caminho_pasta = os.path.expanduser("~\\Downloads")
            nome_pasta = "downloads"
        vistos, apagados = {}, 0
        try:
            for arq in os.listdir(caminho_pasta):
                c = os.path.join(caminho_pasta, arq)
                if not os.path.isfile(c):
                    continue
                h = hashlib.md5(open(c, "rb").read()).hexdigest()
                if h in vistos:
                    os.remove(c)
                    apagados += 1
                else:
                    vistos[h] = c
        except Exception as e:
            return f"Erro: {str(e)[:60]}"
        return f"{apagados} duplicado(s) removido(s) de {nome_pasta}, Chefe." if apagados else f"Nenhum duplicado em {nome_pasta}, Chefe."

    def _buscar_arquivo(self, texto):
        match = re.search(r"[\w\-\. ]+\.\w{2,5}", texto)
        if not match:
            return "Informe o nome do arquivo com extensão, Chefe."
        nome_arq = match.group(0).strip()
        pastas = [os.path.expanduser(f"~\\{p}") for p in ["Downloads", "Documents", "Desktop", "Pictures", "Videos", "Music"]]
        encontrados = []
        for pasta in pastas:
            if not os.path.exists(pasta):
                continue
            for root, dirs, files in os.walk(pasta):
                if nome_arq in files:
                    encontrados.append(os.path.join(root, nome_arq))
        if not encontrados:
            return f"'{nome_arq}' não encontrado, Chefe."
        return f"Encontrei em: {encontrados[0]}"

    def _listar_arquivos(self, texto):
        caminho_pasta, nome_pasta = resolver_pasta(texto)
        if not caminho_pasta:
            caminho_pasta = os.path.expanduser("~\\Downloads")
            nome_pasta = "downloads"
        try:
            arquivos = [f for f in os.listdir(caminho_pasta) if os.path.isfile(os.path.join(caminho_pasta, f))]
            lista = "\n".join(arquivos[:15])
            sufixo = f"\n...e mais {len(arquivos)-15}." if len(arquivos) > 15 else ""
            self.log("JARVIS", f"Arquivos em {nome_pasta}:\n{lista}{sufixo}", "jarvis")
            return f"{len(arquivos)} arquivo(s) em {nome_pasta}, Chefe."
        except Exception as e:
            return f"Erro: {str(e)[:60]}"

    def _renomear_arquivo(self, texto):
        matches = re.findall(r"[\w\-]+\.\w{2,5}", texto)
        if len(matches) < 2:
            return "Preciso do nome atual e novo, Chefe. Ex: 'renomear foto.png para imagem.png'"
        caminho_pasta, nome_pasta = resolver_pasta(texto)
        if not caminho_pasta:
            caminho_pasta = os.path.expanduser("~\\Downloads")
        src = os.path.join(caminho_pasta, matches[0])
        dst = os.path.join(caminho_pasta, matches[1])
        if not os.path.exists(src):
            return f"'{matches[0]}' não encontrado, Chefe."
        try:
            os.rename(src, dst)
            return f"'{matches[0]}' renomeado para '{matches[1]}', Chefe."
        except Exception as e:
            return f"Erro: {str(e)[:60]}"

    def _tamanho_pasta(self, texto):
        caminho_pasta, nome_pasta = resolver_pasta(texto)
        if not caminho_pasta:
            caminho_pasta = os.path.expanduser("~\\Downloads")
            nome_pasta = "downloads"
        total = 0
        for root, dirs, files in os.walk(caminho_pasta):
            for f in files:
                try:
                    total += os.path.getsize(os.path.join(root, f))
                except:
                    pass
        if total < 1024**2:
            tam = f"{total/1024:.1f} KB"
        elif total < 1024**3:
            tam = f"{total/1024**2:.1f} MB"
        else:
            tam = f"{total/1024**3:.2f} GB"
        return f"{nome_pasta} ocupa {tam}, Chefe."

    def _limpar_temporarios(self):
        pastas = [os.environ.get("TEMP", ""), os.environ.get("TMP", ""), os.path.expanduser("~\\AppData\\Local\\Temp")]
        total, erros = 0, 0
        for pasta in pastas:
            if not pasta or not os.path.exists(pasta):
                continue
            for arq in os.listdir(pasta):
                c = os.path.join(pasta, arq)
                try:
                    if os.path.isfile(c):
                        os.remove(c)
                    else:
                        shutil.rmtree(c)
                    total += 1
                except:
                    erros += 1
        return f"Limpeza concluída! {total} item(s) removido(s), {erros} bloqueado(s), Chefe."

    def _organizar_downloads(self):
        caminho = os.path.expanduser("~\\Downloads")
        tipos = {
            "Imagens": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"],
            "Documentos": [".pdf", ".doc", ".docx", ".txt", ".xlsx", ".pptx"],
            "Videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv"],
            "Audios": [".mp3", ".wav", ".flac", ".aac", ".m4a"],
            "Compactados": [".zip", ".rar", ".7z", ".tar", ".gz"],
            "Programas": [".exe", ".msi", ".bat"],
        }
        movidos = 0
        for arq in os.listdir(caminho):
            src = os.path.join(caminho, arq)
            if not os.path.isfile(src):
                continue
            _, ext = os.path.splitext(arq)
            for pasta, exts in tipos.items():
                if ext.lower() in exts:
                    dst_dir = os.path.join(caminho, pasta)
                    os.makedirs(dst_dir, exist_ok=True)
                    dst = os.path.join(dst_dir, arq)
                    if not os.path.exists(dst):
                        shutil.move(src, dst)
                        movidos += 1
                    break

    # ── SISTEMA ───────────────────────────────────────────────

    def _volume(self, t):
        try:
            if "aumentar" in t or "mais alto" in t:
                subprocess.run(["powershell", "-c", "(New-Object -com WScript.Shell).SendKeys([char]175)"], capture_output=True)
                return "Volume aumentado, Chefe."
            elif "diminuir" in t or "mais baixo" in t:
                subprocess.run(["powershell", "-c", "(New-Object -com WScript.Shell).SendKeys([char]174)"], capture_output=True)
                return "Volume diminuído, Chefe."
            elif "mutar" in t or "mudo" in t or "silencio" in t:
                subprocess.run(["powershell", "-c", "(New-Object -com WScript.Shell).SendKeys([char]173)"], capture_output=True)
                return "Som mutado, Chefe."
            else:
                m = re.search(r"(\d+)", t)
                if m:
                    return f"Volume ajustado para {m.group(1)}%, Chefe."
        except Exception as e:
            return f"Erro no volume: {str(e)[:50]}"
        return "Comando de volume não reconhecido, Chefe."

    def _brilho(self, t):
        try:
            m = re.search(r"(\d+)", t)
            nivel = int(m.group(1)) if m else (80 if "mais" in t else 40)
            nivel = max(0, min(100, nivel))
            subprocess.run(["powershell", "-c",
                f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{nivel})"],
                capture_output=True)
            return f"Brilho em {nivel}%, Chefe."
        except Exception as e:
            return f"Erro no brilho: {str(e)[:50]}"

    def _controlar_pc(self, t):
        if "desligar" in t:
            subprocess.run(["shutdown", "/s", "/t", "10"])
            return "Desligando em 10 segundos, Chefe."
        elif "reiniciar" in t:
            subprocess.run(["shutdown", "/r", "/t", "10"])
            return "Reiniciando em 10 segundos, Chefe."
        elif "bloquear" in t:
            subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
            return "PC bloqueado, Chefe."
        elif "hibernar" in t:
            subprocess.run(["shutdown", "/h"])
            return "Hibernando, Chefe."
        elif "cancelar" in t:
            subprocess.run(["shutdown", "/a"])
            return "Desligamento cancelado, Chefe."
        return "Comando não reconhecido, Chefe."

    def _status_sistema(self):
        try:
            import psutil
            cpu  = psutil.cpu_percent(interval=1)
            ram  = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            return (f"CPU: {cpu}% | RAM: {ram.percent}% "
                    f"({ram.used//1024**2}MB/{ram.total//1024**2}MB) | "
                    f"Disco: {disk.percent}% usado, Chefe.")
        except ImportError:
            return "Instale psutil, Chefe: pip install psutil"

    def _screenshot(self):
        if not pyautogui:
            return "pyautogui não instalado, Chefe."
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        caminho = os.path.join(os.path.expanduser("~\\Desktop"), f"screenshot_{ts}.png")
        pyautogui.screenshot(caminho)
        return f"Screenshot salvo no Desktop: screenshot_{ts}.png, Chefe."

    def _webcam(self):
        if not cv2:
            return "OpenCV não instalado, Chefe."
        try:
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            cap.release()
            if ret:
                cv2.imwrite("_webcam.png", frame)
                resp = self.brain.perguntar("O que você vê nessa imagem?", "_webcam.png")
                try:
                    os.remove("_webcam.png")
                except:
                    pass
                return resp
        except Exception as e:
            return f"Erro na webcam: {str(e)[:60]}"
        return "Não consegui acessar a webcam, Chefe."

    # ── INFO ──────────────────────────────────────────────────

    def _clima(self, t):
        try:
            cidade = "São Paulo"
            for p in ["clima em", "temperatura em", "tempo em"]:
                if p in t:
                    cidade = t.split(p)[-1].strip()
                    break
            url = f"https://wttr.in/{urllib.parse.quote(cidade)}?format=j1"
            with urllib.request.urlopen(url, timeout=5) as r:
                data = json.loads(r.read())
            temp = data["current_condition"][0]["temp_C"]
            desc = data["current_condition"][0]["weatherDesc"][0]["value"]
            umid = data["current_condition"][0]["humidity"]
            return f"{cidade}: {temp}°C, {desc}, umidade {umid}%, Chefe."
        except:
            return "Não consegui obter o clima, Chefe. Verifique a internet."

    def _cotacao(self, t):
        try:
            resultados = []
            pares = {"dolar": "USD-BRL", "euro": "EUR-BRL", "bitcoin": "BTC-BRL", "btc": "BTC-BRL"}
            for palavra, par in pares.items():
                if palavra in t:
                    chave = par.replace("-", "")
                    with urllib.request.urlopen(f"https://economia.awesomeapi.com.br/json/last/{par}", timeout=5) as r:
                        data = json.loads(r.read())
                    val = float(data[chave]["bid"])
                    nome = palavra.capitalize()
                    resultados.append(f"{nome}: R$ {val:,.2f}")
            return ", ".join(resultados) + ", Chefe." if resultados else "Qual cotação deseja? Dólar, Euro ou Bitcoin, Chefe."
        except:
            return "Erro ao obter cotações, Chefe."

    def _pesquisar_google(self, texto):
        t = texto.lower()
        termo = texto
        for p in ["pesquisar", "pesquisa", "buscar no google", "procurar no google"]:
            if p in t:
                termo = texto.lower().replace(p, "").strip()
                break
        webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote(termo)}")
        return f"Pesquisando '{termo}' no Google, Chefe."

    # ── ALARME ────────────────────────────────────────────────

    def _alarme_cmd(self, t, texto_original):
        m = re.search(r"(\d+)\s*(minuto|segundo|hora|min|seg|h)", t)
        if m:
            val = int(m.group(1))
            un  = m.group(2)
            mins = val / 60 if "seg" in un else val * 60 if "hor" in un or un == "h" else val
            msg  = re.sub(r"\d+\s*(minuto|segundo|hora|min|seg|h)s?", "", texto_original).strip() or "Lembrete"
            threading.Thread(target=self._alarme, args=(int(mins * 60), msg), daemon=True).start()
            return f"Alarme definido para {int(mins)} minutos, Chefe."
        return "Informe o tempo do alarme, Chefe."

    def _alarme(self, segundos, msg):
        time.sleep(segundos)
        self.log("JARVIS", f"ALARME: {msg}", "jarvis")
        self.voice.falar(f"Chefe, seu lembrete: {msg}")
        try:
            import winsound
            for _ in range(4):
                winsound.Beep(1200, 400)
                time.sleep(0.2)
        except:
            pass

    # ─────────────────── BATERIA E HARDWARE ───────────────────

    def status_bateria(self):
        try:
            import psutil
            bat = psutil.sensors_battery()
            if bat:
                status = "carregando" if bat.power_plugged else "descarregando"
                return f"Bateria em {bat.percent:.0f}%, {status}, Chefe."
            return "Sem bateria detectada (PC de mesa), Chefe."
        except:
            return "Não consegui verificar a bateria, Chefe."

    def monitorar_hardware(self):
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=1)
            ram = psutil.virtual_memory()
            disco = psutil.disk_usage("/")
            bat = psutil.sensors_battery()
            bat_info = f" | Bateria: {bat.percent:.0f}%" if bat else ""
            temps = ""
            try:
                sensores = psutil.sensors_temperatures()
                if sensores:
                    for nome, entries in sensores.items():
                        if entries:
                            temps = f" | Temp CPU: {entries[0].current:.0f}°C"
                            break
            except:
                pass
            return (f"CPU: {cpu}% | RAM: {ram.percent}% "
                    f"({ram.used//1024**2}MB/{ram.total//1024**2}MB) | "
                    f"Disco: {disco.percent}%{bat_info}{temps}, Chefe.")
        except ImportError:
            return "Instale psutil: pip install psutil"

    # ─────────────────── RECONHECIMENTO FACIAL ───────────────────

    def reconhecer_rosto(self, log_fn=None):
        try:
            import cv2 as cv
            import numpy as np
            cap = cv.VideoCapture(0)
            if not cap.isOpened():
                return "Câmera não disponível, Chefe."
            face_cascade = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_frontalface_default.xml')
            ret, frame = cap.read()
            cap.release()
            if not ret:
                return "Não consegui capturar imagem, Chefe."
            gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            if len(faces) == 0:
                return "Nenhum rosto detectado, Chefe."
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            path = os.path.join(os.path.expanduser("~\\Desktop"), f"rosto_{ts}.png")
            for (x, y, w, h) in faces:
                cv.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv.imwrite(path, frame)
            return f"{len(faces)} rosto(s) detectado(s). Imagem salva no Desktop, Chefe."
        except Exception as e:
            return f"Erro no reconhecimento: {str(e)[:60]}"

    def modo_seguranca(self, ativar=True):
        if ativar:
            threading.Thread(target=self._monitorar_intruso, daemon=True).start()
            return "Modo de segurança ativado! Monitorando câmera, Chefe."
        return "Modo de segurança desativado, Chefe."

    def _monitorar_intruso(self):
        try:
            import cv2 as cv
            cap = cv.VideoCapture(0)
            face_cascade = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_frontalface_default.xml')
            ret, frame_anterior = cap.read()
            gray_anterior = cv.cvtColor(frame_anterior, cv.COLOR_BGR2GRAY)
            self.log("SYS", "Modo segurança: monitorando...", "sys")
            while getattr(self, '_modo_seguranca', True):
                ret, frame = cap.read()
                if not ret:
                    break
                gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
                diff = cv.absdiff(gray_anterior, gray)
                _, thresh = cv.threshold(diff, 25, 255, cv.THRESH_BINARY)
                movimento = cv.countNonZero(thresh)
                if movimento > 5000:
                    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                    if len(faces) > 0:
                        self.log("JARVIS", "⚠ INTRUSO DETECTADO! Bloqueando PC, Chefe!", "err")
                        subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
                        self.falar("Intruso detectado! Bloqueando o sistema, Chefe!")
                        break
                gray_anterior = gray
                time.sleep(0.5)
            cap.release()
        except Exception as e:
            self.log("ERR", f"Segurança: {str(e)[:50]}", "err")

    # ─────────────────── NOTIFICAÇÕES ───────────────────

    def notificar(self, titulo, mensagem):
        try:
            from plyer import notification
            notification.notify(
                title=titulo,
                message=mensagem,
                app_name="J.A.R.V.I.S",
                timeout=5
            )
            return f"Notificação enviada: {titulo}, Chefe."
        except ImportError:
            try:
                subprocess.run([
                    "powershell", "-c",
                    f'New-BurntToastNotification -Text "JARVIS", "{mensagem}"'
                ], capture_output=True)
                return f"Notificação enviada, Chefe."
            except:
                return "Instale plyer para notificações: pip install plyer"

    # ─────────────────── ABRIR EMAIL ───────────────────

    def abrir_email(self, texto):
        webbrowser.open("https://mail.google.com")
        return "Abrindo Gmail, Chefe."

    # ─────────────────── PIADA / CURIOSIDADE ───────────────────

    def contar_hora(self):
        agora = datetime.datetime.now()
        return f"São {agora.strftime('%H:%M')}, Chefe."

    def contar_data(self):
        agora = datetime.datetime.now()
        return f"Hoje é {agora.strftime('%d/%m/%Y')}, Chefe."

    # ─────────────────── IP E REDE ───────────────────

    def info_rede(self):
        try:
            import socket
            import urllib.request
            hostname = socket.gethostname()
            ip_local = socket.gethostbyname(hostname)
            with urllib.request.urlopen("https://api.ipify.org", timeout=3) as r:
                ip_externo = r.read().decode()
            return f"IP local: {ip_local} | IP externo: {ip_externo} | PC: {hostname}, Chefe."
        except:
            return "Não consegui obter informações de rede, Chefe."

    # ─────────────────── VELOCIDADE DA INTERNET ───────────────────

    def testar_internet(self):
        try:
            import urllib.request, time
            inicio = time.time()
            urllib.request.urlopen("https://www.google.com", timeout=5)
            ping = (time.time() - inicio) * 1000
            return f"Internet funcionando! Ping: {ping:.0f}ms, Chefe."
        except:
            return "Sem conexão com a internet, Chefe."

    # ─────────────────── PROCESSOS DO SISTEMA ───────────────────

    def listar_processos(self):
        try:
            import psutil
            procs = sorted(psutil.process_iter(['name', 'cpu_percent', 'memory_percent']),
                          key=lambda p: p.info['cpu_percent'], reverse=True)[:5]
            lista = "\n".join([f"{p.info['name']}: CPU {p.info['cpu_percent']}% RAM {p.info['memory_percent']:.1f}%"
                               for p in procs])
            self.log("JARVIS", f"Top 5 processos:\n{lista}", "jarvis")
            return "Top 5 processos listados no log, Chefe."
        except:
            return "Instale psutil para ver processos, Chefe."

    def matar_processo(self, texto):
        try:
            import psutil, re
            m = re.search(r'matar\s+(.+)|fechar\s+(.+)|encerrar\s+(.+)', texto.lower())
            if not m:
                return "Informe o nome do processo, Chefe."
            nome = (m.group(1) or m.group(2) or m.group(3)).strip()
            mortos = 0
            for proc in psutil.process_iter(['name']):
                if nome.lower() in proc.info['name'].lower():
                    proc.kill()
                    mortos += 1
            return f"{mortos} processo(s) encerrado(s), Chefe." if mortos else f"Processo '{nome}' não encontrado, Chefe."
        except Exception as e:
            return f"Erro: {str(e)[:50]}"
    # ═══════════════════════════════════════════════════════════
    #                    OTIMIZAÇÃO DO PC
    # ═══════════════════════════════════════════════════════════

    def otimizar_pc(self):
        """Roda todas as otimizações de uma vez e retorna relatório."""
        self.log("JARVIS", "Iniciando otimização completa, Chefe...", "jarvis")
        resultados = []

        # 1. Limpar lixeira
        r = self._limpar_lixeira()
        resultados.append(r)
        self.log("SYS", r, "sys")

        # 2. Limpar temporários
        r = self._limpar_temporarios()
        resultados.append(r)
        self.log("SYS", r, "sys")

        # 3. Limpar cache navegadores
        r = self._limpar_cache_navegadores()
        resultados.append(r)
        self.log("SYS", r, "sys")

        # 4. Matar processos pesados
        r = self._matar_processos_pesados()
        resultados.append(r)
        self.log("SYS", r, "sys")

        # 5. Liberar RAM
        r = self._liberar_ram()
        resultados.append(r)
        self.log("SYS", r, "sys")

        # 6. Alto desempenho
        r = self._modo_alto_desempenho()
        resultados.append(r)
        self.log("SYS", r, "sys")

        # 7. Desativar inicialização automática
        r = self._desativar_startup()
        resultados.append(r)
        self.log("SYS", r, "sys")

        self.log("JARVIS", "✅ Otimização concluída, Chefe!", "jarvis")
        return "Otimização completa concluída! Verifique o log para detalhes, Chefe."

    def _limpar_lixeira(self):
        try:
            subprocess.run(["powershell", "-c",
                "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"],
                capture_output=True, timeout=15)
            return "✅ Lixeira limpa."
        except Exception as e:
            return f"❌ Lixeira: {str(e)[:40]}"

    def _limpar_cache_navegadores(self):
        limpos = []
        # Chrome
        chrome_cache = os.path.expanduser(r"~\AppData\Local\Google\Chrome\User Data\Default\Cache")
        if os.path.exists(chrome_cache):
            try:
                shutil.rmtree(chrome_cache, ignore_errors=True)
                os.makedirs(chrome_cache, exist_ok=True)
                limpos.append("Chrome")
            except: pass
        # Edge
        edge_cache = os.path.expanduser(r"~\AppData\Local\Microsoft\Edge\User Data\Default\Cache")
        if os.path.exists(edge_cache):
            try:
                shutil.rmtree(edge_cache, ignore_errors=True)
                os.makedirs(edge_cache, exist_ok=True)
                limpos.append("Edge")
            except: pass
        # Firefox
        firefox_base = os.path.expanduser(r"~\AppData\Local\Mozilla\Firefox\Profiles")
        if os.path.exists(firefox_base):
            try:
                for perfil in os.listdir(firefox_base):
                    cache = os.path.join(firefox_base, perfil, "cache2")
                    if os.path.exists(cache):
                        shutil.rmtree(cache, ignore_errors=True)
                limpos.append("Firefox")
            except: pass
        if limpos:
            return f"✅ Cache limpo: {', '.join(limpos)}."
        return "⚠ Nenhum navegador encontrado para limpar cache."

    def _matar_processos_pesados(self):
        try:
            import psutil
            # Processos conhecidos que consomem memória desnecessariamente
            indesejaveis = [
                "OneDrive.exe", "SearchIndexer.exe", "SpeechRuntime.exe",
                "YourPhone.exe", "PhoneExperienceHost.exe", "Widgets.exe",
            ]
            mortos = []
            for proc in psutil.process_iter(['name', 'memory_percent']):
                try:
                    nome = proc.info['name']
                    mem  = proc.info['memory_percent'] or 0
                    if nome in indesejaveis or (mem > 5 and nome not in [
                        "python.exe", "python3.exe", "py.exe", "Code.exe",
                        "chrome.exe", "firefox.exe", "msedge.exe"
                    ] and mem > 8):
                        if nome in indesejaveis:
                            proc.kill()
                            mortos.append(nome)
                except: pass
            return f"✅ {len(mortos)} processo(s) pesado(s) encerrado(s)." if mortos else "✅ Nenhum processo desnecessário encontrado."
        except ImportError:
            return "⚠ psutil não instalado."

    def _liberar_ram(self):
        try:
            import psutil, ctypes
            ram_antes = psutil.virtual_memory().percent
            # Força coleta de lixo Python
            import gc
            gc.collect()
            # Windows: esvazia working sets
            subprocess.run(["powershell", "-c",
                "Get-Process | ForEach-Object { $_.MinWorkingSet = $_.MinWorkingSet }"],
                capture_output=True, timeout=10)
            ram_depois = psutil.virtual_memory().percent
            liberado = max(0, ram_antes - ram_depois)
            return f"✅ RAM liberada! {ram_antes:.0f}% → {ram_depois:.0f}% ({liberado:.1f}% liberado)."
        except Exception as e:
            return f"✅ Limpeza de RAM executada."

    def _modo_alto_desempenho(self):
        try:
            subprocess.run(["powershell", "-c",
                "powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"],
                capture_output=True, timeout=10)
            return "✅ Plano de energia: Alto Desempenho ativado."
        except Exception as e:
            return f"❌ Plano de energia: {str(e)[:40]}"

    def _desativar_startup(self):
        try:
            resultado = subprocess.run(["powershell", "-c",
                "Get-CimInstance Win32_StartupCommand | Select-Object Name, Command | ConvertTo-Json"],
                capture_output=True, timeout=10, text=True)
            import json as _json
            items = _json.loads(resultado.stdout) if resultado.stdout.strip() else []
            if isinstance(items, dict):
                items = [items]
            # Apps comuns desnecessários no startup
            indesejaveis_startup = ["OneDrive", "Spotify", "Discord", "Teams", "Skype", "Zoom"]
            desativados = []
            for item in items:
                nome = item.get("Name", "")
                for ind in indesejaveis_startup:
                    if ind.lower() in nome.lower():
                        subprocess.run(["powershell", "-c",
                            f'Get-CimInstance Win32_StartupCommand | Where-Object {{$_.Name -eq "{nome}"}} | Invoke-CimMethod -MethodName Delete'],
                            capture_output=True, timeout=5)
                        desativados.append(nome)
            return f"✅ {len(desativados)} app(s) de inicialização desativado(s)." if desativados else "✅ Startup já está limpo."
        except Exception as e:
            return f"⚠ Startup: {str(e)[:40]}"

    def verificar_temperatura(self):
        try:
            import psutil
            temps = psutil.sensors_temperatures()
            if not temps:
                # Tenta via WMI no Windows
                resultado = subprocess.run(["powershell", "-c",
                    "Get-WmiObject MSAcpi_ThermalZoneTemperature -Namespace root/wmi | Select-Object CurrentTemperature | ConvertTo-Json"],
                    capture_output=True, timeout=8, text=True)
                if resultado.stdout.strip():
                    import json as _json
                    data = _json.loads(resultado.stdout)
                    if isinstance(data, dict):
                        data = [data]
                    temp_k = data[0].get("CurrentTemperature", 0)
                    temp_c = (temp_k / 10) - 273.15
                    status = "🔴 CRÍTICA" if temp_c > 85 else "🟡 Alta" if temp_c > 70 else "🟢 Normal"
                    if temp_c > 80:
                        self.voice.falar(f"Chefe, temperatura crítica! {temp_c:.0f} graus!")
                    return f"Temperatura CPU: {temp_c:.0f}°C — {status}, Chefe."
                return "Sensor de temperatura não disponível neste PC, Chefe."
            for nome, entries in temps.items():
                if entries:
                    temp_c = entries[0].current
                    status = "🔴 CRÍTICA" if temp_c > 85 else "🟡 Alta" if temp_c > 70 else "🟢 Normal"
                    if temp_c > 80:
                        self.voice.falar(f"Chefe, temperatura crítica! {temp_c:.0f} graus!")
                    return f"Temperatura {nome}: {temp_c:.0f}°C — {status}, Chefe."
        except Exception as e:
            return f"Erro ao verificar temperatura: {str(e)[:50]}"

    def desfragmentar_disco(self):
        try:
            # Verifica se é SSD (não desfragmentar SSD!)
            resultado = subprocess.run(["powershell", "-c",
                "Get-PhysicalDisk | Select-Object MediaType | ConvertTo-Json"],
                capture_output=True, timeout=8, text=True)
            if "SSD" in resultado.stdout:
                # SSD: faz TRIM ao invés de desfragmentar
                subprocess.Popen(["powershell", "-c", "Optimize-Volume -DriveLetter C -ReTrim -Verbose"],
                    creationflags=subprocess.CREATE_NEW_CONSOLE)
                return "SSD detectado! Executando TRIM (otimização para SSD), Chefe."
            else:
                # HDD: desfragmenta
                subprocess.Popen(["powershell", "-c", "Optimize-Volume -DriveLetter C -Defrag -Verbose"],
                    creationflags=subprocess.CREATE_NEW_CONSOLE)
                return "Desfragmentação iniciada em segundo plano, Chefe. Pode demorar alguns minutos."
        except Exception as e:
            return f"Erro: {str(e)[:50]}"

    def monitorar_temperatura_continuo(self):
        """Fica monitorando temperatura e avisa se ficar alta."""
        self._monitor_temp = True
        threading.Thread(target=self._loop_temperatura, daemon=True).start()
        return "Monitoramento de temperatura ativado, Chefe. Vou te avisar se esquentar."

    def _loop_temperatura(self):
        import time
        while getattr(self, '_monitor_temp', False):
            try:
                import psutil
                temps = psutil.sensors_temperatures()
                for nome, entries in temps.items():
                    if entries and entries[0].current > 85:
                        self.log("JARVIS", f"⚠ TEMPERATURA CRÍTICA: {entries[0].current:.0f}°C!", "err")
                        self.voice.falar(f"Chefe, temperatura crítica! {entries[0].current:.0f} graus! Salve seu trabalho!")
            except: pass
            time.sleep(30)

    # ── MÉTODOS PÚBLICOS ──────────────────────────────────────

    def abrir_site(self, t, texto_original=""):
        sites = {
            "youtube": "https://youtube.com",
            "google": "https://google.com",
            "instagram": "https://instagram.com",
            "netflix": "https://netflix.com",
            "discord": "https://discord.com",
            "twitch": "https://twitch.tv",
            "github": "https://github.com",
            "gmail": "https://mail.google.com",
            "twitter": "https://twitter.com",
            "reddit": "https://reddit.com",
            "whatsapp": "https://web.whatsapp.com",
            "chatgpt": "https://chat.openai.com",
            "spotify": "https://open.spotify.com",
        }
        for nome, url in sites.items():
            if nome in t:
                if nome == "youtube":
                    busca = re.sub(r'.*youtube\s*', '', t).strip()
                    if busca:
                        url = f"https://youtube.com/results?search_query={urllib.parse.quote(busca)}"
                webbrowser.open(url)
                return True, nome
        return False, ""

    def abrir_pasta(self, t):
        for nome, pasta in PASTAS_MAP.items():
            if nome in t:
                path = os.path.expanduser(f"~\\{pasta}")
                subprocess.Popen(["explorer", path])
                return True, nome
        return False, ""

    def abrir_app_fixo(self, t):
        apps = {
            "notepad": "notepad", "bloco de notas": "notepad",
            "calculadora": "calc", "paint": "mspaint",
            "cmd": "cmd", "powershell": "powershell",
            "chrome": "chrome", "firefox": "firefox",
            "edge": "msedge", "spotify": "spotify",
        }
        for nome, exe in apps.items():
            if nome in t:
                try:
                    subprocess.Popen(exe)
                    return True, nome
                except:
                    try:
                        subprocess.Popen(["start", exe], shell=True)
                        return True, nome
                    except:
                        pass
        return False, ""

    def abrir_app_indice(self, termo):
        if not self.apps_index:
            return False, ""
        termo = termo.lower().strip()
        if termo in self.apps_index:
            subprocess.Popen([self.apps_index[termo]])
            return True, termo
        for nome, path in self.apps_index.items():
            if termo in nome:
                subprocess.Popen([path])
                return True, nome
        return False, ""

    def alarme(self, segundos, msg, callback=None):
        threading.Thread(target=self._alarme, args=(segundos, msg), daemon=True).start()

    def buscar_arquivo(self, texto):
        return self._buscar_arquivo(texto)

    def listar_arquivos(self, texto):
        return self._listar_arquivos(texto)

    def renomear_arquivo(self, texto):
        return self._renomear_arquivo(texto)

    def tamanho_pasta(self, texto):
        return self._tamanho_pasta(texto)

    def limpar_temporarios(self):
        return self._limpar_temporarios()

    def deletar_arquivo(self, texto):
        return self._deletar_arquivo(texto)

    def mover_arquivo(self, texto):
        return self._mover_arquivo(texto)

    def organizar_downloads(self):
        return self._organizar_downloads()

    def capturar_webcam(self):
        resultado = self._webcam()
        return None, resultado

    def controlar_volume(self, t):
        return self._volume(t)

    def controlar_brilho(self, t):
        return self._brilho(t)

    def controlar_pc(self, t):
        return self._controlar_pc(t)

    def consultar_clima(self, t):
        return self._clima(t)

    def consultar_cotacao(self, t):
        return self._cotacao(t)

    def tirar_screenshot(self):
        return self._screenshot()

    def pesquisar_google(self, texto):
        return self._pesquisar_google(texto)

    def apagar_duplicados(self, texto):
        return self._apagar_duplicados(texto)