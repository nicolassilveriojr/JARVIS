import os
import subprocess
import re
import time
import sys
import webbrowser
import threading
import json
import urllib.parse

try:
    import cv2
except ImportError:
    cv2 = None

try:
    import pyautogui
except ImportError:
    pyautogui = None

try:
    import psutil
except ImportError:
    psutil = None

PASTAS_MAP = {
    "documentos": "Documents",
    "imagens": "Pictures",
    "downloads": "Downloads",
    "videos": "Videos",
    "musicas": "Music",
    "area de trabalho": "Desktop"
}

def detectar_pasta(texto):
    t = texto.lower()
    for nome, pasta in PASTAS_MAP.items():
        if nome in t:
            return os.path.expanduser(f"~\\{pasta}"), nome
    return None, None

class JarvisCommands:
    def __init__(self, brain, voice, log_fn, status_fn, memory):
        self.brain = brain
        self.voice = voice
        self.log = log_fn
        self.status = status_fn
        self.memory = memory
        self.apps_index = {}
        self.api_processes = {}
        self._indexar_apps()

    def _indexar_apps(self):
        """Indexa aplicativos instalados no Windows usando PowerShell"""
        try:
            ps_cmd = 'Get-ItemProperty HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*, HKLM:\\SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*, HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | Select-Object DisplayName, InstallLocation, DisplayIcon | ConvertTo-Json'
            res = subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, text=True)
            if res.stdout:
                apps = json.loads(res.stdout)
                for app in apps:
                    name = app.get("DisplayName")
                    if name:
                        self.apps_index[name.lower()] = app
        except: pass

    def processar(self, texto):
        match_cmd = re.search(r"\[\[CMD:(.*?)\]\]", texto)
        if match_cmd:
            cmd_string = match_cmd.group(1)
            return self._executar_estruturado(cmd_string)

        t = texto.lower().strip()
        palavras = t.split()
        
        if any(p in palavras for p in ["cpu", "ram", "memoria", "processador", "uso do pc"]):
            return self._status_sistema()
            
        if any(p in t for p in ["screenshot", "print", "captura de tela"]):
            return self._screenshot()

        if any(p in t for p in ["clima", "temperatura", "previsao", "chuva"]):
            return self._clima(t)
            
        if any(p in t for p in ["dolar", "bitcoin", "btc", "euro", "cotacao"]):
            return self._cotacao(t)

        return None

    def _executar_estruturado(self, cmd_string):
        try:
            parts = cmd_string.split("|")
            cmd_name = parts[0].strip()
            args = parts[1:] if len(parts) > 1 else []

            if cmd_name == "shell_exec":
                return self._shell_exec(args[0])
            elif cmd_name == "criar_projeto":
                return self._criar_projeto(args[0], args[1] if len(args) > 1 else "")
            elif cmd_name == "escrever_arquivo":
                return self._escrever_arquivo(args[0], args[1] if len(args) > 1 else "")
            elif cmd_name == "auto_update":
                return self._auto_update(args[0], args[1] if len(args) > 1 else "")
            elif cmd_name == "git_sync":
                return self._git_sync(args[0] if args else "Sincronização automática JARVIS")
            elif cmd_name == "ler_tela":
                return self._ler_tela()
            elif cmd_name == "webcam":
                return self._webcam()
            elif cmd_name == "status_sistema":
                return self._status_sistema()
            elif cmd_name == "abrir_app":
                return self._abrir_app(args[0])
            elif cmd_name == "aprender":
                return self._aprender(args[0], args[1])
            elif cmd_name == "buscar_memoria":
                return self._buscar_memoria(args[0])
            elif cmd_name == "novo_chat":
                self.memory.clear_conversation()
                return "Canais neurais resetados, Sir."
            elif cmd_name == "stark_booster":
                return self._stark_booster(args[0])
            
            return f"Comando '{cmd_name}' não reconhecido."
        except Exception as e:
            return f"Erro na execução estruturada: {e}"

    def _shell_exec(self, cmd):
        try:
            res = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True)
            out = res.stdout.strip() or res.stderr.strip()
            return f"Shell: {out[:500]}" if out else "Shell: Sucesso."
        except Exception as e:
            return f"Erro Shell: {e}"

    def _criar_projeto(self, tipo, descricao):
        try:
            base_dir = os.path.expanduser("~/Documents/JARVIS_PROJECTS")
            os.makedirs(base_dir, exist_ok=True)
            
            nome_sugerido = self.brain.responder(f"Sugira apenas UM nome curto para um projeto de: {descricao}")
            nome_limpo = re.sub(r'[^a-zA-Z0-9_-]', '', nome_sugerido).strip() or f"projeto_{int(time.time())}"
            
            proj_path = os.path.join(base_dir, nome_limpo)
            os.makedirs(proj_path, exist_ok=True)

            prompt = (
                f"Voce e um Arquiteto de Sistemas Lendario. Projete um sistema '{tipo}' para: '{descricao}'. "
                "Responda APENAS com arquivos no formato: FILE:nome\n[CONTEUDO]\n---END---"
            )
            codigo = self.brain.responder(prompt)
            
            arquivos = re.findall(r"FILE:(.*?)\n(.*?)\n---END---", codigo, re.DOTALL)
            for name, content in arquivos:
                f_path = os.path.join(proj_path, name.strip())
                os.makedirs(os.path.dirname(f_path), exist_ok=True)
                with open(f_path, "w", encoding="utf-8") as f:
                    f.write(content.strip())
            
            os.startfile(proj_path)
            return f"Projeto '{nome_limpo}' criado com {len(arquivos)} arquivos, Sir."
        except Exception as e:
            return f"Erro ao criar projeto: {e}"

    def _escrever_arquivo(self, path, conteudo):
        try:
            if not os.path.isabs(path):
                base_dir = os.path.expanduser("~/Documents/JARVIS_PROJECTS/STANDALONE")
                os.makedirs(base_dir, exist_ok=True)
                path = os.path.join(base_dir, path)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(conteudo.strip())
            return f"Arquivo '{os.path.basename(path)}' gerado, Sir."
        except Exception as e:
            return f"Erro ao escrever arquivo: {e}"

    def _git_sync(self, msg):
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            subprocess.run(f'git -C "{base_dir}" add .', shell=True)
            subprocess.run(f'git -C "{base_dir}" commit -m "{msg}"', shell=True)
            subprocess.run(f'git -C "{base_dir}" push origin main', shell=True)
            return f"Sincronia GitHub realizada: {msg}"
        except Exception as e:
            return f"Erro Git: {e}"

    def _status_sistema(self):
        if not psutil: return "Monitoramento offline."
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        return f"Sistemas a {cpu}% CPU e {ram}% RAM, Sir."

    def _screenshot(self):
        if not pyautogui: return "PyAutoGUI offline."
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(base_dir, "data", "temp", "screenshot.png")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        pyautogui.screenshot(path)
        os.startfile(path)
        return "Captura realizada, Sir."

    def _clima(self, t):
        import requests
        try:
            res = requests.get("https://api.open-meteo.com/v1/forecast?latitude=-23.55&longitude=-46.63&current_weather=true").json()
            temp = res['current_weather']['temperature']
            return f"Clima: {temp}°C, Sir."
        except: return "Clima instável, Sir."

    def _cotacao(self, t):
        import requests
        try:
            res = requests.get("https://economia.awesomeapi.com.br/last/USD-BRL,BTC-BRL").json()
            usd = res['USDBRL']['bid']
            return f"Dólar: R$ {float(usd):.2f}, Sir."
        except: return "Mercados fechados, Sir."

    def _stark_booster(self, modo):
        try:
            if modo == "game":
                subprocess.run("powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c", shell=True)
                return "Modo Gamer: Alto Desempenho ativado, Sir."
            return "Modo Booster desconhecido."
        except Exception as e:
            return f"Erro Booster: {e}"
            
    def _auto_update(self, path, content):
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            full_path = os.path.join(base_dir, path) if not os.path.isabs(path) else path
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content.strip())
            return f"Auto-Update: {path} reescrito."
        except Exception as e: return f"Erro Update: {e}"

    def _aprender(self, k, v):
        self.memory.learn(k, v)
        return f"Assimilado: {k}"

    def _buscar_memoria(self, q):
        mems = self.memory.recall(q)
        return "\n".join([f"{k}: {v}" for k, v in mems]) if mems else "Nada encontrado."
