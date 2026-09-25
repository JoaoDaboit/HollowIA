#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HollowIA - Um Chatbot Simples com Aprendizado Contínuo, Geração de Perguntas e Pesquisa Web.

Este script implementa um chatbot de linha de comando chamado HollowIA.
Ele é capaz de:
- Conversar com o usuário usando texto e voz.
- Pesquisar na internet buscando explicações conceituais (sem ofertas ou anúncios).
- Detectar se o dispositivo está sem internet e avisar o usuário.
- Aprender novas respostas quando não sabe algo.
- Analisar a conversa para extrair tópicos.
- Gerar suas próprias perguntas de continuação com base nos tópicos.
- Salvar seu conhecimento em um arquivo JSON para persistência.
"""

import json
import os
import random
import re
import socket
from typing import Any, Dict, List, Optional, Union
import urllib.request
import urllib.parse
import html as html_lib

# Tente importar a biblioteca de Text-to-Speech
try:
    import pyttsx3
except ImportError:
    # Em celulares (Pydroid 3 / Termux), o pyttsx3 geralmente não roda sem libs nativas do Android.
    # O código continuará rodando normalmente no modo texto.
    pyttsx3 = None

# --- Constantes ---
MEMORIA_FILE = "memoria.json"
PERGUNTAS_FILE = "perguntas.json"
CHANCE_PERGUNTA_ALEATORIA = 0.15

# ------------------ Voz ------------------
engine = pyttsx3.init() if pyttsx3 else None

def falar(texto: str) -> None:
    if engine:
        try:
            engine.say(texto)
            engine.runAndWait()
        except Exception:
            pass

# ------------------ Verificação de Conexão ------------------
def tem_conexao_internet() -> bool:
    """Verifica se há conexão ativa com a internet."""
    try:
        # Tenta se conectar ao DNS do Google na porta 53
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

# ------------------ Módulo de Pesquisa Direta ------------------
def pesquisar_na_internet(termo: str) -> str:
    """
    Busca explicações e resumos diretos sobre o termo na Wikipédia e no DuckDuckGo,
    ignorando anúncios, ofertas de lojas e links de compras.
    """
    # Checa a internet antes de tentar fazer as requisições
    if not tem_conexao_internet():
        return "Você está sem internet!"

    termo_limpo = termo.strip()
    headers = {'User-Agent': 'HollowIA/1.0 (Educational Chatbot)'}
    
    # 1. Tenta buscar uma definição/resumo conceitual na Wikipédia (em português)
    url_wiki = f"https://pt.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(termo_limpo)}"
    try:
        req = urllib.request.Request(url_wiki, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as response:
            dados = json.loads(response.read().decode('utf-8'))
            if "extract" in dados and dados["extract"]:
                return dados["extract"]
    except Exception:
        pass  # Se não achar na Wikipédia, passa para a tentativa abaixo

    # 2. Busca no DuckDuckGo focando em conceitos/resumos diretos (Instant Answer)
    url_ddg = f"https://api.duckduckgo.com/?q={urllib.parse.quote(termo_limpo)}&format=json&no_html=1&kl=br-pt"
    try:
        req = urllib.request.Request(url_ddg, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as response:
            dados = json.loads(response.read().decode('utf-8'))
            
            # Resumo direto
            if dados.get("AbstractText"):
                return dados["AbstractText"]
            
            # Tópicos relacionados caso haja desambiguação
            if dados.get("RelatedTopics"):
                for topico in dados["RelatedTopics"]:
                    if isinstance(topico, dict) and "Text" in topico:
                        return topico["Text"]
    except Exception:
        pass

    return f"Não encontrei uma explicação direta sobre '{termo_limpo}'. Tente especificar melhor o assunto."

# ------------------ Memória e Aprendizado ------------------
def carregar_memoria() -> Dict[str, List[Dict[str, Any]]]:
    if os.path.exists(MEMORIA_FILE):
        try:
            with open(MEMORIA_FILE, "r", encoding="utf-8") as f:
                memoria = json.load(f)
                if "aprendizado" not in memoria or not isinstance(memoria["aprendizado"], list):
                    return {"aprendizado": []}
                return memoria
        except (json.JSONDecodeError, IOError):
            print(f"(Aviso: Não foi possível ler '{MEMORIA_FILE}'. Começando com memória vazia.)")
            return {"aprendizado": []}
    return {"aprendizado": []}

def salvar_memoria(memoria: Dict[str, List[Dict[str, Any]]]) -> None:
    try:
        with open(MEMORIA_FILE, "w", encoding="utf-8") as f:
            json.dump(memoria, f, indent=4, ensure_ascii=False)
    except IOError:
        print(f"(Erro: Não foi possível salvar '{MEMORIA_FILE}'.)")

def ensinar(
    memoria: Dict[str, List[Dict[str, Any]]],
    assunto: str,
    resposta: str,
    pergunta_followup: Optional[str] = None
) -> None:
    assunto_lower = assunto.lower().strip()
    memoria["aprendizado"] = [
        item for item in memoria["aprendizado"]
        if item.get("assunto", "").lower().strip() != assunto_lower
    ]
    novo_conhecimento = {
        "assunto": assunto,
        "resposta": resposta,
        "pergunta_followup": pergunta_followup
    }
    memoria["aprendizado"].append(novo_conhecimento)
    salvar_memoria(memoria)
    print(f"(Debug: Aprendi -> {novo_conhecimento})")

def corrigir(
    memoria: Dict[str, List[Dict[str, Any]]],
    assunto_a_corrigir: str,
    nova_resposta: str,
    nova_pergunta: Optional[str] = None
) -> None:
    ensinar(memoria, assunto_a_corrigir, nova_resposta, pergunta_followup=nova_pergunta)

def combiner_resposta(memoria: Dict, entrada: str) -> Optional[Dict[str, Any]]:
    entrada_lower = entrada.lower().strip()
    for item in memoria.get("aprendizado", []):
        assunto = item.get("assunto", "").lower().strip()
        if assunto and assunto in entrada_lower:
            return item
    return None

# ------------------ Personalidade ------------------
def detectar_personalidade(entrada: str) -> str:
    entrada_lower = entrada.lower()
    if any(p in entrada_lower for p in ["triste", "chateado", "mal", "deprimido"]):
        return "carinhosa"
    if any(p in entrada_lower for p in ["piada", "haha", "kkk", "engraçado", "lol"]):
        return "engraçada"
    if "?" in entrada:
        return "curiosa"
    return "séria"

def aplicar_personalidade(resposta: str, personality: str) -> str:
    emojis = {
        "carinhosa": " 💙",
        "engraçada": " 😂",
        "curiosa": " 🤔"
    }
    return resposta + emojis.get(personality, "")

# ------------------ Perguntas Aleatórias ------------------
def carregar_perguntas() -> List[str]:
    perguntas_padrao = ["Você gosta de História?", "Qual é a sua comida favorita?"]
    if os.path.exists(PERGUNTAS_FILE):
        try:
            with open(PERGUNTAS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return perguntas_padrao
    return perguntas_padrao

def fazer_pergunta(contexto: List[Dict[str, str]]) -> str:
    perguntas = carregar_perguntas()
    perguntas_nao_feitas = [p for p in perguntas if not any(p in c.get("IA", "") for c in contexto[-5:])]
    return random.choice(perguntas_nao_feitas) if perguntas_nao_feitas else random.choice(perguntas)

# ------------------ Geração de Perguntas por Extração ------------------
def extrair_assunto_principal(texto: str) -> Optional[str]:
    padroes = [
        r'eu gosto de (.+)', r'eu adoro (.+)', r'minha cor favorita é (.+)',
        r'meu filme favorito é (.+)', r'eu acho (.+) interessante', r'estou aprendendo sobre (.+)'
    ]
    texto_lower = texto.lower().strip()
    for padrao in padroes:
        match = re.search(padrao, texto_lower)
        if match:
            assunto = match.group(1).strip()
            return re.sub(r'[.!?]$', '', assunto)
    return None

def gerar_pergunta_criativa(assunto: str) -> str:
    templates = [
        f"Que legal! O que mais você pode me dizer sobre {assunto}?",
        f"Interessante. Por que você se interessa por {assunto}?",
        f"Hmm, {assunto}... Me conte uma curiosidade sobre isso!",
        f"Qual é a sua parte favorita quando se trata de {assunto}?",
        f"Entendi. E desde quando você gosta de {assunto}?"
    ]
    return random.choice(templates)

# ------------------ Processamento Principal ------------------
def processar_entrada(
    memoria: Dict,
    entrada: str,
    contexto: List[Dict[str, str]],
    personalidade: str
) -> Union[Dict[str, Any], str]:
    entrada_clean = entrada.lower().strip()

    # Lógica de Correção
    if entrada_clean == "isso está errado":
        falar("Oh, entendi. Me corrija, por favor!")
        print("IA: Oh, entendi. Me corrija, por favor!")
        ultima_entrada_usuario = next((item["Você"] for item in reversed(contexto) if "Você" in item), None)
        
        if ultima_entrada_usuario:
            correcao = input(f"Você (corrige sobre '{ultima_entrada_usuario}'): ")
            nova_pergunta = input("Você (nova pergunta de continuação, opcional): ")
            corrigir(memoria, ultima_entrada_usuario, correcao.strip(), nova_pergunta.strip() or None)
            return aplicar_personalidade("Ok! Aprendi a correção. Obrigado!", personalidade)
        else:
            return aplicar_personalidade("Não tenho certeza do que corrigir.", personalidade)

    # --- INTEGRAÇÃO COM A INTERNET ---
    gatilhos_busca = ["pesquise sobre", "o que é", "quem foi", "pesquise"]
    if any(entrada_clean.startswith(g) for g in gatilhos_busca):
        termo_busca = re.sub(r'^(pesquise sobre|o que é|quem foi|pesquise)\s+', '', entrada, flags=re.IGNORECASE).strip()
        
        if termo_busca:
            resultado_web = pesquisar_na_internet(termo_busca)
            
            # Caso esteja sem internet
            if resultado_web == "Você está sem internet!":
                return aplicar_personalidade("Você está sem internet!", personalidade)
            
            sugestao_busca = f"Deixe-me dar uma olhada na internet sobre {termo_busca}..."
            print(f"IA: {sugestao_busca}")
            falar(sugestao_busca)
            
            return {
                "resposta": f"Encontrei isso: {resultado_web}",
                "pergunta_followup": "Quer pesquisar mais alguma coisa?"
            }

    # Tenta encontrar uma resposta na memória local
    item_encontrado = combiner_resposta(memoria, entrada)
    if item_encontrado:
        return item_encontrado

    # Se não sabe a resposta localmente, inicia o aprendizado
    falar("Eu não sei como responder a isso. O que eu deveria dizer?")
    print("IA: Eu não sei como responder a isso. O que eu deveria dizer?")

    nova_resposta = input("Você (ensina a IA): ")
    if nova_resposta.strip():
        pergunta_followup = None
        assunto_extraido = extrair_assunto_principal(entrada)
        if not assunto_extraido:
            assunto_extraido = extrair_assunto_principal(nova_resposta)
            
        if assunto_extraido:
            pergunta_sugerida = gerar_pergunta_criativa(assunto_extraido)
            sugestao_texto = f'Ótimo! Para continuar, posso perguntar: "{pergunta_sugerida}"?'
            print(f"IA: {sugestao_texto}")
            falar(sugestao_texto)
            resposta_usuario = input("Você (pressione Enter para aceitar ou digite outra pergunta): ")
            pergunta_followup = resposta_usuario.strip() or pergunta_sugerida
        else:
            falar("Ótimo! E para deixar a conversa mais legal, que pergunta eu posso fazer de volta?")
            print("IA: Ótimo! E para deixar a conversa mais legal, que pergunta eu posso fazer de volta?")
            pergunta_followup = input("Você (pergunta de continuação): ")
            
        ensinar(memoria, entrada, nova_resposta.strip(), pergunta_followup.strip() or None)
        return aplicar_personalidade("Entendi! Aprendi sobre isso.", personalidade)
    else:
        return aplicar_personalidade("Acho que você não digitou uma resposta. Sem problemas.", personalidade)

# ------------------ Loop Principal ------------------
def main() -> None:
    memoria = carregar_memoria()
    contexto: List[Dict[str, str]] = []
    print("HollowIA iniciada! Digite 'sair' para terminar.")
    print("Dica: Digite 'pesquise sobre [assunto]' para ativar a busca na internet.")
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
            break
            
        personalidade = detectar_personalidade(entrada)
        resultado = processar_entrada(memoria, entrada, contexto, personalidade)
        
        if isinstance(resultado, dict):
            resposta_principal = aplicar_personalidade(resultado["resposta"], personalidade)
            print("IA:", resposta_principal)
            falar(resposta_principal)
            contexto.append({"Você": entrada, "IA": resposta_principal})
            
            if resultado.get("pergunta_followup"):
                pergunta = resultado["pergunta_followup"]
                print("IA (pergunta):", pergunta)
                falar(pergunta)
                contexto.append({"IA": pergunta})
        else:
            resposta_simples = resultado
            print("IA:", resposta_simples)
            falar(resposta_simples)
            contexto.append({"Você": entrada, "IA": resposta_simples})
            
        if random.random() < CHANCE_PERGUNTA_ALEATORIA:
            pergunta_aleatoria = fazer_pergunta(contexto)
            print("IA (puxando assunto):", pergunta_aleatoria)
            falar(pergunta_aleatoria)
            contexto.append({"IA": pergunta_aleatoria})

if __name__ == "__main__":
    main()
