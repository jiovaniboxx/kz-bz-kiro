from signin.domain.signin_model import SignInModel
from signin.infrastructure.t_signin_repository import get_item


def get(signin: SignInModel):
    # ここにデータベースレコード取得のロジックを実装
    print(f"verify sign-in data: {signin}")
    # 実際のデータベース操作はここで行う
    # 例: DynamoDBやRDSからレコード取得する処理を実装する
    try:
        item = {
            "email": signin.email,
            "password": signin.password,
            "created_at": signin.created_at.isoformat(),
        }
        # DynamoDBのget_itemを使用してデータを保存
        res = get_item(
            TableName="t_user_information",
            Key={"email": {"S": signin.email}},
            Item=item
        )
        print(f"Sign-in data saved successfully: {res}")
    except Exception as e:
        print(f"Error saving sign-in data: {e}")

    # ここでは常に成功と仮定
    print("Sign-in data is valid.")

    return True
