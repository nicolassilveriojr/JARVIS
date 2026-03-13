# J.A.R.V.I.S — Mark VII

<div align="center">

![JARVIS](https://img.shields.io/badge/JARVIS-Mark%20VII-00d4e8?style=for-the-badge&logo=python&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)
![Status](https://img.shields.io/badge/Status-Online-00e096?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**Assistente de IA pessoal inspirado no JARVIS do Homem de Ferro.**  
Controle seu PC por voz ou texto, com interface futurista e inteligência artificial.

</div>

---

## ✨ Funcionalidades

- 🎤 **Reconhecimento de voz** em português brasileiro
- 🤖 **IA avançada** com Groq, Gemini e Grok
- 🖥️ **Interface futurista** com animação reativa ao áudio
- 📊 **Monitor de sistema** em tempo real (CPU, RAM, Disco)
- 🌦️ **Clima** atualizado automaticamente
- 🔒 **Segurança** com reconhecimento facial
- ⚡ **+50 comandos** para controlar tudo no PC

---

## 🚀 Comandos

<details>
<summary><b>⏰ Tempo e Lembretes</b></summary>

| Comando | Descrição |
|---|---|
| `que horas são` | Mostra a hora atual |
| `que dia é hoje` | Mostra a data |
| `alarme em X minutos para...` | Cria um lembrete |

</details>

<details>
<summary><b>💻 Hardware e Sistema</b></summary>

| Comando | Descrição |
|---|---|
| `hardware` / `cpu` / `ram` | Status do sistema |
| `bateria` | Nível da bateria |
| `temperatura` | Temperatura do PC |
| `listar processos` | Processos rodando |
| `matar processo X` | Encerra um processo |

</details>

<details>
<summary><b>⚡ Otimização</b></summary>

| Comando | Descrição |
|---|---|
| `otimizar pc` | Faz tudo de uma vez |
| `limpar lixeira` | Esvazia a lixeira |
| `liberar ram` | Libera memória RAM |
| `limpar cache` | Limpa cache dos navegadores |
| `alto desempenho` | Ativa modo desempenho |
| `desfragmentar disco` | Otimiza o disco |

</details>

<details>
<summary><b>🎮 Modos Especiais</b></summary>

| Comando | Descrição |
|---|---|
| `modo jogo` | Otimiza para jogos |
| `modo noturno` | Brilho baixo + volume baixo |
| `modo foco por X minutos` | Timer de foco |
| `modo segurança` | Trava com reconhecimento facial |
| `protocolo emergência` | Monitora câmera + alerta por email |

</details>

<details>
<summary><b>🌐 Internet e Sites</b></summary>

| Comando | Descrição |
|---|---|
| `pesquisar X` | Pesquisa no Google |
| `clima` | Previsão do tempo |
| `dólar` / `bitcoin` / `euro` | Cotações |
| `abrir youtube` | Abre o YouTube |
| `abrir spotify` | Abre o Spotify |
| + YouTube, Instagram, Netflix, Discord, Twitch, GitHub, Gmail, Twitter, Reddit, WhatsApp, ChatGPT... | |

</details>

<details>
<summary><b>📁 Arquivos</b></summary>

| Comando | Descrição |
|---|---|
| `buscar X` | Encontra um arquivo |
| `deletar X` | Apaga um arquivo |
| `mover X para Y` | Move arquivo |
| `organizar downloads` | Organiza a pasta Downloads |
| `criar arquivo X` | Cria um novo arquivo |

</details>

<details>
<summary><b>🤖 Inteligência Artificial</b></summary>

| Comando | Descrição |
|---|---|
| Qualquer pergunta | Responde com IA |
| `traduzir X` | Traduz texto |
| `analisar tela` | Descreve o que está na tela |
| `webcam` | Tira foto e descreve com IA |
| `relatório` | Status geral do sistema |

</details>

---

## 🛠️ Instalação

**1. Clone o repositório**
```bash
git clone https://github.com/nicolassilveriojr/JARVIS.git
cd JARVIS
```

**2. Instale as dependências**
```bash
pip install customtkinter speechrecognition gtts pygame pyttsx3 google-genai openai python-dotenv opencv-python pyautogui Pillow psutil plyer edge-tts numpy pyaudio
```

**3. Configure as APIs**

Crie um arquivo `.env` na raiz do projeto:
```
GROQ_API_KEY=sua_chave_aqui
GEMINI_API_KEY=sua_chave_aqui
GROK_API_KEY=sua_chave_aqui
```

> Obtenha sua chave Groq gratuitamente em [console.groq.com](https://console.groq.com)

**4. Rode**
```bash
py -3.12 main.py
```

---

## 🧠 Tecnologias

| Tecnologia | Uso |
|---|---|
| Python 3.12 | Linguagem principal |
| Groq + LLaMA 3.3 70B | IA principal (grátis) |
| Google Gemini | IA alternativa |
| Grok | IA alternativa |
| Edge TTS | Voz pt-BR natural |
| CustomTkinter | Interface gráfica |
| OpenCV | Reconhecimento facial |
| psutil | Monitor de sistema |
| pyaudio | Áudio reativo |

---

## 📋 Requisitos

- Windows 10/11
- Python 3.12+
- Microfone
- Conexão com internet

---

<div align="center">

**Desenvolvido por [Nicolas](https://github.com/nicolassilveriojr)**

*"Bem-vindo, Chefe. Todos os sistemas operacionais."*

</div>
