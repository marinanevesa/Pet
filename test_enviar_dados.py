import os
import re
import json
from datetime import datetime, timezone
from docx import Document

# ============================================================================
# CONFIGURAÇÕES
# ============================================================================
PASTA_FAQS = "./faqs/"  # Certifique-se que esta pasta existe com seus arquivos

def extrair_metadados(texto_bloco):
    tags = []
    fonte = ""

    # 1. Extração de FONTE
    fonte_match = re.search(r'(?:FONTE:|Ref:|\(Ref:)\s*([^)\n\t]+)', texto_bloco, re.IGNORECASE)
    if fonte_match:
        fonte = fonte_match.group(1).strip().rstrip('.)').lower()

    # 2. Extração de TAGS
    tags_match = re.search(r'TAGS:\s*(.+?)(?=\s*P:|$|\n)', texto_bloco, re.IGNORECASE)
    if tags_match:
        conteudo_tags = tags_match.group(1).strip().lower()
        conteudo_tags = conteudo_tags.replace('#', ' ')
        lista_bruta = [t.strip() for t in re.split(r'[,\s\t]+', conteudo_tags) if t.strip()]
        tags = [t for t in lista_bruta if t not in ["p:", "r:", "fonte:", "ref:"]]
    
    return tags, fonte

def simular_processamento():
    total = 0
    if not os.path.exists(PASTA_FAQS):
        print(f"❌ Erro: A pasta '{PASTA_FAQS}' não foi encontrada.")
        return

    print(f"--- Iniciando Simulação de Extração (Chatbot Saúde) ---\n")

    for raiz, _, arquivos in os.walk(PASTA_FAQS):
        for nome_arquivo in arquivos:
            if nome_arquivo.endswith('.docx') and not nome_arquivo.startswith('~$'):
                caminho = os.path.join(raiz, nome_arquivo)
                doc = Document(caminho)
                
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
                        resposta = partes[1].strip().lower()
                        resposta = re.split(r'tags:|fonte:|ref:', resposta, flags=re.IGNORECASE)[0].strip()

                    # Caso B: Linhas separadas
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

                        # Simulação do Objeto que iria para o Banco
                        doc_fake = {
                            "category": categoria_atual,
                            "question": pergunta,
                            "answer": resposta,
                            "tags": tags,
                            "source": fonte
                        }
                        
                        print(f"✅ DOCUMENTO EXTRAÍDO:")
                        print(json.dumps(doc_fake, indent=4, ensure_ascii=False))
                        print("-" * 20)
                        total += 1

    print(f"\n--- Fim da Simulação ---")
    print(f"Total de FAQs processados: {total}")

if __name__ == "__main__":
    simular_processamento()