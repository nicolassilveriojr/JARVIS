import os
import sys
import threading
import time
import re
from dotenv import load_dotenv

# Carrega configurações
_env = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(_env, override=True)

# Importa componentes
from core.memory import JarvisMemory
from core.brain import JarvisBrain
from core.voice import JarvisVoice
from core.commands import JarvisCommands
from core.api_core import JarvisCoreAPI
from ui.interface import JarvisUI
from utils.helpers import corrigir_texto

class JARVIS:
    def __init__(self):
        # Inicializa componentes
        self.brain = JarvisBrain()
        self.memory = JarvisMemory()
        self.voice = JarvisVoice()
        
        # Interface
        self.ui = JarvisUI(
            on_command=self._processar,
            on_listen=self._ouvir_thread,
        )
        self.commands = JarvisCommands(
            brain=self.brain, 
            voice=self.voice,
            log_fn=self.ui.log,
            status_fn=self.ui.set_status,
            memory=self.memory
        )

        # Inicializa a API Core do JARVIS
        self.api_core = JarvisCoreAPI(self)
        self.api_url = self.api_core.run(port=8008)
        if self.api_url:
            self.ui.log("SYS", f"API Core ativa: {self.api_url}", "sys")

        # Define callbacks para a interface
        self.ui.on_set_api = self.brain.set_mode
        self.ui.on_new_chat = self.memory.clear_conversation
        
        # Log inicial
        self.ui.log("SYS", "JARVIS Mark III Online", "sys")
        self.ui.log("SYS", "Sincronia Neural com Trae Architect estabelecida.", "sys")

    def _ouvir_thread(self):
        """Thread para ouvir voz sem travar a UI"""
        def listen():
            texto = self.voice.ouvir()
            if texto:
                self.ui.input_field.delete(0, 'end')
                self.ui.input_field.insert(0, texto)
                self._processar(texto)
        threading.Thread(target=listen, daemon=True).start()

    def _processar(self, texto):
        """Processa comandos do usuário com Execução Absoluta e Limpeza de Voz"""
        try:
            if self.voice.speaking:
                self.voice.parar_fala()
                self.ui.log("SYS", "Interrupção detectada.", "sys")

            self.ui.set_status("● PROCESSANDO", "#FFB300")
            
            # Auto-Correção
            if any(p in texto.lower() for p in ["arruma o erro", "corrigir erro", "fix error"]):
                erro_recente = self.memory.get_recent(limit=5, category='error')
                if erro_recente:
                    self.ui.log("SYS", "Auto-Correção Iniciada...", "sys")
                    prompt_fix = f"Ocorreu este erro: {erro_recente[0][2]}. Analise e corrija se for um comando ou arquivo."
                    resp_fix = self.brain.responder(prompt_fix)
                    self.commands.processar(resp_fix)
                    return

            texto_corrigido = corrigir_texto(texto)
            t = texto_corrigido.lower().strip()
            
            def responder(msg):
                if not msg: return
                # Limpeza de Voz (Remove asteriscos, etc)
                msg_voz = re.sub(r"[\*\_\#\>\`\-\[\]]", "", msg).strip()
                msg_voz = re.sub(r"\[\[CMD:.*?\]\]", "", msg_voz).strip()
                
                if msg_voz:
                    self.ui.log("JARVIS", msg, "jarvis")
                    self.voice.falar(msg_voz, prioritario=True)
                
                match = re.search(r"\[\[CMD:(.*?)\]\]", msg)
                if match:
                    try:
                        cmd_res = self.commands.processar(msg)
                        if cmd_res:
                            self.ui.log("SYS", cmd_res, "sys")
                            self.voice.falar(cmd_res)
                    except Exception as e_cmd:
                        self.ui.log("SYS", f"Erro: {e_cmd}", "err")
                        self.memory.save(f"CMD_ERROR: {msg}", str(e_cmd), category='error')
                
                self.ui.set_status("● STANDBY", "#FF6D00")

            # Memória Semântica (Recall)
            mems = self.memory.recall(t)
            if mems and any(p in t for p in ["quem é", "o que é", "lembra"]):
                contexto_memoria = "\n".join([f"{k}: {v}" for k, v in mems])
                resp_ia = self.brain.responder(f"Com base nestas memórias: {contexto_memoria}, responda: {texto}")
                if resp_ia:
                    responder(resp_ia)
                    self.memory.save(texto, resp_ia)
                    return

            # Execução Direta
            historico = self.memory.get_recent(limit=10)
            resp_ia = self.brain.responder(texto, historico=historico)
            if resp_ia:
                responder(resp_ia)
                self.memory.save(texto, resp_ia)

        except Exception as e:
            self.ui.log("SYS", f"Erro crítico: {e}", "err")
            self.ui.set_status("● ERRO", "#F44336")

    def iniciar(self):
        self.ui.root.mainloop()

if __name__ == "__main__":
    app = JARVIS()
    app.iniciar()
