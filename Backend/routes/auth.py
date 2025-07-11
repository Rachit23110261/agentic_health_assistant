from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.future import select
from models import Doctor, Patient
from database import get_session

router = APIRouter()

@router.post("/login")
async def login(
    name: str = Query(...),
    email: str = Query(...),
    role: str = Query(...)
):
    async with get_session() as session:
        if role == "doctor":
            result = await session.execute(select(Doctor).where(Doctor.email == email))
            doctor = result.scalars().first()

            if doctor:
                created = False
            else:
                doctor = Doctor(name=name, email=email)
                session.add(doctor)
                await session.commit()
                await session.refresh(doctor)
                created = True
                # ➕ OPTIONAL: Create default schedule/profile/etc. here

            return {
                "message": f"Doctor '{doctor.name}' {'created and' if created else ''} logged in.",
                "user": {"name": doctor.name, "email": doctor.email, "role": "doctor"},
                "created": created
            }

        elif role == "patient":
            result = await session.execute(select(Patient).where(Patient.email == email))
            patient = result.scalars().first()

            if patient:
                created = False
            else:
                patient = Patient(name=name, email=email)
                session.add(patient)
                await session.commit()
                await session.refresh(patient)
                created = True
                # ➕ OPTIONAL: Create default medical history/etc. here

            return {
                "message": f"Patient '{patient.name}' {'created and' if created else ''} logged in.",
                "user": {"name": patient.name, "email": patient.email, "role": "patient"},
                "created": created
            }

        else:
            raise HTTPException(status_code=400, detail=f"Invalid role '{role}'")
