#!/usr/bin/env python3
"""
管理者アカウント作成スクリプト
"""
import asyncio
import sys
import os
from getpass import getpass

# パスを追加してアプリケーションモジュールをインポート可能にする
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.domain.admin import Admin
from app.infrastructure.repositories.admin_repository import AdminRepository
from app.core.database import get_async_session
from app.utils.event_bus import EventBus

async def create_admin():
    """管理者アカウントを作成"""
    print("=== 管理者アカウント作成 ===")
    
    # 入力値取得
    username = input("ユーザー名: ").strip()
    if not username:
        print("エラー: ユーザー名は必須です")
        return
    
    email = input("メールアドレス: ").strip()
    if not email:
        print("エラー: メールアドレスは必須です")
        return
    
    password = getpass("パスワード: ")
    if len(password) < 8:
        print("エラー: パスワードは8文字以上である必要があります")
        return
    
    password_confirm = getpass("パスワード（確認）: ")
    if password != password_confirm:
        print("エラー: パスワードが一致しません")
        return
    
    role = input("ロール (admin/staff) [admin]: ").strip() or "admin"
    if role not in ["admin", "staff"]:
        print("エラー: ロールはadminまたはstaffである必要があります")
        return
    
    # データベース接続
    try:
        async with get_async_session() as session:
            admin_repository = AdminRepository(session)
            
            # 既存チェック
            existing_username = await admin_repository.find_by_username(username)
            if existing_username:
                print(f"エラー: ユーザー名 '{username}' は既に使用されています")
                return
            
            existing_email = await admin_repository.find_by_email(email)
            if existing_email:
                print(f"エラー: メールアドレス '{email}' は既に使用されています")
                return
            
            # 管理者作成
            admin = Admin.create(username, email, password, role)
            saved_admin = await admin_repository.save(admin)
            
            print(f"✅ 管理者アカウントを作成しました:")
            print(f"   ID: {saved_admin.id}")
            print(f"   ユーザー名: {saved_admin.username}")
            print(f"   メールアドレス: {saved_admin.email}")
            print(f"   ロール: {saved_admin.role}")
            print(f"   作成日時: {saved_admin.created_at}")
    
    except Exception as e:
        print(f"エラー: 管理者アカウントの作成に失敗しました: {e}")

async def list_admins():
    """管理者一覧を表示"""
    print("=== 管理者一覧 ===")
    
    try:
        async with get_async_session() as session:
            admin_repository = AdminRepository(session)
            admins = await admin_repository.find_all_active()
            
            if not admins:
                print("管理者アカウントが見つかりません")
                return
            
            for admin in admins:
                print(f"ID: {admin.id}")
                print(f"ユーザー名: {admin.username}")
                print(f"メールアドレス: {admin.email}")
                print(f"ロール: {admin.role}")
                print(f"アクティブ: {admin.is_active}")
                print(f"作成日時: {admin.created_at}")
                print(f"最終ログイン: {admin.last_login or 'なし'}")
                print("-" * 40)
    
    except Exception as e:
        print(f"エラー: 管理者一覧の取得に失敗しました: {e}")

async def main():
    """メイン関数"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python create_admin.py create  # 管理者作成")
        print("  python create_admin.py list    # 管理者一覧")
        return
    
    command = sys.argv[1]
    
    if command == "create":
        await create_admin()
    elif command == "list":
        await list_admins()
    else:
        print(f"不明なコマンド: {command}")
        print("使用可能なコマンド: create, list")

if __name__ == "__main__":
    asyncio.run(main())