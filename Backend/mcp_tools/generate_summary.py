from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
from models import Appointment, Doctor
from sqlalchemy.ext.asyncio import AsyncSession


async def get_summary(
    doctor_name: str = None,
    period: str = "today",
    symptom: str = None,
    session: AsyncSession = None
) -> dict:
    now = datetime.now()  

    period = period.lower()
    try:
        if period == "today":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
        elif period == "tomorrow":
            start = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
        elif period == "yesterday":
            start = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
        else:
            return {
                "error": f"Invalid period '{period}'. Choose from 'yesterday', 'today', or 'tomorrow'."
            }
    except Exception as e:
        return {"error": f"Failed to process period: {str(e)}"}

    print(f"Fetching appointments from {start.isoformat()} to {end.isoformat()}")

    if not doctor_name:
        return {"error": "Doctor name is required but missing."}

    result = await session.execute(
        select(Doctor).where(Doctor.name.ilike(f"%{doctor_name.strip()}%"))
    )
    doctor = result.scalars().first()
    if not doctor:
        return {"error": f"No doctor found matching '{doctor_name}'."}

    stmt = (
        select(Appointment)
        .where(
            Appointment.doctor_id == doctor.id,
            Appointment.datetime >= start,
            Appointment.datetime < end
        )
        .options(selectinload(Appointment.patient))
    )

    if symptom:
        stmt = stmt.where(Appointment.symptoms.ilike(f"%{symptom}%"))

    result = await session.execute(stmt)
    appointments = result.scalars().all()

    print(f"Total appointments found: {len(appointments)}")
    for appt in appointments:
        print(f"{appt.datetime.isoformat()} - {appt.patient.name if appt.patient else 'Unknown'}")

    return {
        "doctor": doctor.name,
        "period": period,
        "from": start.isoformat(),
        "to": end.isoformat(),
        "total_appointments": len(appointments),
        "filtered_by_symptom": symptom if symptom else None,
        "appointments": [
            {
                "patient_name": appt.patient.name if appt.patient else "Unknown",
                "datetime": appt.datetime.isoformat(),
                "symptoms": appt.symptoms
            }
            for appt in appointments
        ]
    }
