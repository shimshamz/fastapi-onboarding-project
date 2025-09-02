import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import col, delete, func, select

from app import crud
from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from app.models import (
    AcademicInstitutionCreate,
    AcademicInstitutionPublic,
    AcademicInstitutionPublicWithStudents,
    StudentCreate,
    StudentPublic,
    StudentPublicWithAcademicInstitution,
)

router = APIRouter(prefix="/academic_institutions", tags=["academic institutions"])

@router.get("/")
def read_academic_institutions(
    session: SessionDep, offset: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve Academic Institutions.
    """
    return {"message": "read_academic_institutions"}