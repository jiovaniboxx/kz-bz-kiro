from fastapi import APIRouter
from contact.usecase.contact import ContactUseCase
from contact.domain.contact import ContactModel

contact_router = APIRouter()

@contact_router.post("/api/contact")
def submit_contact_form(contact: ContactModel):
    # `ContactModel`を受け取り、ビジネスロジックを実行
    print(f"Received contact form: {contact}")
    ContactUseCase(contact).execute()
    return {"message": "お問い合わせを受け付けました！"}

@contact_router.get("/")
def read_root():
    print("Root endpoint accessed")
    return {"message": "Welcome to the API!"}
