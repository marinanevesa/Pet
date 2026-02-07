import os
import re
import json
from datetime import datetime, timezone
from dotenv import load_dotenv
from pymongo import MongoClient
from docx import Document

# 1. Carrega as variáveis de ambiente
load_dotenv()
uri = os.getenv("MONGODB_URI")

# ============================================================================
# CONFIGURAÇÃO DOS ARQUIVOS
# ============================================================================
ARQUIVOS_PROCESSAR = [
    ("./faqs/medicamento.docx", "Medicamentos"),
    ("./faqs/local.docx", "Local"),
    ("./faqs/vacinas.docx", "Vacina"),
    ("./faqs/FAQACOESJUDICIAIS.docx", "Ações Judiciais"),
    ("./faqs/FAQCDI.docx", "CDI"),
    ("./faqs/FAQREMOCAOINTERNA.docx", "Remoção Interna"),
    ("./faqs/FAQREMOCAOEXTERNA.docx", "Remoção Externa"),
    ("./faqs/FAQFARMACIADEMANIPULACAO.docx", "Farmacia de Manipulação"),
    ("./faqs/FAQFARMACIAMUNICIPAL.docx", "Farmacia Municipal"),
    ("./faqs/FAQUBSCITYPETROPOLIS.docx", "UBS City Petrópolis"),
    ]

def subir_faq(nome_arquivo, categoria, collection):
    """
    Processa um arquivo .docx e envia as FAQs para o MongoDB
    
    Args:
        nome_arquivo: Caminho do arquivo .docx
        categoria: Categoria a ser atribuída às FAQs deste arquivo
        collection: Coleção do MongoDB onde inserir os dados
    """
    try:
        doc = Document(nome_arquivo)
    except Exception as e:
        print(f"Erro ao abrir arquivo {nome_arquivo}: {e}")
        return 0
    count = 0

    for para in doc.paragraphs:
        texto = para.text.strip()
        if not texto or "P:" not in texto.upper(): 
            continue

        try:
            # 1. Extrai as TAGS (separadas por vírgula) - vem no final antes do ponto
            tags = "NaN"
            tags_match = re.search(r'TAGS:\s*(.+?)\.?\s*$', texto)
            if tags_match:
                tags_raw = tags_match.group(1).strip().rstrip('.').rstrip(',')
                # Divide por vírgula e retorna como lista
                tags_list = [tag.strip() for tag in tags_raw.split(',') if tag.strip()]
                texto = texto[:tags_match.start()].strip()
            else:
                tags_list = []

            # 2. Extrai a FONTE (Ref: ou FONTE:)
            fonte = "NaN"
            fonte_match = re.search(r'\(Ref:\s*(.+?)\)|\(FONTE:\s*(.+?)\)', texto)
            if fonte_match:
                fonte = fonte_match.group(1) if fonte_match.group(1) else fonte_match.group(2)
                fonte = fonte.strip()
                texto = texto[:fonte_match.start()].strip()

            # 3. Separa Pergunta (P:) e Resposta (R:)
            partes_pr = re.split(r'\s+R:\s+', texto, flags=re.IGNORECASE)
            if len(partes_pr) < 2:
                continue
                
            pergunta = partes_pr[0].replace("P:", "").strip()
            resposta = partes_pr[1].strip()

            # Monta o documento com a categoria recebida
            item = {
                "question": pergunta,
                "answer": resposta,
                "tags": tags_list,
                "source": fonte,
                "category": categoria,
                "isActive": True,
                "updatedAt": datetime.now(timezone.utc)
            }
            
            collection.insert_one(item)
            count += 1
            
        except Exception as err:
            print(f"Erro ao processar linha: {texto[:50]}... | Erro: {err}")

    print(f"\nTotal inserido do arquivo: {count} perguntas")
    return count


def main():
    """
    Função principal que conecta ao MongoDB e processa todos os arquivos configurados
    """
    print("=" * 100)
    print("INICIANDO ENVIO DE FAQs PARA O MONGODB")
    print("=" * 100 + "\n")
    
    # Conecta ao MongoDB
    try:
        client = MongoClient(uri)
        db = client['ministerio_saude']
        collection = db['faq_medicamentos']
        print("Conectado ao MongoDB com sucesso!")
        
        # Limpa a coleção antes de inserir novos dados
        deleted_count = collection.delete_many({}).deleted_count
        print(f"Removidos {deleted_count} documentos antigos da coleção\n")
        
    except Exception as e:
        print(f"Erro ao conectar ao MongoDB: {e}")
        return
    
    total_inseridos = 0
    
    # Processa cada arquivo
    for arquivo, categoria in ARQUIVOS_PROCESSAR:
        print("\n" + "█" * 100)
        print(f"PROCESSANDO: {arquivo}")
        print(f"CATEGORIA: {categoria}")
        print("█" * 100 + "\n")
        
        count = subir_faq(arquivo, categoria, collection)
        total_inseridos += count
        
        print()
    
    # Resumo final
    print("\n" + "=" * 100)
    print("RESUMO FINAL")
    print("=" * 100)
    print(f"Total de arquivos processados: {len(ARQUIVOS_PROCESSAR)}")
    print(f"Total de FAQs inseridas no MongoDB: {total_inseridos}")
    print("\n" + "=" * 100)
    print("ENVIO CONCLUÍDO COM SUCESSO!")
    print("=" * 100)
    
    # Fecha a conexão
    if client:
        client.close()
        print("Conexão com MongoDB fechada.")


if __name__ == "__main__":
    main() 