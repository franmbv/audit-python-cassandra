# Atrium Museum - Audit Microservice (Cassandra + FastAPI + Web UI)

> [!NOTE]
> Esta documentación también está disponible en [Español (README.es.md)](README.es.md).

Satellite microservice for the **Atrium Core Ecosystem**, responsible for immutable append-only auditing, artwork status tracking, security access logging, and periodic financial/membership reporting using **Apache Cassandra / DataStax Astra DB** and **FastAPI**.

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.
- Python 3.10 or higher.
- Python virtual environment tool (venv).

---

## Project Structure (Clean Architecture - 3 Layers)

```text
audit-python-cassandra/
├── app/
│   ├── domain/                  # Layer 1: Pure Domain Models, ABC Interfaces, Exceptions & Services
│   │   ├── exceptions/          # Strongly-typed domain exceptions
│   │   ├── models/              # Pure business entities
│   │   ├── repositories/        # Abstract repository contracts
│   │   └── services/            # Business orchestration and logic
│   │
│   ├── persistence/             # Layer 2: Cassandra/Astra Connection, Entities, Mappers & Repositories
│   │   ├── config/              # Dynamic DB manager with local/cloud fallback
│   │   ├── entities/            # Physical CQL table schemas
│   │   ├── mappers/             # Bi-directional translators (Entity ⇄ Domain)
│   │   └── repositories/        # Implementations using PreparedStatements & asyncio.to_thread
│   │
│   └── web/                     # Layer 3: FastAPI Routers, DTOs, Dependency Injection & Error Handlers
│       ├── dependencies.py      # Dependency injection providers using Depends()
│       ├── error_handlers.py    # Global mapping from DomainException to HTTP status codes
│       ├── routers/             # Modular endpoints (artworks, security, memberships, reports, health)
│       └── schemas/             # Pydantic Request & Response DTOs
│
├── docker/
│   └── docker-compose.yml       # Container orchestration (Cassandra 4.0 + Web UI)
├── mocks/                       # Sample request payloads and integration contracts
├── scripts/                     # CQL Scripts (01-05 DDL schemas & seed_* initial datasets)
├── tests/                       # Automated test suite (pytest)
├── app_analytics.py             # Streamlit Analytics Dashboard
├── main.py                      # FastAPI Application Assembler (Lifespan, CORS, Routers)
├── .env.example                 # Documented environment variables
├── pytest.ini                   # Pytest configuration (pythonpath = .)
├── requirements.txt             # Clean UTF-8 dependencies
├── README.md                    # Main documentation in English
└── README.es.md                 # Spanish documentation
```

---

## Step 1: Start the Containers

From the root directory of the project, run:

```powershell
docker compose -f docker/docker-compose.yml up -d
```

This will launch three containers:

| Container | Image | Port | Role |
|---|---|---|---|
| `museo-cassandra-nodo` | `cassandra:4.0` | `9042` | Apache Cassandra NoSQL database |
| `museo-cassandra-init` | `cassandra:4.0` | - | Automatically runs CQL schema creation and seed scripts |
| `museo-cassandra-web` | `delermando/docker-cassandra-web:v0.4.0` | `3000` | Web administration UI |

---

## Step 2: Verify Container Health

Check that all containers started properly:

```powershell
docker ps -a
```

Expected status:
- `museo-cassandra-nodo`: `Up (healthy)`.
- `museo-cassandra-init`: `Exited (0)` (signifies successful schema and seed migration).
- `museo-cassandra-web`: `Up`.

---

## Step 3: Access CassandraDB Web UI

Open your browser at:

```
http://localhost:3000
```

Pre-configured credentials:
* **Host:** `172.20.0.10`
* **Port:** `9042`
* **Username:** `cassandra`
* **Password:** `cassandra`

---

## Step 4: Run the Python API

1. **Create and activate the virtual environment:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

2. **Configure environment variables:**
   ```powershell
   Copy-Item .env.example .env
   ```
   *By default, `.env` is configured to connect to the local Docker Cassandra node (`127.0.0.1:9042`). If you wish to connect to DataStax Astra DB in the cloud, specify your credentials in `.env`.*

3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Start the API server:**
   ```powershell
   uvicorn main:app --port 8080 --reload
   ```

Interactive API documentation will be available at:
* Swagger UI: `http://127.0.0.1:8080/docs`
* ReDoc: `http://127.0.0.1:8080/redoc`
* Health Check: `http://127.0.0.1:8080/health`

---

## Step 5: Analytics Dashboard (Streamlit)

To launch the interactive visual dashboard for art asset intelligence and security auditing:

```powershell
streamlit run app_analytics.py
```

---

## Step 6: Run Automated Tests

Run the test suite using `pytest` (configured with `app.dependency_overrides`):

```powershell
pytest -v
```

---

## Useful Commands

```powershell
# Start all containers in background
docker compose -f docker/docker-compose.yml up -d

# Check schema initialization logs
docker logs museo-cassandra-init

# Stop all containers (preserving data volume)
docker compose -f docker/docker-compose.yml down

# Stop all containers and wipe data volumes
docker compose -f docker/docker-compose.yml down -v

# Connect to Cassandra via cqlsh interactive shell
docker exec -it museo-cassandra-nodo cqlsh
```

---

## Troubleshooting

* **Cassandra container is not becoming healthy:** Wait a few moments; Cassandra can take up to 60 seconds to fully initialize its ring.
* **Error "unsupported release version" in Web UI:** Ensure you are using `cassandra:4.0` as specified in `docker-compose.yml`.
* **Error "invalid address" in Web UI:** The web UI requires a static IP address, which is already assigned (`172.20.0.10`) via the Docker custom bridge network.
