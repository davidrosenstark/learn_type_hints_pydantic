from enum import Enum

import pytest
from pydantic import BaseModel, validator, root_validator, validate_arguments
from pydantic.error_wrappers import ValidationError


class Subject(str, Enum):
    math = "math"
    history = "history"
    art = "art"


class Grade(BaseModel):
    subject: Subject
    grade: int

    @validator('subject', pre=True)
    def fix_case(cls, subject: str):
        return subject.lower()

    @validator('grade', pre=True)
    def check_grade(cls, grade):
        if grade not in range(1, 100):
            raise ValueError(f"Grade cannot be less than 1 or more than 100")
        return grade

    @root_validator(pre=False, skip_on_failure=True)
    def art_validate(cls, values):
        if values['subject'] == Subject.art and values['grade'] > 90:
            raise ValueError(f"Art grade cannot exceed 90")
        return values


def test_valid():
    g = Grade(subject="Math", grade=80)
    assert g.dict() == {'subject': 'math', 'grade': 80}


def test_invalid_grade():
    with pytest.raises(ValidationError) as ex:
        Grade(subject="Math", grade=101)
    assert str(
        ex.value
    ) == '1 validation error for Grade\ngrade\n  Grade cannot be less than 1 or more than 100 (type=value_error)'


def test_invalid_subject_grade():
    with pytest.raises(ValidationError) as ex:
        Grade(subject="Grammar", grade=101)
    assert str(
        ex.value
    ) == "2 validation errors for Grade\nsubject\n  value is not a valid enumeration member; permitted: 'math', " \
         "'history', 'art' (type=type_error.enum; enum_values=[<Subject.math: 'math'>, <Subject.history: 'history'>," \
         " <Subject.art: 'art'>])\ngrade\n  Grade cannot be less than 1 or more than 100 (type=value_error)"


def test_art_validate():
    with pytest.raises(ValidationError) as ex:
        Grade(subject="art", grade=95)
    assert str(
        ex.value
    ) == "1 validation error for Grade\n__root__\n  Art grade cannot exceed 90 (type=value_error)"

def func(grade: Grade):
    print(grade)
    return "ok"

@validate_arguments()
def func_with_validate(grade: Grade):
    return ("should not work")


def test_func_validate():
    assert func({'subject': "Math", "grade": 101}) == "ok"


def test_func_validate_fail():
    with pytest.raises(ValidationError) as ex:
        func_with_validate({'subject': "Math", "grade": 101})
    assert str(
        ex.value
    ) == "1 validation error for FuncWithValidate\ngrade -> grade\n  Grade cannot be less than 1 or more than 100 (type=value_error)"
