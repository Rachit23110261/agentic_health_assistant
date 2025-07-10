from datetime import datetime, timedelta
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from models import Doctor, Patient, Appointment
from agents.utils.google_calendar import create_event
from agents.utils.email_utils import send_confirmation_email

SLOTS = [
    "09:00", "10:00", "11:00", "12:00",
    "14:00", "15:00", "16:00", "17:00"
]

def resolve_date_str(date_input: str) -> str:
    now = datetime.now()
    print( "NOW _______>" , now)
    date_input = date_input.strip().lower()
    if date_input == "today":
        return now.strftime("%Y-%m-%d")
    elif date_input == "tomorrow":
        return (now + timedelta(days=1)).strftime("%Y-%m-%d")
    elif date_input == "yesterday":
        return (now - timedelta(days=1)).strftime("%Y-%m-%d")
    return date_input 

async def schedule_appointment(
    doctor_name: str,
    patient_name: str,
    date: str,
    time: str,
    session,
    email: str = None
) -> dict:
    try:
        resolved_date_str = resolve_date_str(date)
        try:
            appointment_dt = datetime.strptime(f"{resolved_date_str} {time}", "%Y-%m-%d %H:%M")
        except ValueError:
            return {"error": f"Invalid date/time format: '{resolved_date_str} {time}'. Use YYYY-MM-DD and HH:MM."}

        parsed_time = appointment_dt.strftime("%H:%M")
        if parsed_time not in SLOTS:
            return {
                "error": f"Time '{parsed_time}' is not a valid slot. Valid slots are: {', '.join(SLOTS)}"
            }

    except Exception:
        return {
            "error": f"Couldn't understand date/time: '{date} {time}'. Try formats like '2025-07-14' and '09:00'."
        }

    try:
        result = await session.execute(select(Doctor).where(Doctor.name == doctor_name))
        doctor = result.scalars().first()
        if not doctor:
            result = await session.execute(select(Doctor).where(Doctor.name.ilike(f"%{doctor_name}%")))
            doctor = result.scalars().first()
        if not doctor:
            return {"error": f"No doctor found with name '{doctor_name}'."}

        result = await session.execute(select(Patient).where(Patient.name == patient_name))
        patient = result.scalars().first()
        if not patient:
            patient = Patient(name=patient_name, email=email if email else None)
            session.add(patient)
            await session.flush()
            await session.refresh(patient)

        if not patient.email and email:
            patient.email = email
            await session.commit()

        if not patient.email:
            await session.commit()
            return {
                "error": f"Missing email for patient '{patient.name}'.",
                "action_required": f"Please provide the email address for {patient.name}.",
                "next_step": {
                    "function": "update_email",
                    "params": {"patient_name": patient.name}
                }
            }

        print("APPOINTMENT DATETIME:", appointment_dt)
        result = await session.execute(
            select(Appointment).where(
                Appointment.doctor_id == doctor.id,
                Appointment.datetime == appointment_dt
            )
        )
        if result.scalars().first():
            # Suggest alternatives
            day_start = appointment_dt.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            result = await session.execute(
                select(Appointment).where(
                    Appointment.doctor_id == doctor.id,
                    Appointment.datetime >= day_start,
                    Appointment.datetime < day_end
                )
            )
            booked = [a.datetime.strftime("%H:%M") for a in result.scalars()]
            suggestions = [s for s in SLOTS if s not in booked and s != parsed_time]

            if suggestions:
                return {
                    "error": f"Slot {parsed_time} on {appointment_dt.date()} is already booked.",
                    "suggestions": suggestions[:3]
                }

            fallback_dates = []
            for offset in range(1, 6):
                next_date = (appointment_dt + timedelta(days=offset)).date()
                next_day_start = datetime.combine(next_date, datetime.min.time())
                next_day_end = next_day_start + timedelta(days=1)

                result = await session.execute(
                    select(Appointment).where(
                        Appointment.doctor_id == doctor.id,
                        Appointment.datetime >= next_day_start,
                        Appointment.datetime < next_day_end
                    )
                )
                booked = [a.datetime.strftime("%H:%M") for a in result.scalars()]
                available = [s for s in SLOTS if s not in booked]
                if available:
                    fallback_dates.append({
                        "date": next_date.isoformat(),
                        "available": available
                    })

            return {
                "error": f"Slot {parsed_time} is booked and no availability left that day.",
                "next_available_days": fallback_dates or ["No free slots in next 5 days."]
            }

        appointment = Appointment(
            doctor_id=doctor.id,
            patient_id=patient.id,
            datetime=appointment_dt
        )
        session.add(appointment)
        await session.commit()

        try:
            calendar_link = create_event(
                summary=f"Appointment with {doctor.name}",
                description=f"Checkup with Dr. {doctor.name} for {patient.name}",
                start_time=appointment_dt,
                attendee_email=patient.email
            )
        except Exception as e:
            print("Calendar error:", e)
            calendar_link = "Calendar invite could not be created."

        try:
            send_confirmation_email(
                to_email=patient.email,
                patient_name=patient.name,
                doctor_name=doctor.name,
                date=appointment_dt.strftime('%Y-%m-%d'),
                time=parsed_time,
                calendar_link=calendar_link
            )
        except Exception as e:
            print("Email error:", e)

        return {
            "message": f"Appointment scheduled with {doctor.name} for {patient.name} on {appointment_dt.strftime('%Y-%m-%d')} at {parsed_time}.",
            "appointment_id": appointment.id
        }

    except SQLAlchemyError as e:
        await session.rollback()
        return {"error": f"Database error: {str(e)}"}

    except Exception as e:
        await session.rollback()
        return {"error": f"Unexpected error: {str(e)}"}
