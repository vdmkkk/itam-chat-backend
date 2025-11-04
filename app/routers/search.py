from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import PaginationParams
from app.db.session import get_db
from app.models.user import User
from app.schemas.common import Page
from app.schemas.user import UserSearchPublic
from app.deps import get_current_user


router = APIRouter(prefix="", tags=["Search"])


@router.get(
    "/search",
    response_model=Page[UserSearchPublic],
    summary="Search users",
    description=(
        "Fast user search across username, first_name, and last_name. "
        "Matches are case-insensitive and prioritize exact/prefix username matches."
    ),
)
async def search_users(
    q: Annotated[str, Query(min_length=1, max_length=100, description="Query string")],
    pagination: Annotated[PaginationParams, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Page[UserSearchPublic]:
    query = q.strip()
    like = f"{query}%"

    where_clause = or_(
        func.lower(User.username).like(func.lower(like)),
        func.lower(User.first_name).like(func.lower(like)),
        func.lower(User.last_name).like(func.lower(like)),
    )

    # Exclude self
    base = select(User).where(where_clause, User.id != current_user.id)

    # Prioritize: exact username match > prefix username match > others
    ordering = (
        func.case((func.lower(User.username) == func.lower(query), 0), else_=1),
        func.case((func.lower(User.username).like(func.lower(like)), 0), else_=1),
        func.lower(User.username),
        func.lower(User.first_name),
        func.lower(User.last_name),
    )

    total_res = await db.execute(select(func.count()).select_from(base.subquery()))
    total = int(total_res.scalar() or 0)

    res = await db.execute(
        base.order_by(*ordering).offset(pagination.offset).limit(pagination.limit)
    )
    items = [UserSearchPublic.model_validate(u) for u in res.scalars().all()]
    return Page[UserSearchPublic](items=items, total=total, limit=pagination.limit, offset=pagination.offset)


