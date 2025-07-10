tools = [
    {
        "type": "function",
    "function": {
        "name": "update_email",
        "description": "Ask for and update a patient's email address if not already provided.",
        "parameters": {
            "type": "object",
            "properties": {
                "patient_id": {
                    "type": "integer",
                    "description": "The ID of the patient whose email needs to be updated"
                },
                "email": {
                    "type": "string",
                    "description": "The new email address"
                }
            },
            "required":  ["patient_name", "email"]
        }
    }
    },
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": "Check if a doctor is available on a specific date",
            "parameters": {
                "type": "object",
                "properties": {
                    "doctor_name": {"type": "string"},
                    "date": {"type": "string", "description": "Date in YYYY-MM-DD format"}
                },
                "required": ["doctor_name", "date"]
            }
        }
    },
    {"type": "function",
    "function": {
        "name": "schedule_appointment",
        "description": "Book an appointment for a patient with a doctor on a specific date and time.",
        "parameters": {
            "type": "object",
            "properties": {
                "doctor_name": {
                    "type": "string",
                    "description": "Full name of the doctor (e.g. 'Dr. Ahuja')"
                },
                "patient_name": {
                    "type": "string",
                    "description": "Full name of the patient"
                },
                "date": {
                    "type": "string",
                    "description": "Date in 'YYYY-MM-DD' format (e.g., '2025-07-14')"
                },
                "time": {
                    "type": "string",
                    "description": "Time in 24-hour format 'HH:MM' (e.g., '09:00')"
                }
            },
            "required": ["doctor_name", "patient_name", "date", "time"]
        }
    }},
    {
    "type": "function",
    "function": {
        "name": "get_summary",
        "description": "Summarizes a doctor's appointments for a given period like today, tomorrow, or yesterday.",
        "parameters": {
            "type": "object",
            "properties": {
                "doctor_name": {
                    "type": "string",
                    "description": "Name of the doctor (e.g., 'Dr. Ahuja')"
                },
                "period": {
                    "type": "string",
                    "enum": ["today", "tomorrow", "yesterday"],
                    "description": "Time period for summary (e.g., 'today', 'tomorrow')"
                },
                "symptom": {
                    "type": "string",
                    "description": "Optional symptom filter (e.g., 'fever')"
                }
            },
            "required": ["period"]
        }
    }
}
]
