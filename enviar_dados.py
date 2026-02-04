from pymongo import MongoClient
from docx import Document
from datetime import datetime, timezone
import re
import json

uri = "mongodb+srv://marina:Ju050100@marinanevesa.rcgenti.mongodb.net/?appName=marinanevesa"

try:
    client = MongoClient(uri)
    db = client['ministerio_saude']
    collection = db['faq_medicamentos']
    collection.delete_many({}) 
    print("Conectado! Preparando para subir o FAQ completo com TAGS...")
except Exception as e:
    print(f"Erro ao conectar: {e}")

def subir_faq_v4(nome_arquivo):
    doc = Document(nome_arquivo)
    count = 0

    for para in doc.paragraphs:
        texto = para.text.strip()
        if not texto or "P:" not in texto.upper(): continue

        try:
            # 1. Separa Pergunta e Resposta (pelo divisor R:)
            partes_pr = re.split(r'[rR]:', texto)
            pergunta = partes_pr[0].replace("P:", "").strip()
            resto = partes_pr[1]

            # 2. Extrai as TAGS (estão entre colchetes [ ])
            tags = "NaN"
            tags_match = re.search(r'TAGS:\s*(\[.*?\])', resto)
            if tags_match:
                tags = tags_match.group(1)
                resto = resto.replace(tags_match.group(0), "").strip()

            # 3. Extrai a FONTE (pode ser Ref: ou FONTE:)
            fonte = "NaN"
            fonte_match = re.search(r'\(Ref: (.*?)\)|FONTE: (.*?)$', resto)
            if fonte_match:
                fonte = fonte_match.group(1) if fonte_match.group(1) else fonte_match.group(2)
                resto = resto.replace(str(fonte_match.group(0)), "").strip()

            # 4. O que sobrou no 'resto' é a resposta limpa
            resposta = resto.strip()

            # Monta o documento
            item = {
                "question": pergunta,
                "answer": resposta,
                "tags": tags,
                "category": "Medicamentos",
                "source": fonte,
                "isActive": True,
                "updatedAt": datetime.now(timezone.utc)
            }
            
            collection.insert_one(item)
            count += 1
        except Exception as err:
            print(f"Pulei uma linha com erro: {texto[:30]}... Erro: {err}")

    print(f"🚀 Missão Cumprida! {count} perguntas com TAGS enviadas com sucesso.")
    
    if client:
        client.close()

# Lembre-se de conferir se o nome do arquivo abaixo está igual ao seu no computador
subir_faq_v4("Medicamento2.docx")