from fastapi import APIRouter, Depends
from Backend.database import get_session
from Backend.mcp_tools.update_email import update_email
from sqlalchemy.future import select

from models import Patient
router = APIRouter()

@router.post("/update_email")
async def update_patient_email(patient_name: str, email: str, session = Depends(get_session)):
    result = await session.execute(select(Patient).where(Patient.name == patient_name))
    patient = result.scalars().first()
    if not patient:
        return {"error": "Patient not found."}

    patient.email = email
    await session.commit()
    return {"message": f"Email for {patient.name} updated successfully."}
