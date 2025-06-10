from pydantic import BaseModel, Field
from datetime import datetime, timezone


class submit_applicationModel(BaseModel):
    lessonPlan: str = Field(default="default_plan")
    name: str = Field(..., title="Name", description="The name of the applicant")
    email: str = Field(..., title="Email", description="The email address of the applicant")
    message: str = Field(..., title="Message", description="The message from the applicant")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))  # 現在時刻をUTCで設定

    def __repr__(self):
        return f"submit_applicationModel(name={self.name}, email={self.email}, message={self.message})"
def send_email(submit_application: submit_applicationModel):
    # ここにメール送信のロジックを実装
    print(f"Sending email to {submit_application.email} with message: {submit_application.message}")
def t_submit_application_repository_save(submit_application: submit_applicationModel):
    # ここにデータベース保存のロジックを実装
    print(f"Saving submit_application: {submit_application}")
    # 実際のデータベース操作はここで行う
    # 例: DynamoDBやRDSに保存する処理を実装する
    return True
class submit_applicationUseCase:
    def __init__(self, submit_application: submit_applicationModel):
        self.submit_application = submit_application

    def validate(self):
        # バリデーションを実行
        if not self.submit_application.name or not self.submit_application.email or not self.submit_application.message:
            raise ValueError("全てのフィールドを入力してください。")
        if "@" not in self.submit_application.email:
            raise ValueError("有効なメールアドレスを入力してください。")
        return True

    def execute(self):
        # ビジネスロジックを実行

        # バリデーションを実行
        print("validating submit_application...")
        self.validate()

        # データベースに保存
        print(f"Saving submit_application: {self.submit_application}")
        t_submit_application_repository_save(self.submit_application)

        # メールを送信
        print("Sending email...")
        send_email(self.submit_application)
# エクスポートするオブジェクトを明示的に指定
__all__ = ["submit_applicationModel", "send_email", "t_submit_application_repository_save", "submit_applicationUseCase"]
# これにより、他のモジュールから必要なオブジェクトをインポートできるようになります。
# 例えば、以下のようにインポートできます。
# from submit_application.domain.submit_application import submit_applicationModel, send_email, t_submit_application_repository_save, submit_applicationUseCase
# これにより、submit_applicationModelやsend_emailなどのオブジェクトを他のモジュールで使用できるようになります。             