import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate


class UserNotFoundError(Exception):
    pass


class DuplicateEmailError(Exception):
    pass


class InvalidUserUpdateError(Exception):
    pass


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = UserRepository(session)

    async def create_user(self, data: UserCreate) -> User:
        # Normalize email consistently for this example.
        email = str(data.email).strip().lower()

        existing = await self.repository.get_by_email(email)
        if existing:
            raise DuplicateEmailError

        user = User(name=data.name.strip(), email=email)

        try:
            await self.repository.create(user)
            await self.session.commit()
            await self.session.refresh(user)
            return user
        except IntegrityError as exc:
            await self.session.rollback()

            # The database constraint also protects against concurrent
            # requests creating the same email.
            if "uq_users_email" in str(exc.orig) or "users.email" in str(exc.orig):
                raise DuplicateEmailError from exc
            raise

    async def get_user(self, user_id: uuid.UUID) -> User:
        user = await self.repository.get_by_id(user_id)

        if user is None:
            raise UserNotFoundError

        return user

    async def list_users(
        self,
        *,
        limit: int,
        offset: int,
        search: str | None = None,
        is_active: bool | None = None,
    ) -> tuple[list[User], int]:
        return await self.repository.list_users(
            limit=limit,
            offset=offset,
            search=search,
            is_active=is_active,
        )

    async def update_user(
        self,
        user_id: uuid.UUID,
        data: UserUpdate,
    ) -> User:
        user = await self.get_user(user_id)
        changes = data.model_dump(exclude_unset=True)

        if not changes:
            raise InvalidUserUpdateError

        # A PATCH can omit a field, but must not clear required columns.
        if "name" in changes:
            if changes["name"] is None or not changes["name"].strip():
                raise InvalidUserUpdateError
            changes["name"] = changes["name"].strip()

        if "email" in changes:
            if changes["email"] is None:
                raise InvalidUserUpdateError
            changes["email"] = str(changes["email"]).strip().lower()

        if "email" in changes:
            existing = await self.repository.get_by_email(changes["email"])
            if existing is not None and existing.id != user.id:
                raise DuplicateEmailError

        for field, value in changes.items():
            setattr(user, field, value)

        try:
            await self.session.flush()
            await self.session.commit()
            await self.session.refresh(user)
            return user
        except IntegrityError as exc:
            await self.session.rollback()
            if "uq_users_email" in str(exc.orig) or "users.email" in str(exc.orig):
                raise DuplicateEmailError from exc
            raise

    async def delete_user(self, user_id: uuid.UUID) -> None:
        user = await self.get_user(user_id)

        try:
            await self.repository.delete(user)
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise
