"""
When you ran uv init, it likely initialized a packaged Python project using the src layout.
- src/ contains the importable Python package.
- fastapi_learning/ is your project's Python package.
- __init__.py marks that directory as a regular Python package and can contain package initialization code.


__init__.py is a special Python file traditionally used to mark a directory as a Python package. It can also execute initialization code when the package is imported.
"""

"""
In your FastAPI backend, Pydantic and SQLAlchemy Async solve two different problems.
- Pydantic validates data and defines the structure of API requests and responses.
- SQLAlchemy Async communicates with your database asynchronously, allowing your application to execute database operations without blocking the event loop while waiting for I/O.


"""


"""
Package	Purpose
sqlalchemy[asyncio]	ORM, async database engine, sessions, queries and transactions
asyncpg	Async PostgreSQL driver used by SQLAlchemy
alembic	Version-controlled database schema migrations
pydantic-settings	Loads and validates configuration such as DATABASE_URL
fastapi[standard]	FastAPI framework and its standard development tools
ruff	Linting and code formatting


"""
