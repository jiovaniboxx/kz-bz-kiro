from pydantic import BaseModel, Field
from datetime import datetime, timezone

class SignInModel(BaseModel):
    email: str = Field(..., title="Email", description="The email address of the user")
    password: str = Field(..., title="Password", description="The password of the user")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))  # 現在時刻をUTCで設定

    def __repr__(self):
        return f"SignInModel(email={self.email})"

    def send_email(signin: SignInModel):
        # ここにメール送信のロジックを実装
        print(f"Sending email to {signin.email} for sign-in.")
        return "メール送信完了"
