import os
import re
import io
from datetime import datetime, timezone
from dotenv import load_dotenv
from pymongo import MongoClient
from docx import Document

# Bibliotecas do Google API
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

load_dotenv()

# ============================================================================
# CONFIGURAÇÕES
# ============================================================================
ID_PASTA_DRIVE = "17J91pfYw-_AQFpt8_Jls96PBowM-Az-5"
FILE_CREDENTIALS = "credentials.json"
URI_MONGO = os.getenv("MONGODB_URI")

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def get_drive_service():
    creds = service_account.Credentials.from_service_account_file(
        FILE_CREDENTIALS, scopes=SCOPES)
    return build('drive', 'v3', credentials=creds)

def extrair_metadados(texto_bloco):
    tags = []
    fonte = ""
    fonte_match = re.search(r'(?:FONTE:|Ref:|\(Ref:)\s*([^)\n\t]+)', texto_bloco, re.IGNORECASE)
    if fonte_match:
        fonte = fonte_match.group(1).strip().rstrip('.)').lower()

    tags_match = re.search(r'TAGS:\s*(.+?)(?=\s*P:|$|\n)', texto_bloco, re.IGNORECASE)
    if tags_match:
        conteudo_tags = tags_match.group(1).strip().lower()
        conteudo_tags = conteudo_tags.replace('#', ' ')
        lista_bruta = [t.strip() for t in re.split(r'[,\s\t]+', conteudo_tags) if t.strip()]
        tags = [t for t in lista_bruta if t not in ["p:", "r:", "fonte:", "ref:"]]
    
    return tags, fonte

def processar_faqs_drive(collection):
    service = get_drive_service()
    total_geral = 0
    # Dicionário para rastrear o par (pergunta, resposta) e o nome do arquivo
    pares_vistos = {} 

    query = f"'{ID_PASTA_DRIVE}' in parents and name contains '.docx' and mimeType = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    arquivos = results.get('files', [])

    if not arquivos:
        print("⚠️ Nenhum arquivo encontrado na pasta do Drive.")
        return 0

    for indice, arquivo in enumerate(arquivos, start=1):
        file_id = arquivo['id']
        nome_arquivo = arquivo['name']
        
        if nome_arquivo.startswith('~$'): continue

        request = service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()

        fh.seek(0)
        doc = Document(fh)
        
        itens_no_documento = 0
        categoria_atual = nome_arquivo.replace("FAQ", "").replace(".docx", "").strip().lower()
        paragrafos = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        pergunta_pendente = ""
        
        for i, linha in enumerate(paragrafos):
            if "[ASSUNTO:" in linha.upper():
                assunto_match = re.search(r'\[ASSUNTO:\s*(.+?)\]', linha, re.IGNORECASE)
                if assunto_match: 
                    categoria_atual = assunto_match.group(1).strip().lower()
                continue

            pergunta, resposta = None, None

            # Caso A: P e R na mesma linha
            if "P:" in linha.upper() and "R:" in linha.upper():
                partes = re.split(r'\s*R:\s*', linha, flags=re.IGNORECASE)
                pergunta = partes[0].replace("P:", "").replace("p:", "").strip().lower()
                resposta_bruta = partes[1].strip().lower()
                resposta = re.split(r'tags:|fonte:|ref:', resposta_bruta, flags=re.IGNORECASE)[0].strip()

            # Caso B: Linhas separadas
            elif linha.upper().startswith("P:"):
                pergunta_pendente = linha.replace("P:", "").replace("p:", "").strip().lower()
                continue
            elif linha.upper().startswith("R:") and pergunta_pendente:
                pergunta = pergunta_pendente
                resposta_bruta = linha.replace("R:", "").replace("r:", "").strip().lower()
                resposta = re.split(r'tags:|fonte:|ref:', resposta_bruta, flags=re.IGNORECASE)[0].strip()
                pergunta_pendente = ""

            if pergunta and resposta:
                # Chave única baseada em Pergunta + Resposta
                chave_faq = (pergunta, resposta)

                if chave_faq in pares_vistos:
                    arquivo_origem = pares_vistos[chave_faq]
                    print(f"   ⚠️ Aviso: Pergunta e Resposta duplicadas encontradas!")
                    print(f"      Conteúdo: '{pergunta[:40]}...'")
                    print(f"      -> se encontra no arquivo: {arquivo_origem} e no arquivo: {nome_arquivo}")
                else:
                    pares_vistos[chave_faq] = nome_arquivo

                bloco_contexto = " ".join(paragrafos[max(0, i-1):i+2])
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
                itens_no_documento += 1
                total_geral += 1
        
        # Define o emoji com base na quantidade de itens processados
        status_emoji = "✅" if itens_no_documento > 0 else "⭕"
        print(f"{indice} {status_emoji} FAQ ({nome_arquivo}) -> {itens_no_documento} itens processados")
                
    return total_geral

def main():
    try:
        client = MongoClient(URI_MONGO)
        db = client['ministerio_saude']
        col = db['faq_medicamentos']
        
        print("--- Iniciando Sincronização MS (Drive -> MongoDB) ---")
        col.delete_many({}) 
        
        total = processar_faqs_drive(col)
        print("---")
        print(f"Finalizado! Total de {total} itens inseridos no Banco de Dados.")
        client.close()
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()