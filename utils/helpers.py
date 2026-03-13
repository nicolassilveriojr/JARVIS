from difflib import SequenceMatcher

# Dicionário de correções de digitação
CORRECOES = {
    "abrri": "abrir", "abri": "abrir", "abre": "abrir",
    "apagr": "apagar", "deletar": "deletar", "deltar": "deletar",
    "orgainzar": "organizar", "oganizar": "organizar",
    "listarr": "listar", "listasr": "listar",
    "renomearr": "renomear",
    "buscarr": "buscar", "procuraar": "procurar",
    "copiarr": "copiar",
    "lembar": "lembrar",
    "yotube": "youtube", "yutube": "youtube", "youtbe": "youtube",
    "googel": "google", "gogle": "google",
    "instagran": "instagram", "insta": "instagram",
    "netflixx": "netflix", "netlix": "netflix",
    "discrod": "discord", "discor": "discord",
    "twittter": "twitter", "twiter": "twitter",
    "spotfy": "spotify", "spotifiy": "spotify",
    "githb": "github", "gihub": "github",
    "donwloads": "downloads", "downlods": "downloads",
    "documetos": "documentos", "docuemntos": "documentos",
    "desktoop": "desktop", "deskop": "desktop",
    "chorme": "chrome", "chome": "chrome",
    "noteapd": "notepad", "notpad": "notepad",
    "temporaios": "temporarios", "temp": "temporarios",
    "duplicaods": "duplicados",
}


def corrigir_texto(texto):
    """Corrige erros de digitação usando dicionário e fuzzy matching."""
    palavras = texto.lower().split()
    corrigidas = []
    for palavra in palavras:
        if palavra in CORRECOES:
            corrigidas.append(CORRECOES[palavra])
        else:
            melhor = palavra
            melhor_score = 0
            for errado, certo in CORRECOES.items():
                score = SequenceMatcher(None, palavra, errado).ratio()
                if score > 0.80 and score > melhor_score:
                    melhor_score = score
                    melhor = certo
            corrigidas.append(melhor)
    return " ".join(corrigidas)
