from fastapi import APIRouter
from signin.usecase.signin import SigninUseCase
from signin.domain.signin import SigninModel

signin_router = APIRouter()
@signin_router.post("/api/auth/signin")
def signin_user(signin: SigninModel):
    print(f"Received signin request: {signin}")
    SigninUseCase(signin).execute()
    return {"message": "サインインが成功しました！"}

@signin_router.get("/")
def read_root():
    print("Root endpoint accessed")
    return {"message": "Welcome to the Signin API!"}
