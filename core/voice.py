import os
import threading
import asyncio

try:
    import edge_tts
except ImportError:
    edge_tts = None

try:
    import pygame
except ImportError:
    pygame = None

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

try:
    import speech_recognition as sr
except ImportError:
    sr = None

# Voz do JARVIS - masculina, sofisticada em ingles
JARVIS_VOICE = "pt-BR-AntonioNeural"


class JarvisVoice:
    def __init__(self, on_speaking=None, on_done=None, on_status=None):
        self.on_speaking = on_speaking or (lambda: None)
        self.on_done     = on_done     or (lambda: None)
        self.on_status   = on_status   or (lambda s, c: None)
        self.speaking    = False
        self.listening   = False

    def falar(self, texto):
        if not texto:
            return
        self.speaking = True
        self.on_speaking()
        try:
            if edge_tts and pygame:
                asyncio.run(self._falar_edge(texto))
            elif pyttsx3:
                self._falar_pyttsx3(texto)
        except Exception as e:
            print("Voz erro:", e)
            try:
                self._falar_pyttsx3(texto)
            except:
                pass
        finally:
            self.speaking = False
            self.on_done()

    async def _falar_edge(self, texto):
        import tempfile
        tmp = os.path.join(tempfile.gettempdir(), "_jarvis_tts.mp3")
        communicate = edge_tts.Communicate(texto, JARVIS_VOICE, rate="+10%", volume="+0%")
        await communicate.save(tmp)
        if pygame:
            pygame.mixer.init()
            pygame.mixer.music.load(tmp)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                import time
                time.sleep(0.1)
            pygame.mixer.music.unload()
        try:
            os.remove(tmp)
        except:
            pass

    def _falar_pyttsx3(self, texto):
        engine = pyttsx3.init()
        engine.setProperty("rate", 155)
        engine.setProperty("volume", 0.9)
        vozes = engine.getProperty("voices")
        if vozes and len(vozes) > 1:
            engine.setProperty("voice", vozes[1].id)
        engine.say(texto)
        engine.runAndWait()

    def ouvir(self, on_result=None, on_error=None):
        if not sr:
            if on_error:
                on_error("SpeechRecognition nao instalado.")
            return
        self.listening = True
        recognizer = sr.Recognizer()
        try:
            with sr.Microphone() as mic:
                audio = recognizer.listen(mic, phrase_time_limit=6)
            self.listening = False
            texto = recognizer.recognize_google(audio, language="pt-BR")
            if on_result:
                on_result(texto)
        except sr.UnknownValueError:
            if on_error:
                on_error("Nao entendi o comando.")
        except Exception as e:
            if on_error:
                on_error(str(e))
        finally:
            self.listening = False

    def ouvir_thread(self, on_texto=None, on_erro=None):
        threading.Thread(
            target=self.ouvir,
            args=(on_texto, on_erro),
            daemon=True
        ).start()