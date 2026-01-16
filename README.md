# 🍔 Microsserviço de Pagamentos - FIAP Fastfood

![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.128+-009688?style=flat&logo=fastapi&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-Motor-47A248?style=flat&logo=mongodb&logoColor=white)
![Architecture](https://img.shields.io/badge/Architecture-Hexagonal-orange?style=flat)
![Tests](https://img.shields.io/badge/Tests-Pytest%20%7C%20BDD-brightgreen?style=flat)
[![SonarCloud](https://sonarcloud.io/api/project_badges/measure?project=DiegodeSalles_FIAP-SOAT-PAYMENT-MICROSERVICE&metric=alert_status)](https://sonarcloud.io/dashboard?id=DiegodeSalles_FIAP-SOAT-PAYMENT-MICROSERVICE)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=DiegodeSalles_FIAP-SOAT-PAYMENT-MICROSERVICE&metric=coverage)](https://sonarcloud.io/dashboard?id=DiegodeSalles_FIAP-SOAT-PAYMENT-MICROSERVICE)


Este projeto é um **Microsserviço de Pagamentos** isolado, responsável por todo o ciclo de vida financeiro dos pedidos da lanchonete.  
Ele integra-se com o **Mercado Pago** para geração de **QR Codes (Pix)** e processamento de **Webhooks**.

O projeto foi desenhado seguindo rigorosamente a **Arquitetura Hexagonal (Ports and Adapters)**, garantindo **desacoplamento**, **testabilidade** e **facilidade de manutenção**.

Este microserviço faz parte do Projeto FIAP Fastfood, [disponível aqui](https://github.com/WeesleyAlves/FIAP-SOAT-FASTFOOD-INFRA-MS).

## 🏛️ Arquitetura do Projeto

O código está organizado para separar as **regras de negócio (Domínio)** de **frameworks externos** (API, Banco de Dados).

```text
src/
├── domain/             # 🧠 Núcleo (Core): Entidades e Regras de Negócio puras
│                       #    (Não conhece banco de dados nem API)
│
├── ports/              # 🔌 Portas: Interfaces (Contratos) de entrada e saída
│                       #    que definem como o mundo externo interage com a 
│
├── use_cases/          # ⚙️ Casos de Uso: Orquestram o fluxo de dados
│                       #    (Criar Pagamento, Processar Webhook, etc.)
│
└── infrastructure/     # 🧱 Adaptadores: Implementações concretas das Portas
    ├── api/            #    Adapter de Entrada: FastAPI (Rotas, DTOs)
    ├── db/             #    Adapter de Saída: MongoDB (Motor)
    └── providers/      #    Adapter de Saída: Mercado Pago
```

## 📋 Pré-requisitos

Docker e Docker Compose (recomendado)

Python 3.13+ (apenas para desenvolvimento local)

## 📊 SonarCloud - Qualidade de Código

O projeto está integrado com o **SonarCloud** para análise contínua de qualidade:

### Métricas Monitoradas

- **Cobertura de Código**: Mínimo de cobertura definido pelos testes
- **Code Smells**: Identificação de más práticas
- **Bugs**: Detecção de possíveis bugs
- **Vulnerabilidades**: Análise de segurança
- **Duplicação**: Código duplicado
- **Maintainability**: Índice de manutenibilidade

### Visualizar Resultados

Acesse o dashboard do SonarCloud em:
- https://sonarcloud.io/dashboard?id=WeesleyAlves_FIAP-SOAT-MICROSERVICE-ORDERS

<img width="1739" height="972" alt="image" src="https://github.com/user-attachments/assets/aef17c64-53d8-493a-a078-54846719c351" />



## 🚀 Como Rodar (Jeito Fácil: Docker)

Método recomendado para garantir que todas as dependências subam corretamente.

1️⃣ Clone o repositório
```bash
git clone git@github.com:DiegodeSalles/FIAP-SOAT-PAYMENT-MICROSERVICE.git
cd FIAP-SOAT-PAYMENT-MICROSERVICE
```

2️⃣ Configure as Variáveis de Ambiente

Renomeie o arquivo .env.example para .env (se existir) ou crie um .env na raiz do projeto:

```text
MONGODB_URL=mongodb://mongo:27017
MONGODB_DB_NAME=payment_db

MP_ACCESS_TOKEN=seu_token_de_teste_mercado_pago
MP_POS_ID=seu_pos_id_mercado_pago
MP_BASE_URL=https://api.mercadopago.com
ORDER_STATUS_URL=https://servico-de-pedidos.com
```

3️⃣ Suba a aplicação
```bash
docker-compose up -d --build
```

4️⃣ Acesse a documentação

Swagger UI: http://localhost:8000/docs

ReDoc: http://localhost:8000/redoc

## 🧪 Como Rodar os Testes

O projeto possui Testes Unitários e Testes de Comportamento (BDD).

▶️ Via Docker (recomendado)

```bash
docker-compose run --rm app pytest --cov=src
```

▶️ Localmente (com venv)
Criar e ativar o ambiente virtual
```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# Linux / Mac
source venv/bin/activate
```

Instalar dependências
```bash
pip install -r requirements.txt
```

### Executar os testes

```bash
pytest --cov=src
```

## 🔌 Integração (Contrato de API)

Para o time de Pedidos (Java) integrar com o serviço de pagamentos.

1️⃣ Criar Pagamento

Chame esta rota quando o cliente finalizar o pedido no Totem.

Endpoint

### `POST /api/v1/payments/`

```json
{
  "order_id": "uuid-do-pedido",
  "customer_id": "id-cliente",
  "amount": 100.50
}
```

Resposta

Retorna o qr_code_payload (Copia e Cola / Imagem) para exibição na tela.

2️⃣ Consultar Status (Polling)

Utilize o order_id para verificar se o pagamento foi aprovado.

Endpoint

### `GET /api/v1/payments/order/{order_id}`


Resposta
```json
{
  "id": "uuid-pagamento",
  "order_id": "uuid-do-pedido",
  "status": "approved",
  "amount": 100.50
}
```

Status possíveis:

pending

approved

rejected

3️⃣ Webhook (Mercado Pago)

Rota pública que recebe notificações do Mercado Pago.

Endpoint

### POST `/api/v1/webhook/`


Ação

Atualiza automaticamente o status do pagamento no banco de dados.

## 🛠️ Stack Tecnológica

| Tecnologia        | Função                                                      |
|-------------------|-------------------------------------------------------------|
| Python 3.13       | Linguagem principal                                         |
| FastAPI           | Framework Web assíncrono e de alta performance              |
| MongoDB           | Banco de dados NoSQL                                        |
| Motor             | Driver assíncrono para MongoDB                              |
| Mercado Pago SDK  | Integração externa de pagamentos                            |
| Pytest + BDD      | Testes automatizados e Gherkin                              |
| Docker            | Containerização e orquestração                              |
| GitHub Actions    | CI/CD (SonarCloud e AWS EKS)                                |

## 👤 Membros do projeto

- Diego de Salles — RM362702
- Lucas Felinto — RM363094
- Maickel Alves — RM361616
- Pedro Morgado — RM364209
- Wesley Alves — RM364342
