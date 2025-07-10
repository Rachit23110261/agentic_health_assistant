from sqlalchemy.future import select
from models import Patient

async def update_email(patient_name: str, email: str, session) -> dict:
    result = await session.execute(select(Patient).where(Patient.name == patient_name))
    patient = result.scalars().first()

    if not patient:
        return {"error": f"Patient '{patient_name}' not found."}

    patient.email = email
    await session.commit()

    return {
        "message": f"Email updated for {patient.name}.",
        "patient_name": patient.name,
        "email": patient.email
    }
