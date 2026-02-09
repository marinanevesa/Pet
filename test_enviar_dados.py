from docx import Document
from datetime import datetime, timezone
import re
import json

# ============================================================================
# CONFIGURAÇÃO DOS ARQUIVOS
# Para adicionar um novo arquivo: adicione uma tupla (caminho, categoria)
# Para remover: comente ou delete a linha
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
    ("./faqs/FAQNAIA.docx", "NAIA"),
    ("./faqs/FAQPSI.docx", "PSI"),
    ("./faqs/FAQPSR.docx", "PSR"),
    ("./faqs/FAQUAC.docx", "UAC"),
    ("./faqs/FAQSAUDEMENTAL.docx", "Saúde Mental"),
    ("./faqs/FAQNGA16.docx", "NGA 16"),
    ("./faqs/FAQCENTROOFTALMOLOGICO.docx", "Centro Oftalmológico"),
    ("./faqs/FAQCAPSIIIFLORESCER.docx", "CAPS III Florescer"),
    ("./faqs/FAQCASADODIABETICO.docx", "Casa do Diabético"),
    ("./faqs/FAQCAPSADIIIRENASCER.docx", "CAPS AD III Renascer"),
]

def processar_faq(nome_arquivo, categoria):
    """
    Processa um arquivo .docx e extrai as FAQs formatadas
    
    Args:
        nome_arquivo: Caminho do arquivo .docx
        categoria: Categoria a ser atribuída às FAQs deste arquivo
    """
    try:
        doc = Document(nome_arquivo)
    except Exception as e:
        print(f"Erro ao abrir arquivo {nome_arquivo}: {e}")
        return []
    
    count = 0
    faqs = []

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

            # Monta o documento na ordem com a categoria recebida
            item = {
                "question": pergunta,
                "answer": resposta,
                "tags": tags_list,
                "source": fonte,
                "category": categoria,
                "isActive": True,
                "updatedAt": datetime.now(timezone.utc).isoformat()
            }
            
            faqs.append(item)
            count += 1
            
            # Imprime cada FAQ formatado
            print(json.dumps(item, ensure_ascii=False, indent=2))
            print("-" * 80)
            
        except Exception as err:
            print(f"⚠️ Erro ao processar linha: {texto[:50]}... | Erro: {err}")

    print(f"\nTotal processado no arquivo: {count} perguntas")
    return faqs


def main():
    """
    Função principal que processa todos os arquivos configurados
    """
    print("=" * 100)
    print("INICIANDO PROCESSAMENTO DE TODOS OS ARQUIVOS")
    print("=" * 100 + "\n")
    
    todos_faqs = []
    
    for arquivo, categoria in ARQUIVOS_PROCESSAR:
        print("\n" + "█" * 100)
        print(f"PROCESSANDO: {arquivo}")
        print(f"CATEGORIA: {categoria}")
        print("█" * 100 + "\n")
        
        faqs = processar_faq(arquivo, categoria)
        todos_faqs.extend(faqs)
        
        print("\n")
    
    # Resumo final
    print("\n" + "=" * 100)
    print("RESUMO FINAL")
    print("=" * 100)
    print(f"Total de arquivos processados: {len(ARQUIVOS_PROCESSAR)}")
    print(f"Total de FAQs extraídas: {len(todos_faqs)}")
    
    # Imprime o JSON completo de todos os FAQs
    print("\n" + "=" * 100)
    print("JSON COMPLETO DE TODOS OS FAQs:")
    print("=" * 100)
    print(json.dumps(todos_faqs, ensure_ascii=False, indent=2))
    print("\n" + "=" * 100)
    print("PROCESSAMENTO CONCLUÍDO COM SUCESSO!")
    print("=" * 100)


if __name__ == "__main__":
    main()
 