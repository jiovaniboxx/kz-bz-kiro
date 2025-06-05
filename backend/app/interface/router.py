from fastapi import APIRouter
from app.usecase.contact import ContactUseCase
from app.domain.contact import ContactModel

router = APIRouter()

@router.post("/api/contact")
def submit_contact_form(contact: ContactModel):
    # `ContactModel`を受け取り、ビジネスロジックを実行
    print(f"Received contact form: {contact}")
    ContactUseCase(contact).execute()
    return {"message": "お問い合わせを受け付けました！"}

@router.get("/")
def read_root():
    print("Root endpoint accessed")
    return {"message": "Welcome to the API!"}
