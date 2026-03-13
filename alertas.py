import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import datetime

# Configurações - carregadas do .env
def _get_config():
    email = os.getenv("ALERT_EMAIL", "nicolas.free.firejr@gmail.com")
    senha = os.getenv("ALERT_SENHA", "knpe pxro uaax jlbp")
    destino = os.getenv("ALERT_DESTINO", "nicolas.free.firejr@gmail.com")
    return email, senha, destino

def enviar_alerta(assunto, mensagem, foto_path=None):
    try:
        email, senha, destino = _get_config()
        msg = MIMEMultipart()
        msg["From"]    = email
        msg["To"]      = destino
        msg["Subject"] = f"🚨 JARVIS ALERTA: {assunto}"

        corpo = f"""
J.A.R.V.I.S - Sistema de Segurança
====================================
⏰ {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

{mensagem}

-- STARK INDUSTRIES
        """
        msg.attach(MIMEText(corpo, "plain"))

        if foto_path and os.path.exists(foto_path):
            with open(foto_path, "rb") as f:
                img = MIMEImage(f.read())
                img.add_header("Content-Disposition", "attachment", filename="alerta.png")
                msg.attach(img)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(email, senha.replace(" ", ""))
            smtp.sendmail(email, destino, msg.as_string())
        return True
    except Exception as e:
        print(f"Erro ao enviar alerta: {e}")
        return False