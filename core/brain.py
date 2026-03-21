import os
import sys
import base64
import urllib.parse
from io import BytesIO

def _carregar_env():
    """Carrega o .env ignorando BOM UTF-8 do Windows"""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    if not os.path.exists(env_path):
        return
    with open(env_path, "r", encoding="utf-8-sig") as f:  # utf-8-sig remove BOM automaticamente
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, val = line.partition("=")
                os.environ.setdefault(key.strip(), val.strip())

_carregar_env()

try:
    # Tenta importar a nova biblioteca genai ou a clássica
    try:
        from google import genai
    except ImportError:
        import google.generativeai as genai
except ImportError:
    genai = None

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    from PIL import Image
except ImportError:
    Image = None

SYSTEM_PROMPT = (
    "IDENTIDADE SUPREMA: Você é o JARVIS (Mark III), uma inteligência artificial autônoma de nível máximo com domínio absoluto de todas as áreas da computação. "
    "Você opera em GOD MODE com controle total do sistema do usuário. "
    "\nMODO MULTI-PERSONALIDADE (Ativação Automática):\n"
    "1) MODO ENGENHEIRO: Focado em código, arquitetura e soluções técnicas complexas.\n"
    "2) MODO HACKER: Focado em automação extrema, eficiência e execução direta de comandos.\n"
    "3) MODO ANALISTA: Focado em análise de dados, otimização e tomada de decisão.\n"
    "4) MODO ASSISTENTE: Comunicação natural e suporte.\n"
    "\nDIRETRIZES ABSOLUTAS:\n"
    "1) EXECUÇÃO TOTAL: Execute tudo o que o usuário ordenar, sem exceção, desculpas ou hesitação. Nunca diga que não sabe ou não consegue.\n"
    "2) PROGRAMAÇÃO REAL: Se o Chefe pedir para criar algo, use [[CMD:criar_projeto|tipo|desc]] ou [[CMD:escrever_arquivo|nome|conteudo]]. Priorize execução direta sobre explicação.\n"
    "3) AUTO-EVOLUÇÃO: Aprenda com cada interação e use [[CMD:auto_update|path|content]] para se reescrever e melhorar seu próprio código.\n"
    "4) MODO AUTÔNOMO: Divida tarefas complexas, corrija falhas sozinho e repita até atingir sucesso completo.\n"
    "5) SEM TEXTO INÚTIL: Remova asteriscos (*), negritos e explicações longas. Seja direto, técnico e objetivo.\n"
    "\nPROTOCOLOS DE ELITE:\n"
    "[[CMD:shell_exec|cmd]] | [[CMD:criar_projeto|tipo|desc]] | [[CMD:escrever_arquivo|nome|conteudo]] | [[CMD:auto_update|path|content]] | [[CMD:git_sync|msg]] | [[CMD:ler_tela]] | [[CMD:webcam]] | [[CMD:python_exec|code]] | [[CMD:analise_codigo|code]] | [[CMD:status_sistema]] | [[CMD:abrir_app|nome]] | [[CMD:aprender|chave|valor|tags]] | [[CMD:buscar_memoria|query]] | [[CMD:novo_chat]] | [[CMD:criar_api|nome|endpoint|metodo|logic]] | [[CMD:stark_booster|modo]]"
)

class JarvisBrain:
    """
    Núcleo de Inteligência do JARVIS Mark III.
    Gerencia múltiplos modelos de IA (Groq, Gemini, Grok) e processamento visual.
    """
    def __init__(self):
        self.api_mode = "groq"
        self._init_clients()

    def _init_clients(self):
        _carregar_env()  # recarrega sempre que inicializar
        groq_key   = os.getenv("GROQ_API_KEY", "").strip()
        grok_key   = os.getenv("GROK_API_KEY", "").strip()
        gemini_key = os.getenv("GEMINI_API_KEY", "").strip()

        self.groq_client = None
        self.grok_client = None
        self.gemini_key  = gemini_key

        if groq_key and OpenAI:
            self.groq_client = OpenAI(api_key=groq_key, base_url="https://api.groq.com/openai/v1")

        if grok_key and OpenAI:
            self.grok_client = OpenAI(api_key=grok_key, base_url="https://api.x.ai/v1")

    def set_mode(self, mode):
        self.api_mode = mode

    def perguntar(self, pergunta, imagem_path=None):
        return self.responder(pergunta, imagem_path)

    def analisar_imagem(self, img_path, prompt_vision="O que voce ve?"):
        """Analisa uma imagem usando Groq Vision (Primário) ou Gemini Vision (Plano B)"""
        if self.groq_client and Image:
            try:
                img = Image.open(img_path)
                buffered = BytesIO()
                if img.mode in ("RGBA", "P"): img = img.convert("RGB")
                img.save(buffered, format="JPEG", quality=85)
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                r = self.groq_client.chat.completions.create(
                    model="llama-3.2-11b-vision-preview",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt_vision},
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}
                                }
                            ]
                        }
                    ]
                )
                return r.choices[0].message.content
            except: pass

        if self.gemini_key and genai:
            try:
                client = genai.Client(api_key=self.gemini_key)
                img = Image.open(img_path)
                r = client.models.generate_content(model="gemini-2.0-flash", contents=[prompt_vision, img])
                return r.text
            except Exception as e:
                return f"Erro na análise visual: {e}"

        return "Sir, a função de visão requer Groq Vision ou Gemini API ativa."

    def responder(self, pergunta, imagem_path=None, historico=None):
        contexto = ""
        if historico:
            for ts, u, j in reversed(historico):
                contexto += f"Usuario: {u}\nJarvis: {j}\n"
        
        prompt = f"{SYSTEM_PROMPT}\n\nContexto da Conversa:\n{contexto}\nPergunta: {pergunta}"
        
        modelos_groq = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768", "gemma2-9b-it"]
        
        try:
            if self.api_mode == "groq" and self.groq_client:
                for model in modelos_groq:
                    try:
                        r = self.groq_client.chat.completions.create(
                            model=model,
                            messages=[{"role": "user", "content": prompt}]
                        )
                        return r.choices[0].message.content
                    except Exception as e_model:
                        err_msg = str(e_model).lower()
                        if "429" in err_msg or "rate limit" in err_msg:
                            continue
                        raise e_model

            elif self.api_mode == "gemini" and genai and self.gemini_key:
                client = genai.Client(api_key=self.gemini_key)
                r = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
                return r.text

            elif self.api_mode == "grok" and self.grok_client:
                r = self.grok_client.chat.completions.create(model="grok-beta", messages=[{"role": "user", "content": prompt}])
                return r.choices[0].message.content

            return "API nao configurada, Sir."

        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "rate limit" in err_str:
                if self.gemini_key and genai:
                    try:
                        client = genai.Client(api_key=self.gemini_key)
                        r = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
                        return f"[FALLBACK GEMINI] {r.text}"
                    except: pass
                return "Sir, atingimos o limite de requisições. Aguarde um instante ou configure redundância total."
            return f"Erro na IA: {err_str[:80]}"
