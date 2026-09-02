from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_user, require_role
from app.models.enums import ATMStatus, UserRole
from app.models.user import User
from app.models.atm import ATM
from app.schemas.atm import ATMCreate, ATMRead, ATMUpdate


# Every request comes under /atms and has to do with ATMs
router = APIRouter(prefix="/atms", tags=["atms"])

# This decorator says this goes to "/atms" with nothing else and returns a list of ATMRead objects
@router.get("", response_model = list[ATMRead])
async def list_atms(
    max_cash : Decimal | None = Query(
        # this is a query parameter used for filtering all of our results
        default = None, # this makes it optional
        ge=0,
        le=100,
        description="Only returns ATMs strictly below this cash level"
    ),
    db: AsyncSession = Depends(get_db),
    # day 5 addition here
    _ : User = Depends(get_current_user)
) -> list[ATM]:
    

    # We need to be able to interact with the DB, so we need our session object to execute those statement
    # We are DEPENDENT on the session object

    # Includes optional query paramter for filtering base on cash level (business question #3)

    # Create our statement for the DB
    statement = select(ATM).where(ATM.status != ATMStatus.OFFLINE)

    # check for max_cash query paramter
    if max_cash is not None:
        statement = statement.where(ATM.cash_level < max_cash)
    statement = statement.order_by(ATM.id)

    result = await db.execute(statement)

    return list(result.scalars().all())

# Get a specific ATM by its id
# GET /atms/{atm_id} -> atm_id is known as a PATH PARAMETER
@router.get("/{atm_id}", response_model=ATMRead)
async def get_atm(
    atm_id : int, 
    db : AsyncSession = Depends(get_db), 
    _ : User = Depends(get_current_user)
) -> ATM:
    atm = await db.get(ATM, atm_id)

    if atm is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail= f"ATM '{atm_id}' not found"
        )
    return atm

@router.post("", response_model=ATMRead, status_code=status.HTTP_201_CREATED)
async def post_atm(
    payload: ATMCreate, 
    db : AsyncSession = Depends(get_db), 
    _ : User = Depends(require_role(UserRole.OPERATIONS_ADMIN))
) -> ATM:
    # we received the payload as a ATMCreate object
    # we need it as a ATM object to save with the ORM
    atm = ATM(**payload.model_dump) # this dumps the model into the ATM constructor
    # the double-star (**) unpackages the model
    db.add(atm)
    await db.commit()
    await db.refresh(atm)
    return atm

@router.patch("/{atm_id}", response_model=ATMRead)
async def update_atm(
    atm_id: int,
    payload: ATMUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.OPERATIONS_ADMIN))
) -> ATM:
    atm = await db.get(ATM, atm_id)

    if atm is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"ATM '{atm_id}' not found"
        )
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(atm, field, value)

    await db.commit()
    await db.refresh(atm)
    return atm

@router.delete("/{atm_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_atm(
    atm_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.OPERATIONS_ADMIN))
) -> Response:
    atm = await db.get(ATM, atm_id)

    if atm is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ATM '{atm_id}' not found"
        )

    await db.delete(atm)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)