# Museo Atrium - Microservicio de Auditoría (Cassandra + Web UI)

> [!NOTE]
> This documentation is also available in [English (README.md)](README.md).

Microservicio satélite del ecosistema **Atrium** encargado de la auditoría inmutable (*append-only*), trazabilidad de estados de obras, bitácora de seguridad y agregación de reportes periódicos utilizando **Apache Cassandra / DataStax Astra DB** y **FastAPI**.

---

## Requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado y en ejecución.
- Python 3.10 o superior.
- Entorno virtual (venv).

---

## Estructura del Proyecto (Clean Architecture - 3 Capas)

```text
audit-python-cassandra/
├── app/
│   ├── domain/                  # Capa 1: Modelos puros, Interfaces (ABC), Excepciones y Servicios
│   │   ├── exceptions/          # Excepciones de dominio tipadas
│   │   ├── models/              # Entidades puras de negocio
│   │   ├── repositories/        # Contratos abstractos de repositorios
│   │   └── services/            # Lógica y orquestación de negocio
│   │
│   ├── persistence/             # Capa 2: Conexión Cassandra/Astra, Entidades, Mappers y Repositorios
│   │   ├── config/              # Gestión de conexión con fallback local/nube
│   │   ├── entities/            # Modelos físicos de tablas CQL
│   │   ├── mappers/             # Traductores bidireccionales Entity ⇄ Domain
│   │   └── repositories/        # Implementaciones con PreparedStatement y asyncio.to_thread
│   │
│   └── web/                     # Capa 3: Routers FastAPI, DTOs, Inyección de Dependencias y Error Handlers
│       ├── dependencies.py      # Proveedores de inyección con Depends()
│       ├── error_handlers.py    # Mapeo global de DomainException a códigos HTTP
│       ├── routers/             # Endpoints modulares (obras, seguridad, membresias, reportes, health)
│       └── schemas/             # DTOs Pydantic de Request y Response
│
├── docker/
│   └── docker-compose.yml       # Orquestación de contenedores (Cassandra + Web UI)
├── mocks/                       # Payloads de prueba y contratos de ejemplo
├── scripts/                     # Scripts CQL (01-05 estructura DDL y seed_* datos de prueba)
├── tests/                       # Pruebas automatizadas (pytest)
├── app_analytics.py             # Dashboard Analítico (Streamlit)
├── main.py                      # Ensamblador FastAPI (Lifespan, CORS, Routers)
├── .env.example                 # Variables de entorno documentadas
├── pytest.ini                   # Configuración para pruebas
├── requirements.txt             # Dependencias de Python (UTF-8)
├── README.md                    # Documentación principal en inglés
└── README.es.md                 # Documentación en español
```

---

## Paso 1: Iniciar los contenedores

Desde la raíz del proyecto, ejecuta:

```powershell
docker compose -f docker/docker-compose.yml up -d
```

Esto levantará tres contenedores:

| Contenedor | Imagen | Puerto | Función |
|---|---|---|---|
| `museo-cassandra-nodo` | `cassandra:4.0` | `9042` | Base de datos Cassandra NoSQL |
| `museo-cassandra-init` | `cassandra:4.0` | - | Inicializa esquemas y datos semilla automáticamente |
| `museo-cassandra-web` | `delermando/docker-cassandra-web:v0.4.0` | `3000` | Interfaz web de administración |

---

## Paso 2: Verificar el estado de los contenedores

```powershell
docker ps -a
```

Debes observar:
- `museo-cassandra-nodo`: Estado `Up (healthy)`.
- `museo-cassandra-init`: Estado `Exited (0)` (indica que el keyspace y las tablas se crearon correctamente).
- `museo-cassandra-web`: Estado `Up`.

---

## Paso 3: Acceder a CassandraDB Web

Abre tu navegador en:

```
http://localhost:3000
```

Credenciales preconfiguradas:
* **Host:** `172.20.0.10`
* **Port:** `9042`
* **Username:** `cassandra`
* **Password:** `cassandra`

---

## Paso 4: Ejecutar el API Python

1. **Crear y activar el entorno virtual:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

2. **Configurar variables de entorno:**
   ```powershell
   Copy-Item .env.example .env
   ```
   *Por defecto, `.env` está preconfigurado para conectarse al contenedor de Cassandra local (`127.0.0.1:9042`). Si prefieres usar DataStax Astra DB en la nube, configura las rutas a tus credenciales dentro de `.env`.*

3. **Instalar dependencias:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Iniciar el servidor:**
   ```powershell
   uvicorn main:app --port 8080 --reload
   ```

Accede a la documentación OpenAPI interactiva en:
* Swagger UI: `http://127.0.0.1:8080/docs`
* ReDoc: `http://127.0.0.1:8080/redoc`
* Health Check: `http://127.0.0.1:8080/health`

---

## Paso 5: Dashboard Analítico (Streamlit)

Para iniciar la interfaz gráfica interactiva de visualización de activos y auditoría:

```powershell
streamlit run app_analytics.py
```

---

## Paso 6: Ejecutar Pruebas Automatizadas

El proyecto incluye pruebas de integración y contratos web usando inyección de dependencias (`app.dependency_overrides`):

```powershell
pytest -v
```

---

## Comandos Útiles

```powershell
# Iniciar todos los contenedores
docker compose -f docker/docker-compose.yml up -d

# Ver logs de inicialización del esquema CQL
docker logs museo-cassandra-init

# Detener los contenedores (conservando datos)
docker compose -f docker/docker-compose.yml down

# Detener y reiniciar eliminando volúmenes de datos
docker compose -f docker/docker-compose.yml down -v

# Conectarse a cqlsh interactivo dentro del contenedor
docker exec -it museo-cassandra-nodo cqlsh
```

---

## Solución de Problemas

* **El contenedor Cassandra no se pone healthy:** Espera unos segundos adicionales; Cassandra puede tardar hasta 60 segundos en arrancar por completo.
* **Error "unsupported release version" en la Web UI:** Asegúrate de usar la imagen `cassandra:4.0` fijada en `docker-compose.yml`.
* **Error "invalid address" en Cassandra Web:** La interfaz web requiere una IP estática; `docker-compose.yml` ya la preasigna en `172.20.0.10`.
