from fastapi import APIRouter, Depends, HTTPException, Response, status

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db, require_role
from app.models import User, UserRole, Branch
from app.schemas.user import UserRead, UserUpdate, UserCreate
from app.security import hash_password

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserRead])
async def list_users(
	db: AsyncSession = Depends(get_db),
	_: User = Depends(require_role(UserRole.OPERATIONS_ADMIN))
) -> list[User]:
	result = await db.execute(select(User).order_by(User.id))
	return list(result.scalars().all())

@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def post_user(
	payload : UserCreate,
	db : AsyncSession = Depends(get_db),
	_ : User = Depends(require_role(UserRole.OPERATIONS_ADMIN))
)->User:
	username = payload.username.strip().lower()
	existing = await db.execute(
		select(User).where(func.lower(User.username) == username)
	)
	if existing.scalar_one_or_none() is not None:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=f"Username '{payload.username}' is already taken"
		)

	if payload.branch_id is not None and await db.get(Branch, payload.branch_id) is None:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=f"Branch '{payload.branch_id}' not found"
		)

	user = User(
		username=username,
		first_name=payload.first_name,
		last_name=payload.last_name,
		role=payload.role,
		branch_id=payload.branch_id,
		hashed_password=hash_password(payload.password)
	)
	db.add(user)
	await db.commit()
	await db.refresh(user)
	return user


@router.get("/{user_id}", response_model=UserRead)
async def get_user_by_id(
	user_id: int,
	db: AsyncSession = Depends(get_db),
	_: User = Depends(get_current_user)
) -> User:
	user = await db.get(User, user_id)
	if user is None:
		raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")
	return user


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
	user_id: int,
	payload: UserUpdate,
	db: AsyncSession = Depends(get_db),
	_: User = Depends(require_role(UserRole.OPERATIONS_ADMIN))
) -> User:
	user = await db.get(User, user_id)
	if user is None:
		raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")

	updates = payload.model_dump(exclude_unset=True)
	if "username" in updates:
		updates["username"] = updates["username"].strip().lower()
	if "password" in updates:
		updates["hashed_password"] = hash_password(updates.pop("password"))

	if "username" in updates:
		existing = await db.execute(
			select(User).where(
				func.lower(User.username) == updates["username"],
				User.id != user_id
			)
		)
		if existing.scalar_one_or_none() is not None:
			raise HTTPException(status_code=400, detail="Username is already taken")

	for field, value in updates.items():
		setattr(user, field, value)

	await db.commit()
	await db.refresh(user)
	return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
	user_id: int,
	db: AsyncSession = Depends(get_db),
	_: User = Depends(require_role(UserRole.OPERATIONS_ADMIN))
) -> Response:
	user = await db.get(User, user_id)
	if user is None:
		raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")

	await db.delete(user)
	await db.commit()
	return Response(status_code=status.HTTP_204_NO_CONTENT)
