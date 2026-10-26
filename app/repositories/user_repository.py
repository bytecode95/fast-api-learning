# The repository is responsible for database queries and persistence—not HTTP status codes or business rules.
# the repository is the layer that communicates with PostgreSQL through SQLAlchemy.
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return await self.session.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def list_users(
        self,
        *,
        limit: int,
        offset: int,
        search: str | None = None,
        is_active: bool | None = None,
    ) -> tuple[list[User], int]:
        statement = select(User)
        count_statement = select(func.count()).select_from(User)

        if search:
            pattern = f"%{search}%"
            filters = User.name.ilike(pattern) | User.email.ilike(pattern)
            statement = statement.where(filters)
            count_statement = count_statement.where(filters)

        if is_active is not None:
            statement = statement.where(User.is_active == is_active)
            count_statement = count_statement.where(User.is_active == is_active)

        total_result = await self.session.execute(count_statement)
        total = total_result.scalar_one()

        # ID provides deterministic ordering for a given database state.
        statement = statement.order_by(User.id.asc()).offset(offset).limit(limit)

        result = await self.session.execute(statement)
        return list(result.scalars().all()), total

    async def create(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def delete(self, user: User) -> None:
        await self.session.delete(user)
