"""SQLAlchemy implementation of Contact repository."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.entities.contact import Contact
from ...domain.repositories.contact_repository import ContactRepository
from ...domain.value_objects.email import Email
from ...domain.value_objects.phone import Phone
from ..database.models.contact import ContactModel


class SQLAlchemyContactRepository(ContactRepository):
    """SQLAlchemy implementation of ContactRepository."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session.
        
        Args:
            session: SQLAlchemy async session
        """
        self._session = session

    async def save(self, contact: Contact) -> Contact:
        """Save a contact entity to database.
        
        Args:
            contact: The contact entity to save
            
        Returns:
            The saved contact entity with updated fields
        """
        # Check if contact already exists
        existing = await self._session.get(ContactModel, contact.id)
        
        if existing:
            # Update existing contact
            existing.name = contact.name
            existing.email = contact.email.value
            existing.phone = contact.phone.value if contact.phone else None
            existing.message = contact.message
            existing.lesson_type = contact.lesson_type.value
            existing.preferred_contact = contact.preferred_contact.value
            existing.status = contact.status.value
            existing.updated_at = contact.updated_at
            existing.processed_at = contact.processed_at
            existing.processed_by = contact.processed_by
            existing.processing_notes = contact.processing_notes
            contact_model = existing
        else:
            # Create new contact
            contact_model = ContactModel(
                id=contact.id,
                name=contact.name,
                email=contact.email.value,
                phone=contact.phone.value if contact.phone else None,
                message=contact.message,
                lesson_type=contact.lesson_type.value,
                preferred_contact=contact.preferred_contact.value,
                status=contact.status.value,
                created_at=contact.created_at,
                updated_at=contact.updated_at,
                processed_at=contact.processed_at,
                processed_by=contact.processed_by,
                processing_notes=contact.processing_notes
            )
            self._session.add(contact_model)
        
        await self._session.flush()
        await self._session.refresh(contact_model)
        return self._model_to_entity(contact_model)

    async def find_by_id(self, contact_id: UUID) -> Optional[Contact]:
        """Find a contact by its ID."""
        contact_model = await self._session.get(ContactModel, contact_id)
        return self._model_to_entity(contact_model) if contact_model else None

    async def find_by_email(self, email: str) -> Optional[Contact]:
        """Find a contact by email address."""
        stmt = select(ContactModel).where(ContactModel.email == email)
        result = await self._session.execute(stmt)
        contact_model = result.scalar_one_or_none()
        return self._model_to_entity(contact_model) if contact_model else None

    async def find_all(self, limit: int = 100, offset: int = 0) -> List[Contact]:
        """Find all contacts with pagination."""
        stmt = (
            select(ContactModel)
            .order_by(ContactModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        contact_models = result.scalars().all()
        return [self._model_to_entity(model) for model in contact_models]

    async def delete(self, contact_id: UUID) -> bool:
        """Delete a contact by its ID."""
        contact_model = await self._session.get(ContactModel, contact_id)
        if contact_model:
            await self._session.delete(contact_model)
            return True
        return False

    async def count(self) -> int:
        """Count total number of contacts."""
        stmt = select(func.count(ContactModel.id))
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def find_with_pagination(self, page: int = 1, per_page: int = 20, filters: dict = None, search: str = None):
        """Find contacts with pagination and filters."""
        from sqlalchemy import and_, or_
        
        # Base query
        stmt = select(ContactModel)
        count_stmt = select(func.count(ContactModel.id))
        
        # Apply filters
        conditions = []
        if filters:
            if "status" in filters:
                conditions.append(ContactModel.status == filters["status"])
        
        # Apply search
        if search:
            search_conditions = or_(
                ContactModel.name.ilike(f"%{search}%"),
                ContactModel.email.ilike(f"%{search}%")
            )
            conditions.append(search_conditions)
        
        if conditions:
            stmt = stmt.where(and_(*conditions))
            count_stmt = count_stmt.where(and_(*conditions))
        
        # Get total count
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar() or 0
        
        # Apply pagination and ordering
        offset = (page - 1) * per_page
        stmt = stmt.order_by(ContactModel.created_at.desc()).limit(per_page).offset(offset)
        
        # Execute query
        result = await self._session.execute(stmt)
        contact_models = result.scalars().all()
        
        contacts = [self._model_to_entity(model) for model in contact_models]
        return contacts, total

    async def update_status(self, contact_id: UUID, status: str, admin_notes: str = None, updated_by: str = None):
        """Update contact status and admin notes."""
        contact_model = await self._session.get(ContactModel, contact_id)
        if not contact_model:
            return None
        
        contact_model.status = status
        if admin_notes:
            contact_model.processing_notes = admin_notes
        if updated_by:
            contact_model.processed_by = updated_by
        
        from datetime import datetime
        contact_model.updated_at = datetime.now()
        if status in ["responded", "closed"]:
            contact_model.processed_at = datetime.now()
        
        await self._session.flush()
        await self._session.refresh(contact_model)
        return self._model_to_entity(contact_model)

    async def get_status_stats(self):
        """Get contact statistics by status."""
        from sqlalchemy import case
        from datetime import datetime, timedelta
        
        # Status counts
        status_stmt = select(
            func.count(ContactModel.id).label("total"),
            func.sum(case((ContactModel.status == "pending", 1), else_=0)).label("pending"),
            func.sum(case((ContactModel.status == "in_progress", 1), else_=0)).label("in_progress"),
            func.sum(case((ContactModel.status == "responded", 1), else_=0)).label("responded"),
            func.sum(case((ContactModel.status == "closed", 1), else_=0)).label("closed")
        )
        
        status_result = await self._session.execute(status_stmt)
        status_row = status_result.first()
        
        # Time-based counts
        now = datetime.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)
        
        time_stmt = select(
            func.sum(case((ContactModel.created_at >= today, 1), else_=0)).label("today"),
            func.sum(case((ContactModel.created_at >= week_start, 1), else_=0)).label("this_week"),
            func.sum(case((ContactModel.created_at >= month_start, 1), else_=0)).label("this_month")
        )
        
        time_result = await self._session.execute(time_stmt)
        time_row = time_result.first()
        
        return {
            "total": status_row.total or 0,
            "pending": status_row.pending or 0,
            "in_progress": status_row.in_progress or 0,
            "responded": status_row.responded or 0,
            "closed": status_row.closed or 0,
            "today": time_row.today or 0,
            "this_week": time_row.this_week or 0,
            "this_month": time_row.this_month or 0
        }

    def _model_to_entity(self, model: ContactModel) -> Contact:
        """Convert ContactModel to Contact entity."""
        from ...domain.entities.contact import LessonType, PreferredContact, ContactStatus
        
        phone = Phone(model.phone) if model.phone else None
        
        contact = Contact(
            id=model.id,
            name=model.name,
            email=Email(model.email),
            phone=phone,
            message=model.message,
            lesson_type=LessonType(model.lesson_type),
            preferred_contact=PreferredContact(model.preferred_contact),
            status=ContactStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
            processed_at=model.processed_at,
            processed_by=model.processed_by,
            processing_notes=model.processing_notes
        )
        
        return contact