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
    AcademicInstitution,
    AcademicInstitutionCreate,
    AcademicInstitutionPublic,
    AcademicInstitutionsPublic,
    AcademicInstitutionPublicWithStudents,
    Student,
    StudentCreate,
    StudentPublic,
    StudentsPublic,
    StudentPublicWithAcademicInstitution,
)

router = APIRouter(prefix="/academic_institutions", tags=["academic institutions"])

async def verify_academic_institution(session, institution_id):
    academic_institution = crud.get_academic_institution_by_id(session=session, id=institution_id)
    if not academic_institution:
        raise HTTPException(status_code=404, detail="Academic Institution not found")
    return academic_institution

@router.post("/", dependencies=[Depends(get_current_active_superuser)], response_model=AcademicInstitutionPublic)
async def create_academic_institution(
    *, session: SessionDep, current_user: CurrentUser, academic_institution_in: AcademicInstitutionCreate
    ) -> Any:
    """
    Create new academic institution.
    """
    
    db_academic_institution = AcademicInstitution.model_validate(academic_institution_in)
    session.add(db_academic_institution)
    session.commit()
    session.refresh(db_academic_institution)
    return db_academic_institution

@router.get("/", dependencies=[Depends(get_current_active_superuser)], response_model=AcademicInstitutionsPublic)
async def read_academic_institutions(session: SessionDep, offset: int = 0, limit: int = 100) -> Any:
    """
    Retrieve Academic Institutions.
    """

    count_statement = select(func.count()).select_from(AcademicInstitution)
    count = session.exec(count_statement).one()

    statement = select(AcademicInstitution).offset(offset).limit(limit)
    academic_institutions = session.exec(statement).all()

    return AcademicInstitutionsPublic(data=academic_institutions, count=count)

@router.get("/{institution_id}", dependencies=[Depends(get_current_active_superuser)], response_model=AcademicInstitutionPublicWithStudents)
async def read_academic_institution(session: SessionDep, institution_id: uuid.UUID) -> Any:
    """
    Get Academic Institution by ID.
    """

    academic_institution = verify_academic_institution(session, institution_id)

    return academic_institution

@router.get("/{institution_id}/students", dependencies=[Depends(get_current_active_superuser)], response_model=StudentsPublic)
async def read_academic_institution_students(session: SessionDep, institution_id: uuid.UUID, offset: int = 0, limit: int = 100) -> Any:
    """
    Retrieve Students.
    """

    academic_institution = verify_academic_institution(session, institution_id)

    students = academic_institution.students
    count = len(students)

    return StudentsPublic(data=students, count=count)

@router.post("/{institution_id}/students", dependencies=[Depends(get_current_active_superuser)], response_model=StudentPublic)
async def create_academic_institution_student(
    *, session: SessionDep, institution_id: uuid.UUID, student_in: StudentCreate
    ) -> Any:
    """
    Create student.
    """

    academic_institution = verify_academic_institution(session, institution_id)

    db_student = Student.model_validate(student_in, update={"academic_institution_id": institution_id})
    session.add(db_student)
    session.commit()
    session.refresh(db_student)
    return db_student

@router.get("/{institution_id}/students/{student_id}", dependencies=[Depends(get_current_active_superuser)], response_model=StudentPublicWithAcademicInstitution)
async def read_academic_institution_student(session: SessionDep, institution_id: uuid.UUID, student_id: uuid.UUID) -> Any:
    """
    Retrieve Student by ID.
    """

    academic_institution = verify_academic_institution(session, institution_id)

    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student
