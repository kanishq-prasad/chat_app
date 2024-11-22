from database.db import safe_session, db
from sqlalchemy.exc import SQLAlchemyError

class BaseRepository:
    @classmethod
    def save_in_db(cls, item, raise_on_fail=True, commit=True):
        """
        Base method to save any model instance to the database.
        
        Args:
            item: The model instance to save
            raise_on_fail (bool): Whether to raise exceptions on failure
            commit (bool): Whether to commit the transaction immediately
        
        Returns:
            The saved item if successful, None if failed and raise_on_fail is False
        
        Raises:
            SQLAlchemyError: If database operation fails and raise_on_fail is True
        """
        try:
            with safe_session() as session:
                session.add(item)
                
                if commit:
                    session.commit()
                    session.refresh(item)  # Refresh to get any DB-generated values
                
                return item
                
        except SQLAlchemyError as e:
            if raise_on_fail:
                raise e
            return None

    @classmethod
    def bulk_save_in_db(cls, items, raise_on_fail=True):
        """
        Saves multiple items in a single transaction.
        
        Args:
            items: List of model instances to save
            raise_on_fail (bool): Whether to raise exceptions on failure
        
        Returns:
            List of saved items if successful, None if failed and raise_on_fail is False
        """
        try:
            with safe_session() as session:
                session.bulk_save_objects(items)
                session.commit()
                return items
                
        except SQLAlchemyError as e:
            if raise_on_fail:
                raise e
            return None