from typing import Generator, Optional
from sqlalchemy.orm import Session
from app.clientsdatabase_clients.db_base_client import BaseDatabaseClient
from supabase import create_client, Client 

class SupabaseClient(BaseDatabaseClient):
    """Supabase PostgreSQL database client with Storage support"""
    
    def __init__(
        self, 
        connection_string: str, 
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None,
        **kwargs
    ):
        super().__init__(connection_string, **kwargs)
        self.db_type = "supabase"
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        
        # --- التعديل السحري هنا ---
        # بنفتح الـ SDK الرسمي ونخزنه جوه attribute اسمه storage
        if supabase_url and supabase_key:
            self._sdk: Client = create_client(supabase_url, supabase_key)
            self.storage = self._sdk.storage 
        else:
            self.storage = None
            print("⚠️ Warning: Supabase URL or Key missing. Storage will not work.")

    def get_session(self) -> Generator[Session, None, None]:
        """Get Supabase database session"""
        db = self.SessionLocal()
        try:
            yield db
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def __repr__(self):
        return f"SupabaseClient(url='{self.supabase_url}')"