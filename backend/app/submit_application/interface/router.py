from fastapi import APIRouter
from submit_application.usecase.submit_application import submit_application_usecase
from submit_application.domain.submit_application import submit_applicationModel

submit_application_router = APIRouter()

@submit_application_router.post("/api/submit-application")
def submit_application_form(submit_application: submit_applicationModel):
    print(f"Received contact form: {submit_application}")
    submit_application_usecase(submit_application).execute()
    return {"message": "お申し込みを受け付けました！"}