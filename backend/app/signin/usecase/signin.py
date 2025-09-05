from signin.domain import SignInRequest, SignInResponse
from signin.infrastructure import t_signin_repository as SignInRepository
from signin.infrastructure import t_user_signin_history_repository as SignInHistoryRepository
from backend.app.signin.domain.signin_model import SignInRequest, SignInResponse

def validate(self):
    # バリデーションを実行
    if not self.signin_request.username or not self.signin_request.password:
        raise ValueError("ユーザー名とパスワードを入力してください。")
    return True

class SigninUseCase:

    def execute(self) -> SignInResponse:
        # ビジネスロジックを実行
        # バリデーションを実行
        print("validating signin...")
        validate()

        # データベースとサインイン情報を照合
        print(f"Saving signin request: {self.signin_request}")
        result = SignInRepository.get(self.signin_request)
        if not result:
            raise ValueError("サインイン情報が正しくありません。")

        print("Signin data is valid.")
        # ここでは実際のデータベース操作を行う
        # ユーザーのログイン履歴を保存
        print("Saving user login history...")
        result = SignInHistoryRepository.save(self.signin_request)
        if not result:
            raise ValueError("ログイン履歴の保存に失敗しました。")
        # ここでは実際のデータベース操作を行う
        # 例: DynamoDBやRDSにログイン履歴を保存する処理を実装する
        print(f"Signin data saved successfully: {result}")

        # レスポンスを返す
        print("サインインが成功しました！")
        return True
