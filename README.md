# Script de FAQs - Ministério da Saúde

Script para processar arquivos .docx com perguntas e respostas e enviar para o MongoDB.

## Como Usar

- Instale as dependências: `pip install pymongo python-docx python-dotenv`
- Crie um arquivo `.env` na raiz do projeto com sua URI do MongoDB

## Configuração de Arquivos

Edite a lista `ARQUIVOS_PROCESSAR` no início do arquivo `enviar_dados.py`:

```python
ARQUIVOS_PROCESSAR = [
    ("./faqs/medicamento.docx", "Medicamentos"),
    ("./faqs/local.docx", "Local"),
    ("./faqs/vacinas.docx", "Vacina"),
]
```

- **Primeiro valor**: Caminho do arquivo .docx
- **Segundo valor**: Categoria da FAQ

## Formato dos Dados

Cada parágrafo no arquivo .docx deve seguir este formato:

```
P: Sua pergunta aqui? R: Sua resposta aqui. (Ref: Fonte da informação) TAGS: tag1,tag2,tag3.
```

### Exemplo:

```
P: Onde eu posso buscar meu Ácido Fólico 5 mg comprimido de graça aqui em Franca? R: O senhor ou a senhora pode retirar nas farmácias de qualquer Unidade Básica de Saúde (UBS), os "postinhos" perto da sua casa. (Ref: REMUME Franca, pág. 2) TAGS: Ácido Fólico,local de retirada,UBS.
```

### Estrutura:

- **P:** - Inicia a pergunta
- **R:** - Inicia a resposta
- **(Ref: ...)** ou **(FONTE: ...)** - Fonte da informação (opcional)
- **TAGS:** - Lista de tags separadas por vírgula (opcional)

## Teste sem Enviar

Para testar o processamento sem enviar ao MongoDB:

```bash
python test_enviar_dados.py
```

Este comando mostra o JSON formatado no terminal sem inserir no banco.

## O que o Script Faz

1. Conecta ao MongoDB
2. Limpa a coleção existente
3. Processa cada arquivo .docx configurado
4. Extrai perguntas, respostas, tags e fontes
5. Insere os dados no MongoDB com a categoria correspondente
6. Mostra resumo do processamento
