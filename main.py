import threading
import os
import sys
import re

_env = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
from dotenv import load_dotenv
load_dotenv(_env, override=True)

from core.memory import JarvisMemory
from core.brain import JarvisBrain
from core.voice import JarvisVoice
from core.commands import JarvisCommands
from ui.interface import JarvisUI
from utils.helpers import corrigir_texto


class JARVIS:
    def __init__(self):
        self.brain  = JarvisBrain()
        self.memory = JarvisMemory()

        self.ui = JarvisUI(
            on_command = self._processar,
            on_listen  = self._ouvir_thread,
        )
        self.voice = JarvisVoice(
            on_speaking = lambda: self.ui.set_status("◈ FALANDO", "#FF6D00"),
            on_done     = lambda: self.ui.set_status("● STANDBY", "#FF6D00"),
        )
        self.commands = JarvisCommands(
            brain     = self.brain,
            voice     = self.voice,
            log_fn    = self.ui.log,
            status_fn = self.ui.set_status,
        )

        # Saudação ao iniciar
        import datetime
        _hora = datetime.datetime.now().hour
        if _hora < 12:
            _saudacao = "Bom dia, Chefe! Sistemas online e prontos para servir."
        elif _hora < 18:
            _saudacao = "Boa tarde, Chefe! Todos os sistemas operacionais."
        else:
            _saudacao = "Boa noite, Chefe! JARVIS à sua disposição."
        self.ui.log("JARVIS", _saudacao, "jarvis")
        threading.Thread(target=self.voice.falar, args=(_saudacao,), daemon=True).start()

    def _falar(self, texto):
        threading.Thread(target=self.voice.falar, args=(texto,), daemon=True).start()

    def _ouvir_thread(self):
        self.ui.set_status("● OUVINDO", "#D32F2F")
        self.ui.listening = True
        def on_result(texto):
            self.ui.listening = False
            self.ui.log("VOCÊ", texto, "user")
            threading.Thread(target=self._processar, args=(texto,), daemon=True).start()
        def on_error(msg):
            self.ui.listening = False
            self.ui.log("SYS", msg, "sys")
            self.ui.set_status("● STANDBY", "#FF6D00")
        self.voice.ouvir(on_result=on_result, on_error=on_error)

    def _processar(self, texto):
        self.ui.set_status("● PROCESSANDO", "#FFB300")

        texto_corrigido = corrigir_texto(texto)
        if texto_corrigido != texto.lower():
            self.ui.log("SYS", f"Entendido: {texto_corrigido}", "sys")

        t = texto_corrigido.lower().strip()
        cmd = self.commands

        def responder(msg):
            self.ui.log("JARVIS", msg, "jarvis")
            self._falar(msg)
            self.ui.set_status("● STANDBY", "#FF6D00")

        if any(p in t for p in ["lembrar", "alarme", "lembrete", "alerta"]):
            m = re.search(r'(\d+)\s*(minuto|segundo|hora|min|seg|h)', t)
            if m:
                val, un = int(m.group(1)), m.group(2)
                mins = val / 60 if "seg" in un else val * 60 if "hor" in un or un == "h" else val
                msg_lembrete = re.sub(r'\d+\s*(minuto|segundo|hora|min|seg|h)s?', '', texto).strip() or "Lembrete"
                cmd.alarme(int(mins * 60), msg_lembrete,
                    callback=lambda msg: (self.ui.log("JARVIS", f"ALARME: {msg}", "jarvis"), self._falar(f"Chefe, seu lembrete: {msg}")))
                return responder(f"Alarme definido para {int(mins)} minutos, Chefe.")

        if any(p in t for p in ["horas", "hora", "que horas"]):
            return responder(cmd.contar_hora())
        if any(p in t for p in ["data", "dia de hoje", "que dia"]):
            return responder(cmd.contar_data())
        if any(p in t for p in ["bateria", "carga"]):
            return responder(cmd.status_bateria())
        if any(p in t for p in ["hardware", "cpu", "ram", "memoria", "processador", "desempenho", "temperatura"]):
            return responder(cmd.monitorar_hardware())
        if any(p in t for p in ["reconhecer rosto", "detectar rosto", "quem esta"]):
            return responder(cmd.reconhecer_rosto())
        if any(p in t for p in ["modo seguranca", "modo segurança", "ativar seguranca"]):
            return responder(cmd.modo_seguranca(True))
        if any(p in t for p in ["desativar seguranca", "desativar segurança"]):
            cmd._modo_seguranca = False
            return responder("Modo de segurança desativado, Chefe.")
        if any(p in t for p in ["notificar", "notificacao", "notificação"]):
            return responder(cmd.notificar("J.A.R.V.I.S", texto))
        if any(p in t for p in ["meu ip", "ip da rede", "info rede"]):
            return responder(cmd.info_rede())
        if any(p in t for p in ["testar internet", "velocidade internet", "ping"]):
            return responder(cmd.testar_internet())
        if any(p in t for p in ["listar processos", "o que esta rodando"]):
            return responder(cmd.listar_processos())
        if any(p in t for p in ["matar processo", "fechar processo", "encerrar processo"]):
            return responder(cmd.matar_processo(t))
        if any(p in t for p in ["duplicado", "duplicados", "repetido"]):
            return responder(cmd.apagar_duplicados(texto))
        if any(p in t for p in ["buscar", "procurar", "onde esta", "onde está", "achar", "encontrar"]) and "google" not in t:
            return responder(cmd.buscar_arquivo(texto))
        if any(p in t for p in ["listar", "mostrar arquivos", "quais arquivos"]):
            return responder(cmd.listar_arquivos(texto))
        if any(p in t for p in ["renomear", "renomeia", "mudar nome"]):
            return responder(cmd.renomear_arquivo(texto))
        if any(p in t for p in ["tamanho", "quanto ocupa", "espaco", "espaço"]):
            return responder(cmd.tamanho_pasta(texto))
        if any(p in t for p in ["limpar temporario", "limpar temp", "arquivos temporarios"]):
            return responder(cmd.limpar_temporarios())
        if any(p in t for p in ["deletar", "apagar", "excluir", "remover"]):
            return responder(cmd.deletar_arquivo(texto))
        if any(p in t for p in ["mover", "transferir", "copiar"]):
            return responder(cmd.mover_arquivo(texto))
        if any(p in t for p in ["organizar", "arrumar"]) and "download" in t:
            return responder(cmd.organizar_downloads())
        if any(p in t for p in ["webcam", "camera", "câmera"]):
            caminho, erro = cmd.capturar_webcam()
            if erro:
                return responder(erro)
            resp = self.brain.responder("O que voce ve nessa imagem?", caminho)
            try: os.remove(caminho)
            except: pass
            return responder(resp)
        if any(p in t for p in ["volume", "som"]):
            return responder(cmd.controlar_volume(t))
        if any(p in t for p in ["brilho"]):
            return responder(cmd.controlar_brilho(t))
        if any(p in t for p in ["desligar", "reiniciar", "bloquear", "hibernar"]):
            return responder(cmd.controlar_pc(t))
        if any(p in t for p in ["clima", "temperatura", "previsao", "previsão", "chuva"]):
            return responder(cmd.consultar_clima(t))
        if any(p in t for p in ["dolar", "dólar", "bitcoin", "btc", "cotacao", "euro"]):
            return responder(cmd.consultar_cotacao(t))
        if any(p in t for p in ["screenshot", "print", "captura de tela"]):
            return responder(cmd.tirar_screenshot())
        if any(p in t for p in ["pesquisar", "pesquisa", "buscar no google"]):
            return responder(cmd.pesquisar_google(texto))

        # ── OTIMIZAÇÃO ──
        if any(p in t for p in ["otimizar", "otimiza", "limpar pc", "melhorar pc", "deixar rapido"]):
            return responder(cmd.otimizar_pc())

        if any(p in t for p in ["limpar lixeira", "esvaziar lixeira"]):
            return responder(cmd._limpar_lixeira())

        if any(p in t for p in ["limpar cache", "cache navegador"]):
            return responder(cmd._limpar_cache_navegadores())

        if any(p in t for p in ["liberar ram", "liberar memoria", "limpar ram"]):
            return responder(cmd._liberar_ram())

        if any(p in t for p in ["alto desempenho", "modo desempenho", "plano energia"]):
            return responder(cmd._modo_alto_desempenho())

        if any(p in t for p in ["temperatura", "temp do pc", "pc esquentando"]):
            return responder(cmd.verificar_temperatura())

        if any(p in t for p in ["monitorar temperatura", "monitorar temp"]):
            return responder(cmd.monitorar_temperatura_continuo())

        if any(p in t for p in ["desfragmentar", "desfrag", "otimizar disco"]):
            return responder(cmd.desfragmentar_disco())

        if any(p in t for p in ["startup", "inicializacao", "programas inicialização", "desativar startup"]):
            return responder(cmd._desativar_startup())

        if any(p in t for p in ["processos pesados", "matar processos", "limpar processos"]):
            return responder(cmd._matar_processos_pesados())

        # ── MODO JOGO ──
        if any(p in t for p in ["modo jogo", "ativar jogo", "modo game"]):
            return responder(cmd.modo_jogo(True))
        if any(p in t for p in ["desativar jogo", "sair do jogo"]):
            return responder(cmd.modo_jogo(False))

        # ── MODO NOTURNO ──
        if any(p in t for p in ["modo noturno", "modo escuro", "ativar noturno"]):
            return responder(cmd.modo_noturno(True))
        if any(p in t for p in ["desativar noturno", "sair do noturno"]):
            return responder(cmd.modo_noturno(False))

        # ── MODO FOCO ──
        if any(p in t for p in ["modo foco", "ativar foco", "foco por"]):
            return responder(cmd.modo_foco(texto, True))

        # ── DESCREVER IMAGEM ──
        if any(p in t for p in ["descrever imagem", "descreva imagem", "o que tem na imagem"]):
            return responder(cmd.descrever_imagem())

        # ── MEMÓRIA ──
        if any(p in t for p in ["lembra", "memoria", "memória", "voce disse", "eu disse"]):
            return responder(cmd.lembrar(texto))

        # ── ANALISAR TELA ──
        if any(p in t for p in ["analisar tela", "o que tem na tela", "descrever tela", "ver tela"]):
            return responder(cmd.analisar_tela())

        # ── PROTOCOLO EMERGÊNCIA ──
        if any(p in t for p in ["protocolo emergencia", "protocolo de emergencia", "emergencia"]):
            return responder(cmd.protocolo_emergencia(True))
        if any(p in t for p in ["desativar emergencia", "cancelar emergencia"]):
            return responder(cmd.protocolo_emergencia(False))

        # ── TRADUZIR ──
        if any(p in t for p in ["traduzir", "traduz", "traducao", "tradução"]):
            return responder(cmd.traduzir(texto))

        # ── CRIAR ARQUIVO ──
        if any(p in t for p in ["criar arquivo", "criar documento", "novo arquivo"]):
            return responder(cmd.criar_arquivo(texto))

        # ── ANALISAR SITE ──
        if any(p in t for p in ["analisar site", "resumir site", "resume esse site"]):
            return responder(cmd.analisar_site(texto))

        # ── RELATÓRIO DIÁRIO ──
        if any(p in t for p in ["relatorio", "relatório", "status geral"]):
            return responder(cmd.relatorio_diario())

        # ── CONTROLAR JANELAS ──
        if any(p in t for p in ["minimizar", "maximizar janela", "fechar janela"]):
            return responder(cmd.controlar_janela(texto))

        ok, site = cmd.abrir_site(t, texto)
        if ok:
            return responder(f"Abrindo {site}, Chefe.")

        if any(p in t for p in ["abrir", "abre", "acessa"]):
            ok, nome = cmd.abrir_pasta(t)
            if ok:
                return responder(f"Abrindo {nome}, Chefe.")

        ok, app = cmd.abrir_app_fixo(t)
        if ok:
            return responder(f"Abrindo {app}, Chefe.")

        if any(p in t for p in ["abrir", "abre", "abra", "iniciar", "acessar"]):
            termo = t
            for p in ["abrir", "abre", "abra", "iniciar", "acessar"]:
                termo = termo.replace(p, "").strip()
            ok, nome = cmd.abrir_app_indice(termo)
            if ok:
                return responder(f"Abrindo {nome}, Chefe.")

        resp = self.brain.responder(texto)
        if resp:
            self.ui.log("JARVIS", resp, "jarvis")
            self._falar(resp)
            self.memory.save(texto, resp)
        self.ui.set_status("● STANDBY", "#FF6D00")

    def run(self):
        self.ui.mainloop()


if __name__ == "__main__":
    jarvis = JARVIS()
    jarvis.run()