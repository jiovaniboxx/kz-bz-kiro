from submit_application.domain.submit_application import submit_applicationModel
from submit_application.domain.submit_application import send_email
from submit_application.infrastructure.t_submit_application_repository import t_submit_application_repository_save

class submit_application_usecase:
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