from fastapi import APIRouter, Depends
from Backend.database import get_session
from Backend.mcp_tools.check_availability import check_availability

router = APIRouter()

@router.get("/check-availability")
async def check(doctor_name: str, date: str, session=Depends(get_session)):
    return await check_availability(doctor_name, date, session)