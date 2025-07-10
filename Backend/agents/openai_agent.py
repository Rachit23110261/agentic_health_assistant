import json
from agents.llm_client import chat_with_llm
from agents.utils.tools import tools
from mcp_tools import check_availability, schedule_appointment, update_email, generate_summary
from database import get_session
SYSTEM_PROMPT_TEMPLATE = """You are a helpful health assistant.
The current user is a {role} named {name}.
Always use this information to infer missing 'doctor_name' or 'patient_name' in tool calls.
If the user is a doctor, assume they are asking about their own appointments unless stated otherwise.
Always speak politely and clearly in your responses.
Do NOT convert fuzzy dates like “tomorrow”, “today”, “yesterday”, or weekday names like “Friday” into fixed YYYY-MM-DD format in tool calls.
Instead, pass them literally as 'tomorrow', 'today', etc. — the backend will resolve them using the correct year.
Always provide time in 24-hour HH:MM format (e.g., 09:00, 14:00) in tool calls.
"""
def build_system_prompt(user: dict):
    return {
        "role": "system",
        "content": SYSTEM_PROMPT_TEMPLATE.format(
            role=user.get("role", "user"),
            name=user.get("name", "Unknown")
        )
    }

def inject_user_args(tool_name: str, args: dict, user: dict) -> dict:
    print(f"[Injecting args] Tool: {tool_name}, User: {user}, Args before: {args}")

    if tool_name == "get_summary":
        if not args.get("doctor_name") or args["doctor_name"].strip() == "":
            if user.get("role") == "doctor" and user.get("name"):
                args["doctor_name"] = user["name"]

    if tool_name == "schedule_appointment":
        if not args.get("patient_name") or args["patient_name"].strip() == "":
            if user.get("role") == "patient" and user.get("name"):
                args["patient_name"] = user["name"]

    if tool_name in ["schedule_appointment", "update_email"]:
        if not args.get("email") and user.get("email"):
            args["email"] = user["email"]

    print(f"[Injecting args] Args after: {args}")
    return args

def format_tool_result(tool_name, result):
    if "error" in result:
        return f"Error: {result['error']}"

    if tool_name == "get_summary":
        summary = f"Summary for {result['doctor']} ({result['period']}):\n"
        summary += f"Total appointments: {result['total_appointments']}\n"
        if result.get("filtered_by_symptom"):
            summary += f"Filtered by symptom: {result['filtered_by_symptom']}\n"
        for appt in result["appointments"]:
            summary += f"- {appt['patient_name']} at {appt['datetime']} ({appt['symptoms']})\n"
        return summary or "No appointments found."

    return json.dumps(result, indent=2)

async def get_llm_response(prompt: str, chat_history: list, user: dict):
    user = user.get("user", user)
    print("User context injected:", user)
    messages = [build_system_prompt(user)] + chat_history + [{"role": "user", "content": prompt}]

    response = await chat_with_llm(messages, tools=tools, tool_choice="auto")
    message = response.choices[0].message

    if not hasattr(message, "tool_calls"):
        return message.content or "Assistant gave no reply."

    tool_call = message.tool_calls[0]
    tool_name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)
    print(f"Tool: {tool_name}")
    print(f"Raw Args: {args}")

    args = inject_user_args(tool_name, args, user)
    print(f"Final Args: {args}")

    async with get_session() as session:
        try:
            if tool_name == "check_availability":
                tool_result = await check_availability(**args, session=session)
            elif tool_name == "schedule_appointment":
                tool_result = await schedule_appointment.schedule_appointment(**args, session=session)
            elif tool_name == "update_email":
                tool_result = await update_email.update_email(**args, session=session)
            elif tool_name == "get_summary":
                tool_result = await generate_summary.get_summary(**args, session=session)
                print("******TOOL RESULT*****", tool_result)
            else:
                tool_result = {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            print(f"Exception during tool call to {tool_name}:", str(e))
            tool_result = {"error": str(e)}

    messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "name": tool_name,
        "content": json.dumps(tool_result)
    })

    followup_response = await chat_with_llm(messages)
    final_message = followup_response.choices[0].message

    if final_message.content:
        return final_message.content
    elif hasattr(final_message, "tool_calls"):
        return format_tool_result(tool_name, tool_result)
    else:
        return "No response from assistant after tool execution."
