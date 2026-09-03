from fastapi import APIRouter, Depends, HTTPException, Response, status

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.diagnostic_report import (
    DiagnosticReportCreate,
    DiagnosticReportRead,
    DiagnosticReportUpdate,
)
from app.models.diagnostic_report import DiagnosticReport
from app.models.user import User
from app.models.enums import UserRole
from app.models.service_call import ServiceCall
from app.dependencies import get_db, get_current_user, require_role

router = APIRouter(prefix="/diagnostic_reports", tags=["diagnostic_reports"])

@router.get("", response_model=list[DiagnosticReportRead])
async def list_diagnostic_reports(
    db : AsyncSession = Depends(get_db),
    _ : User = Depends(get_current_user)
)->list[DiagnosticReport]:
    results = await db.execute(select(DiagnosticReport).order_by(DiagnosticReport.id))
    return list(results.scalars().all())

@router.post("", response_model=DiagnosticReportRead, status_code=status.HTTP_201_CREATED)
async def post_diagnostic_report(
    payload : DiagnosticReportCreate,
    db : AsyncSession = Depends(get_db),
    _ : User = Depends(require_role(UserRole.OPERATIONS_ADMIN, UserRole.FIELD_TECHNICIAN))
)->DiagnosticReport:
    service_call = await db.get(ServiceCall, payload.service_call_id)
    if service_call is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(f"ServiceCall '{payload.service_call_id}' not found")
        )
    diagnostic = DiagnosticReport(**payload.model_dump())
    db.add(diagnostic)
    await db.commit()
    await db.refresh(diagnostic)
    return diagnostic

@router.get("/{diagnostic_id}", response_model=DiagnosticReportRead)
async def get_diagnostic_report_by_id(
    diagnostic_id : int,
    db : AsyncSession = Depends(get_db),
    _ : User = Depends(get_current_user)
)->DiagnosticReport:
    diagnostic = await db.get(DiagnosticReport, diagnostic_id)
    if diagnostic is None: 
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail=(f"Diagnostic Report '{diagnostic_id}' not found")
        )
    return diagnostic

@router.patch("/{diagnostic_id}", response_model=DiagnosticReportRead)
async def update_diagnostic(
    diagnostic_id : int,
    payload : DiagnosticReportUpdate,
    db : AsyncSession = Depends(get_db),
    _ : User = Depends(require_role(UserRole.OPERATIONS_ADMIN,UserRole.FIELD_TECHNICIAN))
)->DiagnosticReport:
    diagnostic = await db.get(DiagnosticReport, diagnostic_id)
    if diagnostic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(f"Diagnostic Log '{diagnostic_id}' not found")
        )
    updates = payload.model_dump(exclude_unset=True)
    if "service_call_id" in updates:
        service_call = await db.get(ServiceCall, updates["service_call_id"])
        if service_call is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ServiceCall '{updates['service_call_id']}' not found"
            )

    for field, value in updates.items():
        setattr(diagnostic, field, value)
    await db.commit()
    await db.refresh(diagnostic)
    return diagnostic

@router.delete("/{diagnostic_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_diagnostic_report(
    diagnostic_id : int,
    db : AsyncSession = Depends(get_db),
    _ : User = Depends(require_role(UserRole.OPERATIONS_ADMIN))
)->Response:
    diagnostic = await db.get(DiagnosticReport, diagnostic_id)
    if diagnostic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(f"Diagnostic Log '{diagnostic_id}' not found")
        )
    await db.delete(diagnostic)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)