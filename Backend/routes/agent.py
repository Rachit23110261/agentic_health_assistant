from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session
from agents.openai_agent import get_llm_response

router = APIRouter()

@router.post("/agent")
async def agent_endpoint(
    data: dict = Body(...),
    session: AsyncSession = Depends(get_session)
):
    prompt = data.get("prompt")
    user = data.get("user")
    chat_history = data.get("chat_history", [])

    try:
        response = await get_llm_response(prompt=prompt, chat_history=chat_history, user=user)
        return {"response": response}
    except Exception as e:
        return {"error": str(e)}
