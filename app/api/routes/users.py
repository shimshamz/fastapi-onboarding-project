from typing import Annotated, Any
from fastapi import APIRouter, Depends, HTTPException, Query

from app import crud
from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from app.core.security import get_password_hash, verify_password
from app.models import UpdatePassword, User, UserCreate, UserPublic, UsersPublic
from sqlmodel import func, select

router = APIRouter(tags=["users"])

@router.get("/users", dependencies=[Depends(get_current_active_superuser)], response_model=UsersPublic)
async def read_users(session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100) -> Any:
    """
    Retrieve users.
    """

    count_statement = select(func.count()).select_from(User)
    count = session.exec(count_statement).one()

    statement = select(User).offset(offset).limit(limit)
    users = session.exec(statement).all()

    return UsersPublic(data=users, count=count)

@router.post("/users", dependencies=[Depends(get_current_active_superuser)], response_model=UserPublic)
async def create_user(*, session: SessionDep, user_in: UserCreate) -> Any:
    """
    Create new user.
    """

    # Check if the email already exists
    user = crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )

    db_user = User.model_validate(
        user_in, update={"hashed_password": get_password_hash(user_in.password)}
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@router.get("/me", response_model=UserPublic)
async def read_user_me(current_user: CurrentUser) -> Any:
    """
    Get current user.
    """
    return current_user

@router.patch("/me/password")
async def update_password_me(*, session: SessionDep, body: UpdatePassword, current_user: CurrentUser) -> Any:
    """
    Update own password.
    """
    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    if body.current_password == body.new_password:
        raise HTTPException(
            status_code=400, detail="New password cannot be the same as the current one"
        )
    hashed_password = get_password_hash(body.new_password)
    current_user.hashed_password = hashed_password
    session.add(current_user)
    session.commit()
    return {"message":"Password updated successfully"}