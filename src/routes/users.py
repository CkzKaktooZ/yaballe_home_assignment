from fastapi import APIRouter

router = APIRouter(tags=["Users"])

@router.post("/register")
def register():
    pass
    
@router.post("/login")    
def login():
    pass