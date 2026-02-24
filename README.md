# 📜 Script de FAQs Inteligente - Ministério da Saúde

Este projeto automatiza a extração de Perguntas e Respostas (FAQs) de documentos hospedados no **Google Drive** e realiza a sincronização com um banco de dados **MongoDB Atlas**, incluindo geração de **embeddings vetoriais** para busca semântica. Ele foi desenhado para facilitar a curadoria de dados do chatbot de saúde, permitindo que a equipe atualize apenas o Word no Drive para que o robô aprenda as novas informações.

---

## 🛠️ O que o Script Faz

1. **Conexão Google Cloud**: Autentica-se via Conta de Serviço para acessar pastas específicas no Google Drive.
2. **Download Dinâmico**: Localiza todos os arquivos `.docx` dentro da pasta configurada.
3. **Processamento de Texto (Regex)**:
   - Varre o documento em busca de padrões `P:` (Pergunta) e `R:` (Resposta).
   - Suporta perguntas e respostas na mesma linha ou em linhas separadas.
   - Detecta automaticamente mudanças de **[ASSUNTO]** dentro do texto.
4. **Extração de Metadados**: Separa de forma inteligente as `TAGS` e a `FONTE` (Referência) de cada item.
5. **Geração de Embeddings**: Usa a API do Google Gemini para gerar vetores semânticos de cada FAQ.
6. **Sincronização Inteligente**:
   - Modo incremental: só processa arquivos que mudaram no Drive.
   - Reutiliza embeddings de conteúdo que não foi alterado (economia de API).
   - Cria índice vetorial no MongoDB Atlas para busca semântica.

---

## 🚀 Como Rodar o Código

### 1. Pré-requisitos

Certifique-se de ter o Python 3.8+ instalado e as bibliotecas necessárias:

```bash
pip install pymongo python-docx python-dotenv google-api-python-client google-auth-httplib2 google-auth-oauthlib google-genai
```

### 2. Configuração de Credenciais

* **MongoDB**: Obtenha sua Connection String no MongoDB Atlas.
* **Google Gemini**: Obtenha sua API Key em [aistudio.google.com/apikey](https://aistudio.google.com/apikey).
* **Google Drive**:
  - Crie um projeto no [Google Cloud Console](https://console.cloud.google.com/).
  - Ative a **Google Drive API**.
  - Crie uma **Conta de Serviço**, gere uma chave JSON e salve-a na raiz do projeto com o nome `credentials.json`.
  - **Importante**: Compartilhe a pasta do Google Drive com o e-mail da sua Conta de Serviço (ex: `leitor-drive-faq@...`).



### 3. Variáveis de Ambiente (.env)

> ⚠️ **IMPORTANTE**: O arquivo `.env` contém suas credenciais secretas. **NUNCA** envie este arquivo para o GitHub!

Copie o arquivo de exemplo e preencha com suas credenciais:

```bash
cp .env.example .env
```

Edite o `.env` com os valores reais:

```env
# String de conexão do MongoDB Atlas
MONGODB_URI=mongodb+srv://usuario:senha@cluster.mongodb.net/database

# Chave da API do Google Gemini
GEMINI_API_KEY=sua_api_key_aqui

# ID da pasta do Google Drive (pegue da URL da pasta)
ID_PASTA_DRIVE=17J91pfYw-_AQFpt8_Jls96PBowM-Az-5

# Caminho para credenciais do Google (opcional, padrão: credentials.json)
FILE_CREDENTIALS=credentials.json
```

> 💡 **Para suas colegas**: O ID da pasta do Drive e credenciais do banco **não podem ficar no código fonte**! Se subirem pro GitHub, qualquer pessoa pode acessar nossos dados.

### 4. Execução

Para processar e enviar os dados para o banco:

```bash
python enviar_dados.py

```

Para apenas **testar a extração** e ver o que seria enviado (sem tocar no banco de dados):

```bash
python test_enviar_dados.py

```

---

## 📝 Formatação dos Documentos (.docx)

Para que o script reconheça as informações, os documentos no Drive devem seguir um destes padrões:

**Opção A (Mesma linha):**

> P: Qual a dose do paracetamol? R: 500mg. TAGS: dose, paracetamol. FONTE: Protocolo MS 2024.

**Opção B (Linhas separadas):**

> P: Como armazenar a insulina?
> R: Deve ser mantida em refrigeração entre 2°C e 8°C.
> TAGS: armazenamento, insulina. FONTE: Manual ABC.

**Mudança de Categoria:**

> [ASSUNTO: Medicamentos Especiais]

---

## 📂 Estrutura do Projeto

```
Pet/
├── enviar_dados.py      # Script principal: extrai FAQs, gera embeddings e sincroniza com MongoDB
├── test_enviar_dados.py # Versão de teste: valida extração sem tocar no banco nem gerar embeddings
├── lib/
│   └── gemini_embendding.py  # Módulo de geração de embeddings via Google Gemini
├── .env                 # Suas credenciais (NÃO enviar ao GitHub!)
├── .env.example         # Modelo do .env para compartilhar com a equipe
├── credentials.json     # Chave da Conta de Serviço Google (NÃO enviar ao GitHub!)
├── .gitignore           # Protege arquivos sensíveis de serem expostos
└── README.md            # Esta documentação
```

---

## 🔄 Posso Rodar Múltiplas Vezes?

**Sim!** O script é incremental e inteligente:

| Situação | O que acontece |
|----------|----------------|
| Arquivo não mudou no Drive | ⏭️ Pula (não gasta API/tempo) |
| Arquivo foi editado | 🔄 Atualiza só esse arquivo |
| Conteúdo P/R igual ao anterior | 💰 Reutiliza embedding existente |
| Conteúdo P/R mudou | 🆕 Gera novo embedding |

---

### ⚠️ Aviso de Segurança

> As chaves de API e senhas foram removidas deste repositório por segurança. Caso tenha exposto sua `private_key` no histórico do Git, revogue-a imediatamente no console do Google Cloud.
