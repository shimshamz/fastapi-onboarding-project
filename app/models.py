import uuid

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel
from datetime import datetime, timezone, date

def get_utc_now() -> datetime:
        return datetime.now(timezone.utc)

# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)

class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)

# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str

# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None

# AcademicInstitution
class AcademicInstitutionBase(SQLModel):
    name: str = Field(index=True, max_length=255)

class AcademicInstitution(AcademicInstitutionBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=get_utc_now)

    students: list["Student"] = Relationship(back_populates="academic_institution")

class AcademicInstitutionPublic(AcademicInstitutionBase):
    id: uuid.UUID

class AcademicInstitutionCreate(AcademicInstitutionBase):
    pass

class AcademicInstitutionPublicWithStudents(AcademicInstitutionPublic):
    students: list["StudentPublic"] = []

class AcademicInstitutionsPublic(SQLModel):
    data: list[AcademicInstitutionPublicWithStudents]
    count: int

# Student
class StudentBase(SQLModel):
    name: str = Field(index=True, max_length=255)

class Student(StudentBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    enrollment_date: datetime = Field(default_factory=get_utc_now)

    academic_institution_id: uuid.UUID = Field(
        foreign_key="academicinstitution.id", nullable=False, ondelete="CASCADE"
    )
    academic_institution: AcademicInstitution | None = Relationship(back_populates="students")

class StudentPublic(StudentBase):
    id: uuid.UUID
    enrollment_date: datetime

class StudentCreate(StudentBase):
    pass

class StudentPublicWithAcademicInstitution(StudentPublic):
    academic_institution: AcademicInstitutionPublic | None = None

class StudentsPublic(SQLModel):
    data: list[StudentPublicWithAcademicInstitution]
    count: int