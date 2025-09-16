"""
問い合わせ管理API（管理者用）
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.services.auth_service import get_current_admin
from app.domain.admin import Admin
from app.domain.contact import Contact
from app.infrastructure.repositories.sqlalchemy_contact_repository import ContactRepository
from app.core.database import get_db_session

router = APIRouter(prefix="/api/admin/contacts", tags=["問い合わせ管理"])

# レスポンスモデル
class ContactListItem(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str]
    lesson_type: Optional[str]
    preferred_contact: str
    status: str
    submitted_at: str
    updated_at: Optional[str]

class ContactDetail(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str]
    message: str
    lesson_type: Optional[str]
    preferred_contact: str
    status: str
    submitted_at: str
    updated_at: Optional[str]
    admin_notes: Optional[str]

class ContactListResponse(BaseModel):
    contacts: List[ContactListItem]
    total: int
    page: int
    per_page: int
    total_pages: int

class UpdateContactStatusRequest(BaseModel):
    status: str
    admin_notes: Optional[str] = None

class ContactStatusResponse(BaseModel):
    message: str

# 依存関数
async def get_contact_repository(
    db: AsyncSession = Depends(get_db_session)
) -> ContactRepository:
    """ContactRepositoryの依存注入"""
    return ContactRepository(db)

def require_admin_or_staff(admin: Admin = Depends(get_current_admin)) -> Admin:
    """管理者またはスタッフ権限を要求"""
    if admin.role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="管理者またはスタッフ権限が必要です"
        )
    return admin

# エンドポイント
@router.get("/", response_model=ContactListResponse)
async def get_contacts(
    page: int = Query(1, ge=1, description="ページ番号"),
    per_page: int = Query(20, ge=1, le=100, description="1ページあたりの件数"),
    status: Optional[str] = Query(None, description="ステータスフィルター"),
    search: Optional[str] = Query(None, description="検索キーワード（名前、メール）"),
    admin: Admin = Depends(require_admin_or_staff),
    contact_repo: ContactRepository = Depends(get_contact_repository)
):
    """問い合わせ一覧を取得"""
    try:
        # フィルター条件を構築
        filters = {}
        if status:
            filters["status"] = status
        
        # 問い合わせ一覧を取得
        contacts, total = await contact_repo.find_with_pagination(
            page=page,
            per_page=per_page,
            filters=filters,
            search=search
        )
        
        # レスポンス形式に変換
        contact_items = []
        for contact in contacts:
            contact_items.append(ContactListItem(
                id=contact.id,
                name=contact.name,
                email=str(contact.email),
                phone=contact.phone,
                lesson_type=contact.lesson_type,
                preferred_contact=contact.preferred_contact,
                status=contact.status,
                submitted_at=contact.submitted_at.isoformat() if contact.submitted_at else "",
                updated_at=contact.updated_at.isoformat() if contact.updated_at else None
            ))
        
        total_pages = (total + per_page - 1) // per_page
        
        return ContactListResponse(
            contacts=contact_items,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"問い合わせ一覧の取得に失敗しました: {str(e)}"
        )

@router.get("/{contact_id}", response_model=ContactDetail)
async def get_contact_detail(
    contact_id: str,
    admin: Admin = Depends(require_admin_or_staff),
    contact_repo: ContactRepository = Depends(get_contact_repository)
):
    """問い合わせ詳細を取得"""
    contact = await contact_repo.find_by_id(contact_id)
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="問い合わせが見つかりません"
        )
    
    return ContactDetail(
        id=contact.id,
        name=contact.name,
        email=str(contact.email),
        phone=contact.phone,
        message=contact.message,
        lesson_type=contact.lesson_type,
        preferred_contact=contact.preferred_contact,
        status=contact.status,
        submitted_at=contact.submitted_at.isoformat() if contact.submitted_at else "",
        updated_at=contact.updated_at.isoformat() if contact.updated_at else None,
        admin_notes=getattr(contact, 'admin_notes', None)
    )

@router.put("/{contact_id}/status", response_model=ContactStatusResponse)
async def update_contact_status(
    contact_id: str,
    request: UpdateContactStatusRequest,
    admin: Admin = Depends(require_admin_or_staff),
    contact_repo: ContactRepository = Depends(get_contact_repository)
):
    """問い合わせのステータスを更新"""
    # 有効なステータスをチェック
    valid_statuses = ["pending", "in_progress", "responded", "closed"]
    if request.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"無効なステータスです。有効な値: {', '.join(valid_statuses)}"
        )
    
    contact = await contact_repo.find_by_id(contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="問い合わせが見つかりません"
        )
    
    try:
        # ステータスを更新
        updated_contact = await contact_repo.update_status(
            contact_id=contact_id,
            status=request.status,
            admin_notes=request.admin_notes,
            updated_by=admin.id
        )
        
        return ContactStatusResponse(
            message=f"問い合わせのステータスを「{request.status}」に更新しました"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ステータスの更新に失敗しました: {str(e)}"
        )

@router.get("/stats/summary")
async def get_contact_stats(
    admin: Admin = Depends(require_admin_or_staff),
    contact_repo: ContactRepository = Depends(get_contact_repository)
):
    """問い合わせ統計情報を取得"""
    try:
        stats = await contact_repo.get_status_stats()
        
        return {
            "total": stats.get("total", 0),
            "pending": stats.get("pending", 0),
            "in_progress": stats.get("in_progress", 0),
            "responded": stats.get("responded", 0),
            "closed": stats.get("closed", 0),
            "today": stats.get("today", 0),
            "this_week": stats.get("this_week", 0),
            "this_month": stats.get("this_month", 0)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"統計情報の取得に失敗しました: {str(e)}"
        )

@router.delete("/{contact_id}")
async def delete_contact(
    contact_id: str,
    admin: Admin = Depends(require_admin_or_staff),
    contact_repo: ContactRepository = Depends(get_contact_repository)
):
    """問い合わせを削除（管理者のみ）"""
    if admin.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="管理者権限が必要です"
        )
    
    contact = await contact_repo.find_by_id(contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="問い合わせが見つかりません"
        )
    
    try:
        await contact_repo.delete(contact_id)
        return {"message": "問い合わせを削除しました"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"問い合わせの削除に失敗しました: {str(e)}"
        )