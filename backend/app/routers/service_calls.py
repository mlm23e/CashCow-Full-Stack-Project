from fastapi import APIRouter, Depends, Query, HTTPException, status, Response

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.service_call import (
    ATMReliabilityRead,
    DiscrepancyRead,
    ServiceCreate,
    ServicePriority,
    ServiceRead,
    ServiceUpdate,
    ServiceStatusUpdate,
)
from app.schemas.atm import ATMRead
from app.models import ATM, UserRole, User, ServiceCall, ServicePriority, ServiceStatus

from app.dependencies import get_db, require_role, get_current_user

router = APIRouter(prefix="/service_calls", tags=["service_calls"])


"""
Creates a ServiceCall object
"""
@router.post("", response_model=ServiceRead, status_code=status.HTTP_201_CREATED)
async def post_service_call(
    payload: ServiceCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.OPERATIONS_ADMIN, UserRole.FIELD_TECHNICIAN))
)->ServiceCall:
    atm = await db.get(ATM, payload.atm_id)
    if atm is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = (f"ATM '{payload.atm_id}' not found")
        )

    if payload.technician_id is not None:
        user = await db.get(User, payload.technician_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(f"User '{payload.technician_id}' not found")
            )

    service = ServiceCall(**payload.model_dump())
    db.add(service)
    await db.commit()
    await db.refresh(service)
    return service

"""
Reads ALL ServiceCalls
"""
@router.get("", response_model=list[ServiceRead])
async def list_service_calls(
    db : AsyncSession = Depends(get_db),
    _ : User = Depends(get_current_user)
)->list[ServiceCall]:
    statement = select(ServiceCall).order_by(ServiceCall.id)
    result = await db.execute(statement)
    return list(result.scalars().all())

"""
Determines the service call completion/failure broken down by ATM model
(answers business question #3)
"""
@router.get("/reliability", response_model=list[ATMReliabilityRead])
async def atm_reliability_metric(
    db : AsyncSession = Depends(get_db),
    _ : User = Depends(get_current_user)
) -> list[ATMReliabilityRead]:
    statement = (
        select(
            ATM.model.label("model"),
            func.count(ServiceCall.id).label("total_calls"),
            func.sum(
                case((ServiceCall.status == ServiceStatus.COMPLETED, 1), else_=0)
            ).label("completed_calls"),
            func.sum(
                case((ServiceCall.status == ServiceStatus.FAILED, 1), else_=0)
            ).label("failed_calls"),
        )
        .join(ServiceCall, ServiceCall.atm_id == ATM.id)
        .group_by(ATM.model)
        .order_by(ATM.model)
    )

    result = await db.execute(statement)
    metrics = []

    for row in result.mappings().all():
        completed_calls = int(row["completed_calls"] or 0)
        failed_calls = int(row["failed_calls"] or 0)
        resolved_calls = completed_calls + failed_calls
        completion_rate = (
            completed_calls / resolved_calls * 100 if resolved_calls else 0
        )
        failure_rate = (
            failed_calls / resolved_calls * 100 if resolved_calls else 0
        )

        metrics.append(
            ATMReliabilityRead(
                model=row["model"],
                total_calls=int(row["total_calls"]),
                completed_calls=completed_calls,
                failed_calls=failed_calls,
                completion_rate=completion_rate,
                failure_rate=failure_rate,
            )
        )

    return metrics

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
            ServiceCall.id.label("service_id"), 
            ServiceCall.title, 
            ATM.branch_id.label("atm_branch_id"), 
            User.branch_id.label("technician_branch_id")
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
Reads ServiceCall by its ID
"""
@router.get("/{service_id}", response_model=ServiceRead)
async def get_service_call_by_id(
    service_id : int,
    db : AsyncSession = Depends(get_db),
    _ : User = Depends(get_current_user)
) -> ServiceCall:
    service_call = await db.get(ServiceCall, service_id)
    if service_call is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(f"ServiceCall '{service_id}' not found")
        )
    return service_call


"""
Updates a ServiceCall
"""
@router.patch("/{service_id}", response_model=ServiceRead)
async def update_service(
    service_id : int,
    payload : ServiceUpdate, 
    db : AsyncSession = Depends(get_db),
    _ : User = Depends(require_role(UserRole.OPERATIONS_ADMIN))
) -> ServiceCall:
    service_call = await db.get(ServiceCall, service_id)

    if service_call is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(f"ServiceCall '{service_id}' not found")
        )
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(service_call, field, value)

    await db.commit()
    await db.refresh(service_call)
    return service_call


"""
Updates the ServiceCall status
"""
@router.patch("/{service_id}/status", response_model= ServiceRead)
async def update_service_status(
    service_id : int,
    payload : ServiceStatusUpdate,
    db : AsyncSession = Depends(get_db),
    _ : User = Depends(require_role(UserRole.OPERATIONS_ADMIN, UserRole.FIELD_TECHNICIAN))
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
Deletes a ServiceCall
"""
@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service_call(
    service_id : int,
    db : AsyncSession = Depends(get_db),
    _ : UserRole = Depends(require_role)
)-> Response:
    service = await db.get(ServiceCall, service_id)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(f"Service Call '{service_id}' not found")
        )
    await db.delete(service)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)