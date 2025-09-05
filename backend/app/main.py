from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contact.interface.router import contact_router
from submit_application.interface.router import submit_application_router
from signin.interface.router import signin_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ここで許可するオリジンを指定
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルートを登録
app.include_router(contact_router)
app.include_router(submit_application_router)
app.include_router(signin_router)

if (__name__) == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)