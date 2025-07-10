from fastapi import APIRouter, Depends, Query
from sqlalchemy.future import select
from models import Doctor, Patient
from database import get_session

router = APIRouter()

@router.post("/login")
async def login(name: str = Query(...), email: str = Query(...), role: str = Query(...)):
    from models import Doctor, Patient 

    async with get_session() as session:
        if role == "doctor":
            result = await session.execute(select(Doctor).where(Doctor.email == email))
            doctor = result.scalars().first()
            if not doctor:
                doctor = Doctor(name=name, email=email)
                session.add(doctor)
                await session.commit()
                await session.refresh(doctor)
            return {"message": f"Doctor '{doctor.name}' logged in.", "user": {"name": doctor.name, "email": doctor.email, "role": "doctor"}}

        elif role == "patient":
            result = await session.execute(select(Patient).where(Patient.email == email))
            patient = result.scalars().first()
            if not patient:
                patient = Patient(name=name, email=email)
                session.add(patient)
                await session.commit()
                await session.refresh(patient)
            return {"message": f"Patient '{patient.name}' logged in.", "user": {"name": patient.name, "email": patient.email, "role": "patient"}}

        else:
            return {"error": f"Invalid role '{role}'"}
