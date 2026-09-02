from fastapi import APIRouter, Depends, Query, HTTPException, status

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.service_call import DiscrepancyRead, ServicePriority, ServiceRead, ServiceStatusUpdate
from app.schemas.atm import ATMRead
from app.models import ATM, UserRole, User, ServiceCall, ServicePriority, ServiceStatus

from app.dependencies import get_db, require_role, get_current_user

router = APIRouter(prefix="/service_calls", tags=["service_calls"])


"""
Finds co-location discrepancies between the ATM and User branch IDs, 
with the option to return only the discrepancies found for service 
calls of a certain priority
(answers business question #2)
"""
@router.get("/discrepancies", response_model=list[DiscrepancyRead])
async def list_colocation_discrepancies(
    priority: ServicePriority | None = Query(
        default=None,
        description="Only return discrepancies for service calls of this priority"
    ),
    db : AsyncSession = Depends(get_db),
    _ : User = Depends(require_role(UserRole.OPERATIONS_ADMIN))
):
    # Answers business question #2 (find colocation discrepancies between ATM and Technician facility_id)
    statement = (
        select(
            ServiceCall.id.label("service_call_id"), 
            ServiceCall.title, 
            ATM.branch_id.label("atm_branch_id"), 
            User.branch_id.label("service_branch_id")
        )
        .join(ATM, ATM.id == ServiceCall.atm_id)
        .join(User, User.id == ServiceCall.technician_id)
        .where(ATM.branch_id != User.branch_id)
    )

    if priority is not None:
        statement = statement.where(ServiceCall.priority == priority)

    statement = statement.order_by(ServiceCall.id)

    result = await db.execute(statement)
    return [dict(row) for row in result.mappings().all()]


"""
Updates the ServiceCall status
"""
@router.patch("/{service_id}/status", response_model= ServiceRead)
async def update_status(
    service_id : int,
    payload : ServiceStatusUpdate,
    db : AsyncSession = Depends(get_db),
    _ : User = Depends(require_role(UserRole.OPERATIONS_ADMIN, UserRole.TECHNICIAN))
) -> ServiceCall:
    
    service = await db.get(ServiceCall, service_id)

    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(f"Service Call '{service_id}' not found")
        )

    if service.status.value != payload.status.value:
        service.status = payload.status

    await db.commit()
    await db.refresh(service)

    return service


"""
Determines the service call completion/failure broken down by ATM model
(answers business question #3)
"""
@router.get("", response_model=list[ATMRead])
async def atm_reliability_metric(
    db : AsyncSession = Depends(get_db),
    current_user : User = Depends(get_current_user)
):