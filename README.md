# 📜 Script de FAQs Inteligente - Ministério da Saúde

Este projeto automatiza a extração de Perguntas e Respostas (FAQs) de documentos hospedados no **Google Drive** e realiza a sincronização com um banco de dados **MongoDB Atlas**. Ele foi desenhado para facilitar a curadoria de dados do chatbot de saúde, permitindo que a equipe atualize apenas o Word no Drive para que o robô aprenda as novas informações.

---

## 🛠️ O que o Script Faz

1. **Conexão Google Cloud**: Autentica-se via Conta de Serviço para acessar pastas específicas no Google Drive.
2. **Download Dinâmico**: Localiza todos os arquivos `.docx` dentro da pasta configurada.
3. **Processamento de Texto (Regex)**:
* Varre o documento em busca de padrões `P:` (Pergunta) e `R:` (Resposta).
* Suporta perguntas e respostas na mesma linha ou em linhas separadas.
* Detecta automaticamente mudanças de **[ASSUNTO]** dentro do texto.


4. **Extração de Metadados**: Separa de forma inteligente as `TAGS` e a `FONTE` (Referência) de cada item.
5. **Sincronização MongoDB**:
* Limpa a base antiga para evitar duplicidade.
* Insere os novos dados com data de atualização (`updatedAt`) e status ativo.



---

## 🚀 Como Rodar o Código

### 1. Pré-requisitos

Certifique-se de ter o Python 3.8+ instalado e as bibliotecas necessárias:

```bash
pip install pymongo python-docx python-dotenv google-api-python-client google-auth-httplib2 google-auth-oauthlib

```

### 2. Configuração de Credenciais

* **MongoDB**: Obtenha sua Connection String no MongoDB Atlas.
* **Google Drive**:
* Crie um projeto no [Google Cloud Console](https://console.cloud.google.com/).
* Ative a **Google Drive API**.
* Crie uma **Conta de Serviço**, gere uma chave JSON e salve-a na raiz do projeto com o nome `credentials.json`.
* **Importante**: Compartilhe a pasta do Google Drive com o e-mail da sua Conta de Serviço (ex: `leitor-drive-faq@...`).



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

* `enviar_dados.py`: O "cérebro" do projeto. Faz o download do Drive e upload para o Mongo.
* `test_enviar_dados.py`: Versão de segurança para validar a lógica de extração.
* `.env`: Guarda sua senha do banco de dados (não deve ser enviado ao GitHub).
* `credentials.json`: Chave de acesso ao Google Cloud (não deve ser enviado ao GitHub).
* `.gitignore`: Protege seus arquivos sensíveis de serem expostos.

---

### ⚠️ Aviso de Segurança

> As chaves de API e senhas foram removidas deste repositório por segurança. Caso tenha exposto sua `private_key` no histórico do Git, revogue-a imediatamente no console do Google Cloud.
