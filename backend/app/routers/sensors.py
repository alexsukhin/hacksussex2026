from fastapi import APIRouter

router = APIRouter(
    prefix="/sensors",
    tags=["sensors"]
)

@router.get("/")
def get_sensors():
    return {"message": "List sensors here (not implemented yet)"}