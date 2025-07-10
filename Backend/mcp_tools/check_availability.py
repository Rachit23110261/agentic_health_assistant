from datetime import datetime, timedelta, time
from sqlalchemy.future import select
from models import Doctor, Appointment
from typing import List, Dict

WORK_HOURS = [(9, 12), (14, 17)] 
SLOT_DURATION = 60  

def generate_slots(date: datetime) -> List[datetime]:
    slots = []
    for start_hour, end_hour in WORK_HOURS:
        for hour in range(start_hour, end_hour + 1):
            slots.append(datetime.combine(date.date(), time(hour, 0)))
    return slots

async def check_availability(doctor_name: str, date: str, session) -> Dict:

    try:
        date_obj = datetime.fromisoformat(date)
    except ValueError:
        return {"error": "Invalid date format. Please use YYYY-MM-DD."}

    # Step 1: Fetch doctor
    result = await session.execute(select(Doctor).where(Doctor.name == doctor_name))
    doctor = result.scalars().first()
    if not doctor:
        return {"error": f"No doctor found with name '{doctor_name}'."}

    all_slots = generate_slots(date_obj)

    start_of_day = datetime.combine(date_obj.date(), time(0, 0))
    end_of_day = start_of_day + timedelta(days=1)

    result = await session.execute(
        select(Appointment).where(
            Appointment.doctor_id == doctor.id,
            Appointment.datetime >= start_of_day,
            Appointment.datetime < end_of_day
        )
    )
    appointments = result.scalars().all()
    booked_times = {appt.datetime.strftime("%H:%M") for appt in appointments}

    available_slots = [
        slot.strftime("%H:%M") for slot in all_slots
        if slot.strftime("%H:%M") not in booked_times
    ]
    


    return {
        "doctor": doctor.name,
        "date": date_obj.strftime("%Y-%m-%d"),
        "available_slots": available_slots,
        "total_slots": len(all_slots),
        "booked": sorted(list(booked_times)),
    }
