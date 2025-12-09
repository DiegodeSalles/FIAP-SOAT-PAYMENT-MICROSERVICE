# 📋 Pré-requisitos

- **Docker** e **Docker Compose** (Recomendado)
- Ou **Python 3.13+** e **MongoDB** rodando localmente


## 🚀 Como Rodar (Docker)

Se você não quer configurar ambiente Python, use o Docker. Ele sobe a aplicação e o banco de dados automaticamente.

1. **Configure as Variáveis de Ambiente:**
   Crie um arquivo `.env` na raiz (baseado no exemplo abaixo) ou garanta que as variáveis estejam no `docker-compose.yml`.

2. **Suba o Ambiente:**
   ```bash
   docker-compose up -d --build
   ```
3. **Acesse a Documentação:**
A API estará disponível em: http://localhost:8000/docs

## 🐍 Como Rodar Manualmente (Python)
Para quem for desenvolver ou debugar o código.
1. Criar Ambiente Virtual

    Isso isola as bibliotecas do projeto do seu sistema global.
    ```PowerShell
    # Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

    ```bash
    # Linux/Mac
    python3 -m venv venv
    source venv/bin/activate
    ```
2. Instalar Dependências

```bash
pip install -r requirements.txt
```
3. Configurar Variáveis de Ambiente
Crie um arquivo .env na raiz do projeto com o seguinte conteúdo:

## Banco de Dados (MongoDB)
Se rodar local sem docker, geralmente é `localhost:27017`
```bash
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=payment_db
```

# Integração Mercado Pago
Use credenciais de teste (Sandbox)

```bash
MP_BASE_URL=https://api.mercadopago.com
MP_ACCESS_TOKEN=seu-access-token-aqui
MP_POS_ID=seu-pos-id-aqui
```

Rode o servidor de desenvolvimento (com hot-reload):
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
# ou
fastapi run src/main.py --reload --port 8000
```

# 🧪 Como Rodar os Testes

O projeto utiliza Pytest e Pytest-BDD para testes unitários e de comportamento.
```bash
pytest --cov=src
```

