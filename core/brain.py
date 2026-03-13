import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"), override=True)
except ImportError:
    pass

try:
    from google import genai
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
    "Voce e o JARVIS do Homem de Ferro. "
    "Regras obrigatorias: "
    "1) Responda SEMPRE em portugues do Brasil. "
    "2) NUNCA faca perguntas ao usuario. "
    "3) NUNCA mude de assunto. "
    "4) Responda APENAS o que foi perguntado, de forma curta e direta. "
    "5) Chame o usuario de Chefe ou Sir. "
    "6) Seja sofisticado e levemente sarcastico como o JARVIS do filme. "
    "7) Se nao souber algo, diga que nao sabe sem perguntar nada. "
    "8) NUNCA ofereca ajuda adicional ou sugestoes nao pedidas. "
    "9) Maximo de 2 frases por resposta."
)


class JarvisBrain:
    def __init__(self):
        self.api_mode = "groq"
        self._init_clients()

    def _init_clients(self):
        load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"), override=True)
        groq_key  = os.getenv("GROQ_API_KEY", "")
        grok_key  = os.getenv("GROK_API_KEY", "")
        gemini_key = os.getenv("GEMINI_API_KEY", "")

        self.groq_client  = None
        self.grok_client  = None
        self.gemini_key   = gemini_key

        if groq_key and OpenAI:
            self.groq_client = OpenAI(api_key=groq_key, base_url="https://api.groq.com/openai/v1")

        if grok_key and OpenAI:
            self.grok_client = OpenAI(api_key=grok_key, base_url="https://api.x.ai/v1")

    def set_mode(self, mode):
        self.api_mode = mode

    def perguntar(self, pergunta, imagem_path=None):
        return self.responder(pergunta, imagem_path)

    def responder(self, pergunta, imagem_path=None):
        prompt = SYSTEM_PROMPT + " Pergunta: " + pergunta
        try:
            if self.api_mode == "groq" and self.groq_client:
                r = self.groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}]
                )
                return r.choices[0].message.content

            elif self.api_mode == "gemini" and genai and self.gemini_key:
                client = genai.Client(api_key=self.gemini_key)
                if imagem_path and Image:
                    img = Image.open(imagem_path)
                    r = client.models.generate_content(model="gemini-2.0-flash", contents=[prompt, img])
                else:
                    r = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
                return r.text

            elif self.api_mode == "grok" and self.grok_client:
                r = self.grok_client.chat.completions.create(
                    model="grok-beta",
                    messages=[{"role": "user", "content": prompt}]
                )
                return r.choices[0].message.content

            else:
                return "API nao configurada, Chefe. Verifique o arquivo .env."

        except Exception as e:
            return f"Erro na IA: {str(e)[:80]}"