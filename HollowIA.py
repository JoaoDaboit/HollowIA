#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HollowIA - Chatbot Conversacional com Arquitetura de Fatos 🚀🧠
"""

import json
import random
import re
import socket
import ssl
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import urllib.parse
import urllib.request

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

MEMORIA_FILE = Path("memoria.json")
HISTORICO_FILE = Path("historico.json")

RESPOSTAS_EMOCIONAIS = {
    "triste": "Sinto muito que esteja se sentindo assim. Quer conversar sobre o que aconteceu?",
    "tristeza": "A tristeza pode ser pesada. Estou aqui se quiser desabafar.",
    "chateado": "Poxa, o que aconteceu para te deixar chateado?",
    "chateada": "Poxa, o que aconteceu para te deixar chateada?",
    "deprimido": "Sinto muito. Estou aqui se quiser desabafar ou apenas conversar um pouco.",
    "deprimida": "Sinto muito. Estou aqui se quiser desabafar ou apenas conversar um pouco.",
    "mal": "Espero que as coisas melhorem logo. Quer me contar o motivo?",
    "desanimado": "Dias assim são difíceis... Quer conversar sobre o que te tirou o ânimo?",
    "desanimada": "Dias assim são difíceis... Quer conversar sobre o que te tirou o ânimo?",
    "sozinho": "Você não está só, estou aqui conversando com você. O que está pegando?",
    "sozinha": "Você não está só, estou aqui conversando com você. O que está pegando?",
    "bravo": "Eita, o que te deixou bravo assim? Quer desabafar?",  
    "brava": "Eita, o que te deixou brava assim? Quer desabafar?",  
    "irritado": "Sei como é horrível ficar irritado. Quer me contar o que aconteceu?",  
    "irritada": "Sei como é horrível ficar irritada. Quer me contar o que aconteceu?",  
    "frustrado": "A frustração é péssima. Quer me explicar o que deu errado?",  
    "frustrada": "A frustração é péssima. Quer me explicar o que deu errado?",  
    "ansioso": "Tente respirar fundo com calma. Quer conversar sobre o que está te deixando assim?",  
    "ansiosa": "Tente respirar fundo com calma. Quer conversar sobre o que está te deixando assim?",  
    "estressado": "Dá uma pausinha se puder. Quer desabafar sobre o motivo do estresse?",  
    "estressada": "Dá uma pausinha se puder. Quer desabafar sobre o motivo do estresse?",  
    "cansado": "Poxa, você precisa descansar um pouco. Foi um dia muito puxado?",  
    "cansada": "Poxa, você precisa descansar um pouco. Foi um dia muito puxado?",  
    "feliz": "Que notícia maravilhosa! Fico muito feliz por você! O que aconteceu de bom?",  
    "alegre": "Que ótimo! É muito bom te ver com essa energia positiva!",  
    "animado": "Que show! Qual é a boa nova de hoje?",  
    "animada": "Que show! Qual é a boa nova de hoje?",  
    "bem": "Que excelente que você está bem! Como posso deixar seu dia ainda melhor?"
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

def limpar_texto(texto: str) -> str:
    if not texto:
        return ""
    texto = texto.lower().strip()
    nfkd = unicodedata.normalize('NFKD', texto)
    texto_sem_acento = "".join([c for c in nfkd if not unicodedata.combining(c)])
    texto_limpo = re.sub(r'[^a-z0-9\s]', '', texto_sem_acento)
    return re.sub(r'\s+', ' ', texto_limpo).strip()

def extrair_palavras_chave(texto: str) -> List[str]:
    stopwords = {"o", "a", "os", "as", "um", "uma", "uns", "umas", "de", "do", "da", "dos", "das", "em", "no", "na", "nos", "nas", "por", "para", "com", "que", "e", "ou", "se", "como", "foi", "ser", "ter", "sao", "era"}
    texto_limpo = limpar_texto(texto)
    palavras = texto_limpo.split()
    return [p for p in palavras if len(p) > 2 and p not in stopwords]

def quebrar_em_fatos(texto: str) -> List[str]:
    """Divide um texto corrido em frases individuais."""
    if not texto:
        return []
    frases = [f.strip() for f in re.split(r'(?<=[.!?])\s+', texto.strip()) if len(f.strip()) > 5]
    return frases if frases else [texto.strip()]

def salvar_historico(usuario: str, ia: str, assunto: Optional[str] = None) -> None:
    agora = datetime.now()
    dias_semana = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
    registro = {  
        "data": agora.strftime("%Y-%m-%d"),  
        "dia_semana": dias_semana[agora.weekday()],  
        "horario": agora.strftime("%H:%M:%S"),  
        "usuario": usuario,  
        "ia": ia,  
        "assunto": assunto  
    }  
    historico = []  
    if HISTORICO_FILE.exists():  
        try:  
            with open(HISTORICO_FILE, "r", encoding="utf-8") as f:  
                dados = json.load(f)  
                if isinstance(dados, list):  
                    historico = dados  
        except (json.JSONDecodeError, OSError):  
            historico = []  
            
    historico.append(registro)  
    try:  
        with open(HISTORICO_FILE, "w", encoding="utf-8") as f:  
            json.dump(historico, f, indent=4, ensure_ascii=False)  
    except OSError:  
        pass

def obter_ultimo_assunto_historico() -> Optional[str]:
    if HISTORICO_FILE.exists():
        try:
            with open(HISTORICO_FILE, "r", encoding="utf-8") as f:
                historico = json.load(f)
                if isinstance(historico, list) and historico:
                    for item in reversed(historico):
                        if item.get("assunto"):
                            return item["assunto"]
        except (json.JSONDecodeError, OSError):
            return None
    return None

def carregar_memoria() -> Dict[str, List[Dict[str, Any]]]:
    memoria_padrao = {"usuario": [], "web": []}
    if MEMORIA_FILE.exists():
        try:
            with open(MEMORIA_FILE, "r", encoding="utf-8") as f:
                memoria = json.load(f)
                if not isinstance(memoria, dict):
                    return memoria_padrao
                memoria.setdefault("usuario", [])
                memoria.setdefault("web", [])
                return memoria
        except (json.JSONDecodeError, OSError):
            return memoria_padrao
    return memoria_padrao

def salvar_memoria(memoria: Dict[str, List[Dict[str, Any]]]) -> None:
    try:
        with open(MEMORIA_FILE, "w", encoding="utf-8") as f:
            json.dump(memoria, f, indent=4, ensure_ascii=False)
    except OSError:
        pass

def ensinar(memoria: Dict[str, List[Dict[str, Any]]], assunto: str, conteudo: str, fonte: str = "usuario") -> None:
    assunto_limpo = limpar_texto(assunto)
    memoria[fonte] = [item for item in memoria.get(fonte, []) if limpar_texto(item.get("assunto", "")) != assunto_limpo]

    fatos = quebrar_em_fatos(conteudo)
    palavras_chave = extrair_palavras_chave(assunto + " " + conteudo)

    novo_conhecimento = {  
        "assunto": assunto_limpo,  
        "assunto_original": assunto,
        "fatos": fatos,
        "palavras": palavras_chave
    }  
    memoria[fonte].append(novo_conhecimento)  
    salvar_memoria(memoria)

def compor_resposta_conversacional(fatos: List[str], assunto_original: str) -> str:
    """Transforma os fatos salvos em uma conversa natural e amigável."""
    fatos_validos = [f for f in fatos if f and len(f.strip()) > 3]
    
    if not fatos_validos:
        return ""
    
    fatos_selecionados = random.sample(fatos_validos, min(len(fatos_validos), 2))
    
    inicios_conversacionais = [
        f"Ah, falando sobre {assunto_original}, olha só: ",
        f"Sim! Sobre {assunto_original}, o que eu sei é que ",
        f"Pelo que lembro de {assunto_original}, ",
        f"Legal você mencionar {assunto_original}! Sabe o que é interessante? "
    ]
    
    intro = random.choice(inicios_conversacionais)
    corpo = " ".join(fatos_selecionados)
    
    return f"{intro}{corpo}"

def interpretar_e_buscar(memoria: Dict, entrada: str) -> Optional[Dict[str, Any]]:
    entrada_limpa = limpar_texto(entrada)
    palavras_entrada = set(extrair_palavras_chave(entrada))
    
    variacoes_entrada = {entrada_limpa}
    if entrada_limpa.endswith('s'):
        variacoes_entrada.add(entrada_limpa[:-1])
    else:
        variacoes_entrada.add(entrada_limpa + 's')

    melhor_item = None
    maior_pontuacao = 0

    for fonte in ["usuario", "web"]:
        for item in memoria.get(fonte, []):
            assunto_item = limpar_texto(item.get("assunto", ""))
            palavras_item = set(item.get("palavras", []))
            
            if any(v == assunto_item or v in assunto_item or assunto_item in v for v in variacoes_entrada):
                fatos = item.get("fatos", [])
                assunto_orig = item.get("assunto_original", entrada)
                resposta = compor_resposta_conversacional(fatos, assunto_orig)
                if resposta:
                    return {
                        "resposta": resposta,
                        "assunto": assunto_orig
                    }
            
            if palavras_entrada and palavras_item:
                intersecao = palavras_entrada.intersection(palavras_item)
                pontuacao = len(intersecao)
                
                if pontuacao > maior_pontuacao:
                    maior_pontuacao = pontuacao
                    melhor_item = item

    if melhor_item and maior_pontuacao > 0:
        fatos_disponiveis = melhor_item.get("fatos", [])
        assunto_orig = melhor_item.get("assunto_original", entrada)
        resposta = compor_resposta_conversacional(fatos_disponiveis, assunto_orig)
        if resposta:
            return {
                "resposta": resposta,
                "assunto": assunto_orig
            }

    return None

def diferenciar_intencao(entrada: str) -> str:
    entrada_lower = entrada.lower()
    termos_opiniao = ["acho", "penso", "odeio", "gosto", "amo", "detesto", "legal", "chato", "ruim", "bom", "incrivel", "horrivel", "parece"]
    if any(palavra in entrada_lower for palavra in termos_opiniao):
        return "expressando_opiniao"
    return "falando_sobre"

def extrair_termo_pesquisa(texto: str) -> str:
    texto_limpo = texto.strip()
    nfkd = unicodedata.normalize('NFKD', texto_limpo)
    texto_sem_acento = "".join([c for c in nfkd if not unicodedata.combining(c)]).lower()
    
    padroes = [
        r"^o que (e|sao|foi|sao os|sao as|e o|e a)\s+",
        r"^oque (e|sao|foi)\s+",
        r"^quem (foi|sao|e)\s+",
        r"^qual (e|foi|a origem do nome)\s+",
        r"^como (e|funciona|sao)\s+",
        r"^pesquise sobre\s+",
        r"^pesquisa sobre\s+",
        r"^pesquise\s+",
        r"^pesquisa\s+",
        r"^procura sobre\s+",
        r"^procure sobre\s+",
        r"^procura\s+",
        r"^procure\s+"
    ]
    
    for p in padroes:
        match = re.match(p, texto_sem_acento)
        if match:
            texto_limpo = texto_limpo[match.end():]
            break
            
    return texto_limpo.strip()

def pesquisar_na_internet(termo: str, memoria: Optional[Dict] = None) -> str:
    if not tem_conexao_internet():
        return "Poxa, parece que estamos sem internet agora!"

    headers = {'User-Agent': 'Mozilla/5.0'}  
    termo_limpo = extrair_termo_pesquisa(termo)
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    url_busca = f"https://pt.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(termo_limpo)}&format=json&utf8=1"
    
    titulo_artigo = None
    try:
        req_busca = urllib.request.Request(url_busca, headers=headers)
        with urllib.request.urlopen(req_busca, timeout=4, context=ctx) as resp_busca:
            dados = json.loads(resp_busca.read().decode('utf-8'))
            search_results = dados.get("query", {}).get("search", [])
            if search_results:
                titulo_artigo = search_results[0]["title"]
    except Exception:
        pass

    texto_bruto = ""
    if titulo_artigo:
        try:  
            url_wiki = f"https://pt.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(titulo_artigo)}"
            req = urllib.request.Request(url_wiki, headers=headers)  
            with urllib.request.urlopen(req, timeout=4, context=ctx) as response:  
                dados = json.loads(response.read().decode('utf-8'))  
                if "extract" in dados and dados["extract"]:  
                    ext = dados["extract"]
                    if "desambiguação" not in ext.lower() and len(ext) > 30:
                        texto_bruto = ext
        except Exception:  
            pass  

    if texto_bruto:  
        if memoria is not None:  
            ensinar(memoria, termo, texto_bruto, fonte="web")
            ensinar(memoria, termo_limpo, texto_bruto, fonte="web")
        return compor_resposta_conversacional(quebrar_em_fatos(texto_bruto), termo)

    return ""

def aprender_em_lote(termo_base: str, quantidade: int, memoria: Dict) -> str:
    if not tem_conexao_internet():
        return "Você está sem internet para aprender em lote!"

    headers = {'User-Agent': 'Mozilla/5.0'}
    termo_limpo = extrair_termo_pesquisa(termo_base)
    aprendidos = 0

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    titulos = []
    url_busca = f"https://pt.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(termo_limpo)}&srlimit={quantidade}&format=json&utf8=1"
    try:
        req = urllib.request.Request(url_busca, headers=headers)
        with urllib.request.urlopen(req, timeout=6, context=ctx) as resp:
            dados = json.loads(resp.read().decode('utf-8'))
            search_results = dados.get("query", {}).get("search", [])
            titulos = [item["title"] for item in search_results]
    except Exception:
        pass

    for titulo in titulos:
        try:
            url_wiki = f"https://pt.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(titulo)}"
            req_wiki = urllib.request.Request(url_wiki, headers=headers)
            with urllib.request.urlopen(req_wiki, timeout=4, context=ctx) as resp_wiki:
                dados_wiki = json.loads(resp_wiki.read().decode('utf-8'))
                if "extract" in dados_wiki and dados_wiki["extract"]:
                    texto = dados_wiki["extract"]
                    if "desambiguação" not in texto.lower() and len(texto) > 30:
                        ensinar(memoria, titulo, texto, fonte="web")
                        aprendidos += 1
                        if aprendidos >= quantidade:
                            break
        except Exception:
            continue

    if aprendidos > 0:
        return f"Pronto! Absorvi {aprendidos} fatos sobre '{termo_base}'. Pode me perguntar sobre eles! 🚀"
    else:
        return f"Não consegui achar conteúdos suficientes sobre '{termo_base}'."

def detectar_personalidade(entrada: str) -> str:
    entrada_lower = entrada.lower()
    if any(p in entrada_lower for p in ["triste", "chateado", "mal", "bravo", "ansioso"]):  
        return "carinhosa"  
    if any(p in entrada_lower for p in ["piada", "haha", "kkk", "engraçado"]):  
        return "engraçada"  
    if any(p in entrada_lower for p in ["uau", "incrível", "massa", "legal", "feliz"]):  
        return "empolgada"  
    return "curiosa"

def aplicar_personalidade(resposta: str, personality: str) -> str:
    emojis = {
        "carinhosa": [" ✨💙", " 🌸", " 🤗"],
        "engraçada": [" 😂", " 😜", " 🤣"],
        "empolgada": [" 🚀✨", " 🎉", " 🔥"],
        "curiosa": [" 🤔", " 👀", " 💡"]
    }
    emoji_escolhido = random.choice(emojis.get(personality, [" ✨"]))  
    return resposta + emoji_escolhido

def gerar_saudacao_com_contexto() -> str:
    ultimo_assunto = obter_ultimo_assunto_historico()
    if ultimo_assunto:  
        return f"Oie! Estava pensando... você ainda lembra daquele papo sobre '{ultimo_assunto}'?"  
    return "Oie! Tudo bem? Sobre o que você quer conversar hoje?"

def processar_entrada(
    memoria: Dict,
    entrada: str,
    ultima_pergunta_usuario: str = "",
    esperando_assunto_pesquisa: bool = False,
    em_conversa_emocional: bool = False
) -> Dict[str, Any]:
    entrada_clean = entrada.lower().strip()

    cumprimentos = ["oi", "olá", "ola", "oie", "e aí", "e ai", "bom dia", "boa tarde", "boa noite"]  
    if entrada_clean in cumprimentos and not esperando_assunto_pesquisa:  
        return {"resposta": gerar_saudacao_com_contexto(), "assunto": None, "emocional": False}  

    if esperando_assunto_pesquisa:  
        resultado_web = pesquisar_na_internet(entrada, memoria=memoria)
        return {"resposta": resultado_web, "assunto": entrada, "emocional": False}

    emocoes_exatas = ["triste", "tristeza", "chateado", "chateada", "deprimido", "deprimida", "mal", "desanimado", "desanimada", "sozinho", "sozinha", "bravo", "brava", "irritado", "irritada", "frustrado", "frustrada", "ansioso", "ansiosa", "estressado", "estressada", "cansado", "cansada", "feliz", "alegre", "animado", "animada", "bem"]
    for emocao in emocoes_exatas:
        if entrada_clean == emocao or f"estou {emocao}" in entrada_clean or f"me sinto {emocao}" in entrada_clean:
            return {"resposta": RESPOSTAS_EMOCIONAIS[emocao], "assunto": emocao, "emocional": True}

    if em_conversa_emocional:  
        if any(w in entrada_clean for w in ["como", "o que", "qual", "quem", "onde", "quando", "por que", "porque"]):
            em_conversa_emocional = False  
        else:
            return {"resposta": "Sinto muito que você esteja passando por isso. Quer desabafar mais sobre o que aconteceu?", "assunto": "desabafo", "emocional": True}  

    if entrada_clean.startswith("lote "):
        termo_lote = entrada[5:].strip()
        if tem_conexao_internet():
            resultado_lote = aprender_em_lote(termo_lote, 10, memoria=memoria)
            return {"resposta": resultado_lote, "assunto": termo_lote, "emocional": False}
        else:
            return {"resposta": "Sem internet para aprender em lote!", "assunto": None, "emocional": False}

    if entrada_clean.startswith(("pesquisa", "pesquise", "procura")):
        if tem_conexao_internet():
            resultado_web = pesquisar_na_internet(entrada, memoria=memoria)
            if resultado_web:
                return {"resposta": resultado_web, "assunto": entrada, "emocional": False}
        else:
            return {"resposta": "Você pediu para pesquisar, mas estamos sem internet agora!", "assunto": None, "emocional": False}

    # 1. Tenta buscar na memória local/web salva
    item_encontrado = interpretar_e_buscar(memoria, entrada)  
    if item_encontrado:  
        return {  
            "resposta": item_encontrado.get("resposta", ""),  
            "assunto": item_encontrado.get("assunto"),  
            "emocional": False  
        }  

    tipo_intencao = diferenciar_intencao(entrada)
    if tipo_intencao == "expressando_opiniao":
        return {
            "resposta": "Entendi seu ponto! É bem por aí mesmo.",
            "assunto": entrada,
            "emocional": False
        }

    # 2. Se não encontrou na memória, tenta pesquisar na internet automaticamente
    if tem_conexao_internet():
        resultado_auto_web = pesquisar_na_internet(entrada, memoria=memoria)
        if resultado_auto_web:
            return {"resposta": resultado_auto_web, "assunto": entrada, "emocional": False}

    # 3. Se nem na memória e nem na internet encontrou, aí sim pergunta o que é
    print(f"IA: Poxa, ainda não conheço '{entrada}'. Quer me explicar o que é?")
    falar("Não conheço isso ainda. Me ensina.")
    
    nova_resposta = input("Você (ensine): ").strip()  
    
    if nova_resposta:  
        ensinar(memoria, entrada, nova_resposta, fonte="usuario")  
        fatos_criados = quebrar_em_fatos(nova_resposta)
        resposta_gerada = compor_resposta_conversacional(fatos_criados, entrada)
        return {"resposta": f"Opa, anotado! {resposta_gerada}", "assunto": entrada, "emocional": False}  
    else:  
        return {"resposta": "Beleza! Mudando de assunto, o que mais você quer ver?", "assunto": None, "emocional": False}

def main() -> None:
    memoria = carregar_memoria()
    em_conversa_emocional = False
    ultima_pergunta_usuario = ""

    print("HollowIA Conversacional iniciada! Digite 'sair' para terminar.\n")  
    print("Dica: Use 'lote [termo]' para absorver vários fatos de uma vez!\n")
    falar("Oie! Eu sou a HollowIA!")  
      
    while True:  
        try:  
            entrada = input("Você: ").strip()  
        except (KeyboardInterrupt, EOFError):  
            break  
              
        if not entrada:  
            continue  
              
        if entrada.lower() in ["sair", "exit", "tchau"]:  
            print("IA: Até logo! Foi bom conversar com você!")  
            falar("Até logo!")  
            break  
              
        if not entrada.lower().startswith(("pesquisa", "pesquise", "procura", "lote", "sair")) and len(entrada) > 0:
            ultima_pergunta_usuario = entrada

        personalidade = detectar_personalidade(entrada)  
        resultado = processar_entrada(
            memoria, 
            entrada, 
            ultima_pergunta_usuario=ultima_pergunta_usuario,
            em_conversa_emocional=em_conversa_emocional
        )  

        if isinstance(resultado, dict):  
            em_conversa_emocional = resultado.get("emocional", False)  
            texto_puro = resultado["resposta"]  
            resposta_com_emoji = aplicar_personalidade(texto_puro, personalidade)  
            
            print("IA:", resposta_com_emoji)  
            falar(texto_puro)  
            salvar_historico(entrada, resposta_com_emoji, resultado.get("assunto"))

if __name__ == "__main__":
    main()
