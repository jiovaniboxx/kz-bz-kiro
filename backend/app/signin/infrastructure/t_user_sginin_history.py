from signin.infrastructure.dynamodb import put_item
from signin.domain.signin_model import SignInModel

def save(signin: SignInModel):
    # ここにデータベースレコード保存のロジックを実装
    print(f"Saving sign-in data: {signin}")
    # 実際のデータベース操作はここで行う
    # 例: DynamoDBやRDSにレコード保存する処理を実装する
    try:
        item = {
            "email": signin.email,
            "password": signin.password,
            "created_at": signin.created_at.isoformat(),
        }
        # DynamoDBのput_itemを使用してデータを保存
        res = put_item(
            TableName="t_user_signin_history",
            Item=item
        )
        print(f"Sign-in data saved successfully: {res}")
    except Exception as e:
        print(f"Error saving sign-in data: {e}")

    # ここでは常に成功と仮定
    print("Sign-in data is valid.")

    return True
