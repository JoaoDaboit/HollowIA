#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HollowIA - Chatbot Avançado com Aprendizado, Histórico e Busca Web Aprimorada! 🚀
"""

import json
import os
import random
import re
import socket
from datetime import datetime
from typing import Any, Dict, List, Optional
import urllib.request
import urllib.parse

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

MEMORIA_FILE = "memoria.json"
HISTORICO_FILE = "historico.json"
CHANCE_REFLEXAO_INEDITA = 0.30
CHANCE_PESQUISA_AUTOMATICA = 0.65

RESPOSTAS_EMOCIONAIS = {
    # --- Sentimentos Negativos / Tristeza / Desânimo ---
    "triste": "Sinto muito que esteja se sentindo assim. Quer conversar sobre o que aconteceu?",
    "tristeza": "A tristeza pode ser pesada. Estou aqui se quiser desabafar.",
    "chateado": "Poxa, o que aconteceu para te deixar chateado?",
    "chateada": "Poxa, o que aconteceu para te deixar chateada?",
    "deprimido": "Sinto muito. Estou aqui se quiser desabafar ou apenas conversar um pouco.",
    "deprimida": "Sinto muito. Estou aqui se quiser desabafar ou apenas conversar um pouco.",
    "depressao": "Sinto muito que esteja passando por isso. Quer me contar como tem se sentido?",
    "mal": "Espero que as coisas melhorem logo. Quer me contar o motivo?",
    "desanimado": "Dias assim são difíceis... Quer conversar sobre o que te tirou o ânimo?",
    "desanimada": "Dias assim são difíceis... Quer conversar sobre o que te tirou o ânimo?",
    "sozinho": "Você não está só, estou aqui conversando com você. O que está pegando?",
    "sozinha": "Você não está só, estou aqui conversando com você. O que está pegando?",

    # --- Raiva / Irritação / Frustração ---
    "bravo": "Eita, o que te deixou bravo assim? Quer desabafar?",
    "brava": "Eita, o que te deixou brava assim? Quer desabafar?",
    "irritado": "Sei como é horrível ficar irritado. Quer me contar o que aconteceu?",
    "irritada": "Sei como é horrível ficar irritada. Quer me contar o que aconteceu?",
    "com raiva": "Respire fundo! O que aconteceu para te deixar com tanta raiva?",
    "frustrado": "A frustração é péssima. Quer me explicar o que deu errado?",
    "frustrada": "A frustração é péssima. Quer me explicar o que deu errado?",
    "puto": "Nossa, parece que a situação foi feia. O que rolou?",
    "puta": "Nossa, parece que a situação foi feia. O que rolou?",

    # --- Ansiedade / Estresse / Medo ---
    "ansioso": "Tente respirar fundo com calma. Quer conversar sobre o que está te deixando assim?",
    "ansiosa": "Tente respirar fundo com calma. Quer conversar sobre o que está te deixando assim?",
    "ansiedade": "Ansiedade é bem desconfortável... Vamos focar no momento presente. Quer conversar?",
    "estresse": "Poxa, dias estressantes são bem cansativos. O que te sobrecarregou hoje?",
    "estressado": "Dá uma pausinha se puder. Quer desabafar sobre o motivo do estresse?",
    "estressada": "Dá uma pausinha se puder. Quer desabafar sobre o motivo do estresse?",
    "preocupado": "O que está deixando sua cabeça cheia de preocupações?",
    "preocupada": "O que está deixando sua cabeça cheia de preocupações?",
    "com medo": "É normal sentir medo às vezes. Quer me contar o que está te assustando?",
    "nervoso": "Tenta dar uma pausa e relaxar os ombros. Quer me contar o que te deixou assim?",
    "nervosa": "Tenta dar uma pausa e relaxar os ombros. Quer me contar o que te deixou assim?",

    # --- Sentimentos Estranhos / Confusão / Neutros ---
    "estranho": "Sentir-se estranho às vezes é difícil de explicar, né? Quer tentar me dizer como é essa sensação?",
    "estranha": "Sentir-se estranha às vezes é difícil de explicar, né? Quer tentar me dizer como é essa sensação?",
    "confuso": "Às vezes a nossa cabeça dá um nó mesmo. Quer organizar os pensamentos conversando comigo?",
    "confusa": "Às vezes a nossa cabeça dá um nó mesmo. Quer organizar os pensamentos conversando comigo?",
    "perdido": "Está tudo bem não ter todas as respostas agora. Quer trocar uma ideia sobre o que está sentindo?",
    "perdida": "Está tudo bem não ter todas as respostas agora. Quer trocar uma ideia sobre o que está sentindo?",
    "cansado": "Poxa, você precisa descansar um pouco. Foi um dia muito puxado?",
    "cansada": "Poxa, você precisa descansar um pouco. Foi um dia muito puxado?",
    "tedio": "Tédio é chato mesmo! Quer conversar sobre algum assunto legal para passar o tempo?",
    "entediado": "Vamos espantar esse tédio! Quer falar sobre jogos, tecnologia ou algum tema bacana?",
    "entediada": "Vamos espantar esse tédio! Quer falar sobre jogos, tecnologia ou algum tema bacana?",

    # --- Sentimentos Positivos / Felicidade / Animação ---
    "feliz": "Que notícia maravilhosa! Fico muito feliz por você! O que aconteceu de bom?",
    "alegre": "Que ótimo! É muito bom te ver com essa energia positiva!",
    "alegria": "Que incrível! A alegria contagia! Qual é o motivo dessa felicidade toda?",
    "animado": "Que show! Qual é a boa nova de hoje?",
    "animada": "Que show! Qual é a boa nova de hoje?",
    "bem": "Que excelente que você está bem! Como posso deixar seu dia ainda melhor?",
    "otimo": "Que maravilha! Adoro ver você animado assim!",
    "otima": "Que maravilha! Adoro ver você animada assim!",
    "empolgado": "Massa demais! Me conta o que te deixou tão empolgado!",
    "empolgada": "Massa demais! Me conta o que te deixou tão empolgada!",
    "orgulhoso": "Parabéns! É incrível sentir orgulho das próprias conquistas. Me conta o que você fez!",
    "orgulhosa": "Parabéns! É incrível sentir orgulho das próprias conquistas. Me conta o que você fez!",
    "em paz": "Que sensação boa! Nada como um dia tranquilo e em paz."
}

SINONIMOS = {
    "gpu": ["placa de vídeo", "placa de video", "gpu", "placa gráfica", "placas de vídeo", "placas de video"],
    "placa de vídeo": ["gpu", "placa de vídeo", "placa de video", "placa gráfica"],
    "placa de video": ["gpu", "placa de vídeo", "placa de video", "placa gráfica"],
    "rtx 4090": ["rtx 4090", "geforce rtx 4090", "placa de video rtx 4090"],
    "ets2": ["euro truck simulator 2", "ets2", "euro truck"],
    "euro truck simulator 2": ["ets2", "euro truck simulator 2", "euro truck"],
    "euro truck": ["ets2", "euro truck simulator 2", "euro truck"]
}

engine = None
if pyttsx3:
    try:
        engine = pyttsx3.init()
    except Exception:
        engine = None

def falar(texto: str) -> None:
    if engine:
        try:
            engine.say(texto)
            engine.runAndWait()
        except Exception:
            pass

def tem_conexao_internet() -> bool:
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

def formatar_em_paragrafos(texto: str, frases_por_paragrafo: int = 2) -> str:
    if not texto:
        return ""
    frases = re.split(r'(?<=[.!?])\s+', texto.strip())
    paragrafos = []
    for i in range(0, len(frases), frases_por_paragrafo):
        paragrafo = " ".join(frases[i:i + frases_por_paragrafo])
        paragrafos.append(paragrafo)
    return "\n\n".join(paragrafos)

def resumir_texto(texto: str, max_frases: int = 4) -> str:
    if not texto:
        return ""
    frases = [f.strip() for f in re.split(r'(?<=[.!?])\s+', texto.strip()) if len(f.strip()) > 5]
    return " ".join(frases[:max_frases])

def extrair_palavra_chave(texto: str) -> str:
    stop_words = {"eu", "estou", "me", "sinto", "muito", "o", "a", "os", "as", "de", "do", "da", "em", "um", "uma", "para", "com", "que", "qual", "quais"}
    palavras = re.findall(r'\b\w+\b', texto.lower())
    filtradas = [p for p in palavras if p not in stop_words]
    return filtradas[0] if filtradas else texto.lower().strip()

def gerar_sintese_coerente(assunto: str, texto_memoria: str) -> str:
    frases = [f.strip() for f in re.split(r'(?<=[.!?])\s+', texto_memoria.strip()) if len(f.strip()) > 15]
    termos_irrelevantes = ["vocabulário", "extenso", "especializado", "termo", "etimologia", "palavra", "refere-se a"]
    
    frases_uteis = [
        f for f in frases 
        if not any(t in f.lower() for t in termos_irrelevantes) and not f.endswith('?')
    ]
    
    frase_escolhida = frases_uteis[0] if frases_uteis else (frases[0] if frases and not frases[0].endswith('?') else f"{assunto} é um tema interessante.")
    
    introducoes = [
        f"Sobre {assunto}: {frase_escolhida}",
        f"Lembro que {frase_escolhida.lower() if frase_escolhida[0].isupper() else frase_escolhida}",
        f"Em resumo: {frase_escolhida}"
    ]
    return random.choice(introducoes)

def salvar_historico(usuario: str, ia: str, assunto: Optional[str] = None) -> None:
    agora = datetime.now()
    dias_semana = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
    
    registro = {
        "data": agora.strftime("%Y-%m-%d"),
        "ano": agora.year,
        "dia_semana": dias_semana[agora.weekday()],
        "horario": agora.strftime("%H:%M:%S"),
        "usuario": usuario,
        "ia": ia,
        "assunto": assunto
    }
    
    historico = []
    if os.path.exists(HISTORICO_FILE):
        try:
            with open(HISTORICO_FILE, "r", encoding="utf-8") as f:
                historico = json.load(f)
                if not isinstance(historico, list):
                    historico = []
        except (json.JSONDecodeError, IOError):
            historico = []
            
    historico.append(registro)
    try:
        with open(HISTORICO_FILE, "w", encoding="utf-8") as f:
            json.dump(historico, f, indent=4, ensure_ascii=False)
    except IOError:
        pass

def obter_ultimo_assunto_historico() -> Optional[str]:
    if os.path.exists(HISTORICO_FILE):
        try:
            with open(HISTORICO_FILE, "r", encoding="utf-8") as f:
                historico = json.load(f)
                if isinstance(historico, list) and historico:
                    for item in reversed(historico):
                        if item.get("assunto"):
                            return item["assunto"]
        except Exception:
            return None
    return None

def carregar_memoria() -> Dict[str, List[Dict[str, Any]]]:
    memoria_padrao = {"usuario": [], "web": []}
    if os.path.exists(MEMORIA_FILE):
        try:
            with open(MEMORIA_FILE, "r", encoding="utf-8") as f:
                memoria = json.load(f)
                if not isinstance(memoria, dict):
                    return memoria_padrao
                if "usuario" not in memoria:
                    memoria["usuario"] = []
                if "web" not in memoria:
                    memoria["web"] = []
                return memoria
        except (json.JSONDecodeError, IOError):
            return memoria_padrao
    return memoria_padrao

def salvar_memoria(memoria: Dict[str, List[Dict[str, Any]]]) -> None:
    try:
        with open(MEMORIA_FILE, "w", encoding="utf-8") as f:
            json.dump(memoria, f, indent=4, ensure_ascii=False)
    except IOError:
        pass

def ensinar(memoria: Dict[str, List[Dict[str, Any]]], assunto: str, resposta: str, pergunta_followup: Optional[str] = None, fonte: str = "usuario") -> None:
    assunto_limpo = extrair_palavra_chave(assunto)
    memoria[fonte] = [item for item in memoria.get(fonte, []) if item.get("assunto", "").lower().strip() != assunto_limpo]
    sinonimos_associados = SINONIMOS.get(assunto_limpo, [assunto_limpo, assunto.lower().strip()])

    novo_conhecimento = {
        "assunto": assunto_limpo,
        "frase_original": assunto,
        "resposta": resposta,
        "pergunta_followup": pergunta_followup,
        "sinonimos": sinonimos_associados
    }
    memoria[fonte].append(novo_conhecimento)
    salvar_memoria(memoria)

def combiner_resposta(memoria: Dict, entrada: str) -> Optional[Dict[str, Any]]:
    entrada_lower = entrada.lower().strip()
    for fonte in ["usuario", "web"]:
        for item in memoria.get(fonte, []):
            assunto = item.get("assunto", "").lower().strip()
            if not assunto:
                continue
            if re.search(rf"\b{re.escape(assunto)}\b", entrada_lower):
                return item
            frase_orig = item.get("frase_original", "").lower().strip()
            if frase_orig and frase_orig in entrada_lower:
                return item
            termos_equivalentes = item.get("sinonimos", SINONIMOS.get(assunto, []))
            for eq in termos_equivalentes:
                if re.search(rf"\b{re.escape(eq.lower())}\b", entrada_lower):
                    return item
    return None

def pesquisar_na_internet(termo: str, resumido: bool = False, memoria: Optional[Dict] = None) -> str:
    if not tem_conexao_internet():
        return "Você está sem internet!"

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    texto_bruto = ""

    termo_limpo = re.sub(
        r'^(o que é|o que e|quem foi|pesquisar sobre|pesquise sobre|pesquisar|pesquise|qual|quais|onde|como)\s+', 
        '', 
        termo, 
        flags=re.IGNORECASE
    ).strip()

    # 1. Wikipédia API
    url_wiki = f"https://pt.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(termo_limpo)}"
    try:
        req = urllib.request.Request(url_wiki, headers=headers)
        with urllib.request.urlopen(req, timeout=4) as response:
            dados = json.loads(response.read().decode('utf-8'))
            if "extract" in dados and dados["extract"]:
                texto_bruto = dados["extract"]
    except Exception:
        pass

    # 2. DuckDuckGo HTML
    if not texto_bruto:
        url_ddg_html = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(termo)}"
        try:
            req = urllib.request.Request(url_ddg_html, headers=headers)
            with urllib.request.urlopen(req, timeout=5) as response:
                html = response.read().decode('utf-8')
                
                raw_snippets = re.findall(r'<a class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)
                
                palavras_bloqueadas = ["frete grátis", "mercado livre", "shoppee", "oferta", "comprar", "magalu", "kabum", "encontre na", "examples and translations"]
                snippets_validos = []

                for snip in raw_snippets:
                    texto_limpo_snip = re.sub(r'<[^>]+>', '', snip).strip()
                    if not any(p in texto_limpo_snip.lower() for p in palavras_bloqueadas):
                        if texto_limpo_snip and not texto_limpo_snip.endswith(('.', '!', '?')):
                            texto_limpo_snip += '.'
                        snippets_validos.append(texto_limpo_snip)
                
                if snippets_validos:
                    texto_bruto = " ".join(snippets_validos[:4])
        except Exception:
            pass

    if texto_bruto:
        resposta_final = resumir_texto(texto_bruto, max_frases=4) if resumido else formatar_em_paragrafos(texto_bruto)
        if memoria is not None:
            ensinar(memoria, termo_limpo if termo_limpo else termo, texto_bruto, fonte="web")
        return resposta_final

    return f"Não encontrei uma explicação direta sobre '{termo}'."

# ------------------ Personalidades e Emojis Moderados ------------------
def detectar_personalidade(entrada: str) -> str:
    entrada_lower = entrada.lower()
    def contem_palavras(palavras: List[str]) -> bool:
        return any(re.search(rf"\b{re.escape(p)}\b", entrada_lower) for p in palavras)

    if contem_palavras(["triste", "chateado", "mal", "deprimido", "bravo", "ansioso"]):
        return "carinhosa"
    if contem_palavras(["piada", "haha", "kkk", "engraçado", "lol"]):
        return "engraçada"
    if contem_palavras(["uau", "incrível", "massa", "legal", "demais", "feliz", "alegre"]):
        return "empolgada"
    if contem_palavras(["por que", "porque", "como", "onde", "estranho"]):
        return "pensativa"
    if "?" in entrada:
        return "curiosa"
    return "séria"

def aplicar_personalidade(resposta: str, personality: str) -> str:
    # Apenas 1 a 2 emojis equilibrados por tom
    emojis = {
        "carinhosa": [" ✨💙", " 🌸", " 🤗", " 💖", " ✨🥰"],
        "engraçada": [" 😂", " 😜", " 🤣", " 🤪"],
        "empolgada": [" 🚀✨", " 🎉", " 🔥", " ⭐"],
        "pensativa": [" 🧐", " 💭", " 💡"],
        "curiosa": [" 🤔", " 👀", " 🔎"],
        "séria": [" 👍", " ✨", " 📌", " 😊"]
    }
    
    emoji_escolhido = random.choice(emojis.get(personality, [" ✨"]))
    return resposta + emoji_escolhido

def gerar_saudacao_com_contexto(memoria: Dict) -> str:
    ultimo_assunto = obter_ultimo_assunto_historico()
    if not ultimo_assunto and (memoria.get("usuario") or memoria.get("web")):
        todos_itens = memoria.get("usuario", []) + memoria.get("web", [])
        if todos_itens:
            ultimo_assunto = todos_itens[-1].get("assunto")
        
    if ultimo_assunto:
        variacoes = [
            f"Olá! Você ainda está pensando sobre {ultimo_assunto}?",
            f"Oi! Estava lembrando da nossa conversa sobre {ultimo_assunto}. Quer continuar?",
            f"Olá! Ficou alguma dúvida sobre {ultimo_assunto}?"
        ]
        return random.choice(variacoes)
    
    return random.choice([
        "Olá! Como posso te ajudar hoje?",
        "Oi! Que bom te ver por aqui. Sobre o que quer conversar?"
    ])

def executar_busca_web(termo: str, memoria: Dict, silenciosa: bool = False) -> Dict[str, Any]:
    resultado_web = pesquisar_na_internet(termo, resumido=silenciosa, memoria=memoria)
    if resultado_web == "Você está sem internet!":
        return {"resposta": "Você está sem internet!", "pergunta_followup": None, "assunto": termo}
    
    if silenciosa:
        return {"resposta": resultado_web, "pergunta_followup": None, "assunto": termo}

    sugestao_busca = f"Deixe-me dar uma olhada na internet sobre {termo}..."
    print(f"IA: {sugestao_busca}\n")
    falar(sugestao_busca)
    
    return {
        "resposta": f"Encontrei isso:\n\n{resultado_web}",
        "pergunta_followup": "Quer pesquisar mais sobre isso?",
        "assunto": termo,
        "tipo_followup": "pesquisa"
    }

def processar_entrada(
    memoria: Dict,
    entrada: str,
    contexto: List[Dict[str, str]],
    esperando_assunto_pesquisa: bool = False
) -> Dict[str, Any]:
    entrada_clean = entrada.lower().strip()

    cumprimentos = ["oi", "olá", "ola", "oie", "e aí", "e ai", "bom dia", "boa tarde", "boa noite"]
    if entrada_clean in cumprimentos and not esperando_assunto_pesquisa:
        fala_contextual = gerar_saudacao_com_contexto(memoria)
        return {"resposta": fala_contextual, "assunto": None}

    if esperando_assunto_pesquisa:
        res = executar_busca_web(entrada, memoria)
        res["esperando_assunto"] = False
        return res

    # 1. Trata sentimentos e emoções (ordena do maior para o menor termo)
    termos_emocionais_ordenados = sorted(RESPOSTAS_EMOCIONAIS.keys(), key=len, reverse=True)
    for emocao in termos_emocionais_ordenados:
        if re.search(rf"\b{re.escape(emocao)}\b", entrada_clean):
            return {"resposta": RESPOSTAS_EMOCIONAIS[emocao], "assunto": emocao}

    # 2. Gatilhos explícitos para buscar na web
    gatilhos_busca = ["pesquisar sobre", "pesquise sobre", "pesquisar", "pesquise", "o que é", "o que e", "quem foi", "qual", "quais"]
    if any(entrada_clean.startswith(g) for g in gatilhos_busca):
        termo_busca = re.sub(r'^(pesquisar sobre|pesquise sobre|pesquisar|pesquise|o que é|o que e|quem foi)\s+', '', entrada, flags=re.IGNORECASE).strip()
        if termo_busca:
            return executar_busca_web(termo_busca, memoria)

    # 3. Procura na memória local
    item_encontrado = combiner_resposta(memoria, entrada)
    if item_encontrado:
        assunto_atual = item_encontrado.get("assunto", entrada)
        texto_salvo = item_encontrado.get("resposta", "")

        resposta_gerada = gerar_sintese_coerente(assunto_atual, texto_salvo)
        return {
            "resposta": resposta_gerada.strip(),
            "pergunta_followup": item_encontrado.get("pergunta_followup"),
            "assunto": assunto_atual
        }

    # 4. Busca silenciosa automática
    palavras_entrada = entrada_clean.split()
    tem_internet = tem_conexao_internet()
    if tem_internet and len(palavras_entrada) > 3 and (random.random() < CHANCE_PESQUISA_AUTOMATICA):
        res_silenciosa = executar_busca_web(entrada, memoria, silenciosa=True)
        if res_silenciosa["resposta"] and not res_silenciosa["resposta"].startswith("Não encontrei"):
            return res_silenciosa

    # 5. Aprendizado interativo
    mensagem_aprendizado = random.choice([
        f"Ainda não sei sobre '{entrada}'. Me ensina ou quer que eu pesquise? (Digite o que dizer ou 'pesquisa')",
        f"Eu não tenho isso na minha memória. Como você me ensinaria sobre '{entrada}'? (Ou digite 'pesquisa' para eu procurar)"
    ])
    print(f"IA: {mensagem_aprendizado}")
    falar(mensagem_aprendizado)

    nova_resposta = input("Você (ensina a IA ou digite 'pesquisa'): ").strip()
    gatilhos_pedir_pesquisa = ["pesquisa", "pesquise", "não sei", "nao sei", "pesquisa você", "pesquisa voce", "procura"]
    
    if nova_resposta.lower() in gatilhos_pedir_pesquisa:
        if tem_internet:
            return executar_busca_web(entrada, memoria, silenciosa=False)
        else:
            return {"resposta": "Tentei pesquisar, mas estamos sem conexão no momento!", "assunto": None}

    if nova_resposta:
        ensinar(memoria, entrada, nova_resposta, fonte="usuario")
        fala_aprendizado = f"Entendi! Aprendi sobre '{entrada}'."
        return {"resposta": fala_aprendizado, "assunto": entrada}
    else:
        return {"resposta": "Sem problemas! Vamos conversar sobre outra coisa.", "assunto": None}

def main() -> None:
    memoria = carregar_memoria()
    contexto: List[Dict[str, str]] = []
    pos_pesquisa = False
    esperando_assunto = False

    print("HollowIA iniciada! Digite 'sair' para terminar.\n")
    falar("Olá! Eu sou a HollowIA! Vamos conversar.")
    
    while True:
        try:
            entrada = input("Você: ").strip()
        except (KeyboardInterrupt, EOFError):
            break
            
        if not entrada:
            continue
            
        if entrada.lower() in ["sair", "exit", "tchau", "adeus"]:
            resposta_final = "Até logo! Foi bom conversar com você."
            print("IA:", resposta_final)
            falar(resposta_final)
            salvar_historico(entrada, resposta_final)
            break
            
        personalidade = detectar_personalidade(entrada)

        if pos_pesquisa and not esperando_assunto:
            pos_pesquisa = False
            padrao_nao = r'\b(n[ãa]o|nop|jamais|prefiro n[ãa]o)\b'
            padrao_sim = r'\b(sim|quero|pode|bora|com certeza|s|yes)\b'

            if re.search(padrao_nao, entrada, re.IGNORECASE):
                resposta_ok = aplicar_personalidade("Tudo bem! Sobre o que mais quer conversar?", personalidade)
                print("IA:", resposta_ok)
                falar("Tudo bem! Sobre o que mais quer conversar?")
                salvar_historico(entrada, resposta_ok)
                continue
            elif re.search(padrao_sim, entrada, re.IGNORECASE):
                esperando_assunto = True
                resposta_oq = aplicar_personalidade("O que você gostaria de pesquisar?", personalidade)
                print("IA:", resposta_oq)
                falar("O que você gostaria de pesquisar?")
                salvar_historico(entrada, resposta_oq)
                continue
            
            resultado = executar_busca_web(entrada, memoria)
        else:
            resultado = processar_entrada(memoria, entrada, contexto, esperando_assunto)
            if esperando_assunto:
                esperando_assunto = False

        if isinstance(resultado, dict):
            texto_puro = resultado["resposta"]
            resposta_com_emoji = aplicar_personalidade(texto_puro, personalidade)
            assunto_atual = resultado.get("assunto")
            
            print("IA:", resposta_com_emoji)
            falar(texto_puro)
            contexto.append({"Você": entrada, "IA": resposta_com_emoji})
            salvar_historico(entrada, resposta_com_emoji, assunto_atual)
            
            if resultado.get("pergunta_followup"):
                pergunta = resultado["pergunta_followup"]
                print("\nIA (pergunta):", pergunta)
                falar(pergunta)
                contexto.append({"IA": pergunta})
                salvar_historico("(IA Follow-up)", pergunta, assunto_atual)
                if resultado.get("tipo_followup") == "pesquisa":
                    pos_pesquisa = True

if __name__ == "__main__":
    main()
