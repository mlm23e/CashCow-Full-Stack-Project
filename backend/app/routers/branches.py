from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.branch import Branch
from app.models.enums import UserRole
from app.models.user import User
from app.dependencies import get_db, get_current_user, require_role
from app.schemas.branch import BranchRead, BranchCreate, BranchUpdate

router = APIRouter(prefix="/branches", tags=["branches"])

@router.get("", response_model=list[BranchRead])
async def list_branches(
    db : AsyncSession = Depends(get_db),
    _ : User = Depends(get_current_user)
)->list[Branch]:
    statement = select(Branch).order_by(Branch.id)
    result = await db.execute(statement)
    return list(result.scalars().all())

@router.post("", response_model=BranchRead, status_code=status.HTTP_201_CREATED)
async def post_branch(
    payload : BranchCreate,
    db : AsyncSession = Depends(get_db),
    _ : User = Depends(require_role(UserRole.OPERATIONS_ADMIN))
)->Branch:
    if payload.supervisor_id is not None:
        supervisor = await db.get(User, payload.supervisor_id)
        if supervisor is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(f"User '{payload.supervisor_id}' not found")
            )

    branch = Branch(**payload.model_dump())
    db.add(branch)
    await db.commit()
    await db.refresh(branch)
    return branch

@router.get("/{branch_id}", response_model=BranchRead)
async def get_branch_by_id(
    branch_id : int,
    db : AsyncSession = Depends(get_db),
    _ : User = Depends(get_current_user)
) -> Branch:
    branch = await db.get(Branch, branch_id)
    if branch is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(f"Branch '{branch_id}' not found")
        )
    return branch

@router.patch("/{branch_id}", response_model=BranchRead)
async def update_branch(
    branch_id : int,
    payload : BranchUpdate,
    db : AsyncSession = Depends(get_db),
    _ : User = Depends(require_role(UserRole.OPERATIONS_ADMIN))
)->Branch:
    branch = await db.get(Branch, branch_id)
    if branch is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(f"Branch '{branch_id}' not found")
        )
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(branch, field, value)
    await db.commit()
    await db.refresh(branch)
    return branch

@router.delete("/{branch_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_branch(
    branch_id : int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.OPERATIONS_ADMIN))
)->Response:
    branch = await db.get(Branch, branch_id)
    if branch is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(f"Branch '{branch_id}' not found")
        )
    await db.delete(branch)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
