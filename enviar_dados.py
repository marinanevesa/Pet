import os
import re
import json
from datetime import datetime, timezone
from dotenv import load_dotenv
from pymongo import MongoClient
from docx import Document

# 1. Carrega as variáveis de ambiente
load_dotenv()
URI = os.getenv("MONGODB_URI")
PASTA_FAQS = "./faqs/"

import os
import re
import json
from datetime import datetime, timezone
from dotenv import load_dotenv
from pymongo import MongoClient
from docx import Document

# ============================================================================
# CONFIGURAÇÕES
# ============================================================================

def extrair_metadados(texto_bloco):
    """Extrai Tags e Fonte isolando-as e convertendo para minúsculo"""
    tags = []
    fonte = ""

    # 1. Extração de FONTE / Ref
    fonte_match = re.search(r'(?:FONTE:|Ref:|\(Ref:)\s*([^)\n\t]+)', texto_bloco, re.IGNORECASE)
    if fonte_match:
        fonte = fonte_match.group(1).strip().rstrip('.)').lower() # toLowerCase aqui

    # 2. Extração de TAGS
    tags_match = re.search(r'TAGS:\s*(.+?)(?=\s*P:|$|\n)', texto_bloco, re.IGNORECASE)
    if tags_match:
        conteudo_tags = tags_match.group(1).strip().lower() # toLowerCase aqui
        conteudo_tags = conteudo_tags.replace('#', ' ')
        lista_bruta = [t.strip() for t in re.split(r'[,\s\t]+', conteudo_tags) if t.strip()]
        
        # Filtro para não deixar vazar P: ou R: como tag
        tags = [t for t in lista_bruta if t not in ["p:", "r:", "fonte:", "ref:"]]
    
    return tags, fonte

def processar_faqs(collection):
    total = 0
    for raiz, _, arquivos in os.walk(PASTA_FAQS):
        for nome_arquivo in arquivos:
            if nome_arquivo.endswith('.docx') and not nome_arquivo.startswith('~$'):
                caminho = os.path.join(raiz, nome_arquivo)
                doc = Document(caminho)
                
                # Categoria inicial em minúsculo
                categoria_atual = nome_arquivo.replace("FAQ", "").replace(".docx", "").strip().lower()
                paragrafos = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
                
                pergunta_pendente = ""
                
                for i, linha in enumerate(paragrafos):
                    if "[ASSUNTO:" in linha.upper():
                        assunto_match = re.search(r'\[ASSUNTO:\s*(.+?)\]', linha, re.IGNORECASE)
                        if assunto_match: 
                            categoria_atual = assunto_match.group(1).strip().lower() # toLowerCase aqui
                        continue

                    pergunta, resposta = None, None

                    # Caso A: P e R na mesma linha
                    if "P:" in linha.upper() and "R:" in linha.upper():
                        partes = re.split(r'\s*R:\s*', linha, flags=re.IGNORECASE)
                        pergunta = partes[0].replace("P:", "").replace("p:", "").strip().lower()
                        resposta = partes[1].strip().lower()
                        resposta = re.split(r'tags:|fonte:|ref:', resposta, flags=re.IGNORECASE)[0].strip()

                    # Caso B: Linhas separadas (UPA Anita)
                    elif linha.upper().startswith("P:"):
                        pergunta_pendente = linha.replace("P:", "").replace("p:", "").strip().lower()
                        continue
                    elif linha.upper().startswith("R:") and pergunta_pendente:
                        pergunta = pergunta_pendente
                        resposta = linha.replace("R:", "").replace("r:", "").strip().lower()
                        resposta = re.split(r'tags:|fonte:|ref:', resposta, flags=re.IGNORECASE)[0].strip()
                        pergunta_pendente = ""

                    if pergunta and resposta:
                        bloco_contexto = " ".join(paragrafos[i:i+2])
                        tags, fonte = extrair_metadados(bloco_contexto)

                        collection.insert_one({
                            "question": pergunta,
                            "answer": resposta,
                            "tags": tags,
                            "source": fonte,
                            "category": categoria_atual,
                            "isActive": True,
                            "updatedAt": datetime.now(timezone.utc)
                        })
                        total += 1
    return total

def main():
    try:
        client = MongoClient(URI)
        db = client['ministerio_saude']
        col = db['faq_medicamentos']
        col.delete_many({}) # Limpa para o novo padrão minúsculo
        
        print("Iniciando upload...")
        total = processar_faqs(col)
        print(f"Sucesso! {total} documentos padronizados inseridos.")
        client.close()
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    main()