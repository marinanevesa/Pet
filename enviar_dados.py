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
            # 1. Extrai a CATEGORIA (C:) - está no final
            categoria = "Medicamentos"
            categoria_match = re.search(r'C:\s*(.+?)$', texto)
            if categoria_match:
                categoria = categoria_match.group(1).strip()
                texto = texto[:categoria_match.start()].strip()

            # 2. Extrai as TAGS (separadas por ;) - vem antes de C:
            tags = "NaN"
            tags_match = re.search(r'TAGS:\s*(.+?)\.?\s*$', texto)
            if tags_match:
                tags_raw = tags_match.group(1).strip().rstrip(';').rstrip('.')
                # Divide por ; e retorna como string com cada tag
                tags = "; ".join([tag.strip() for tag in tags_raw.split(';') if tag.strip()])
                texto = texto[:tags_match.start()].strip()

            # 3. Separa Pergunta (P:) e Resposta (R:)
            partes_pr = re.split(r'\s+R:\s+', texto, flags=re.IGNORECASE)
            pergunta = partes_pr[0].replace("P:", "").strip()
            resto = partes_pr[1] if len(partes_pr) > 1 else ""

            # 4. Extrai a FONTE (Ref: ou FONTE:)
            fonte = "NaN"
            fonte_match = re.search(r'\(Ref:\s*(.+?)\)|FONTE:\s*(.+?)$', resto)
            if fonte_match:
                fonte = fonte_match.group(1) if fonte_match.group(1) else fonte_match.group(2)
                fonte = fonte.rstrip(')')
                resto = re.sub(r'\(Ref:\s*.+?\)|FONTE:\s*.+?$', '', resto).strip()

            # 5. O que sobrou é a resposta
            resposta = resto.strip()

            # Monta o documento
            item = {
                "question": pergunta,
                "answer": resposta,
                "tags": tags,
                "category": categoria,
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