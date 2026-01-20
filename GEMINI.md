# Gemini Project Context: Multi-Tenant FastAPI Profile Service

## Project Overview

This is a Python-based backend service built with the **FastAPI** framework. It implements a **multi-tenant architecture** to manage user profiles and documents. The core design separates data into two distinct database types:

1.  **Shared Database**: A central database (likely PostgreSQL in production, as suggested by `asyncpg`) that stores common information, such as tenant metadata. All tables in this database inherit from `SharedBase`.
2.  **Tenant Databases**: Individual **SQLite** databases for each tenant, providing data isolation. These databases store tenant-specific information like profiles and documents.

The application is containerized using **Docker** and `docker-compose`, and uses `uv` for Python package management.

## Key Technologies

-   **Backend Framework**: FastAPI
-   **Database**: SQLAlchemy (for ORM), PostgreSQL (implied for shared DB), SQLite (for tenant DBs)
-   **Database Migrations**: Alembic, with separate migration paths for shared and tenant databases.
-   **Dependency Management**: `uv`
-   **Containerization**: Docker, Docker Compose
-   **Linting**: Ruff
-   **Testing**: Pytest

## Building and Running

The project is designed to run inside a Docker container.

### Local Development (with Docker Compose)

1.  **Build and Run the service**:
    ```bash
    # This command will build the Docker image and start the service.
    # The service will be available at http://localhost:8000
    docker-compose up --build
    ```

2.  **Install dependencies locally (optional, for IDE support)**:
    If you want your local editor to have access to the dependencies, run:
    ```bash
    uv sync --dev
    ```

### Running Commands Inside the Container

To run commands like database migrations, you can `exec` into the running container:

```bash
# Find the container ID
docker ps

# Exec into the container
docker exec -it <container_id> bash

# Now you can run the commands specified in the README
# For example, to apply shared database migrations:
# PYTHONPATH=. uv run alembic -c alembic.ini -n shared upgrade head
```

## Database Management

The project uses **Alembic** to manage database schema migrations. There are two separate migration configurations: `shared` and `tenant`.

-   **Shared Migrations**: Apply to the central, shared database.
    -   Configuration is in `alembic.ini` under `[shared]`.
    -   Migration scripts are in `migrations/shared/versions/`.
-   **Tenant Migrations**: Apply to all individual tenant databases.
    -   Configuration is in `alembic.ini` under `[tenant]`.
    -   Migration scripts are in `migrations/tenant/versions/`.

### Common Migration Commands

*(These should be run inside the container or in a local environment where dependencies are installed.)*

-   **Apply shared migrations**:
    ```bash
    PYTHONPATH=. uv run alembic -c alembic.ini -n shared upgrade head
    ```
-   **Generate a new tenant migration**:
    ```bash
    PYTHONPATH=. uv run alembic -c alembic.ini -n tenant -x tenant_id=<some_tenant_id> revision --autogenerate -m "description"
    ```
-   **Apply migrations for ALL tenants**:
    ```bash
    PYTHONPATH=. uv run alembic -c alembic.ini -n tenant upgrade head
    ```

-   **Initialize with sample data**:
    ```bash
    uv run python scripts/init_dev_data.py
    ```

## Development Conventions

-   **Code Style**: The project uses **Ruff** for linting and formatting. Ensure code is compliant before committing.
-   **Testing**: Tests are written using **Pytest**. The configuration is in `pytest.ini`. Tests are located in the `tests/` directory. Run tests with `pytest`.
-   **API Structure**: The API is versioned under `app/api/v1/`. Endpoints are separated by resource (e.g., `profiles.py`, `documents.py`).
-   **Multi-tenancy**: Tenant is identified via path parameters or headers in API requests. The `db_manager` handles routing connections to the correct tenant database.
