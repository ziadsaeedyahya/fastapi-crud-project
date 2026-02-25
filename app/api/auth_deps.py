import uuid
from enum import Enum  
from fastapi import Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import cast 
from sqlalchemy.dialects.postgresql import UUID 
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.clientsdatabase_clients import postgres_client, supabase_client
from app.core.security import verify_token
from app.models.user_model import User

security = HTTPBearer()

# 1. تعريف القائمة خيارات الاختيار (Dropdown)
class DBSource(str, Enum):
    postgres = "postgres"
    supabase = "supabase"

# 2. تعديل الدالة لتستخدم الـ Enum
def get_auth_db(
    db_source: DBSource = Query(DBSource.postgres, description="Select database: postgres or supabase")
):
    # نستخدم .value عشان نأخذ النص (postgres أو supabase)
    source = db_source.value
    
    if source == "supabase":
        db = next(supabase_client.get_session())
    else:
        db = next(postgres_client.get_session())
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_auth_db)
) -> User:
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials or user not found in selected database",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    user_id_raw = verify_token(token)
    if user_id_raw is None:
        raise credentials_exception
    
    try:
        user_id = uuid.UUID(str(user_id_raw))
    except (ValueError, AttributeError):
        raise credentials_exception
    
    # الـ cast اللي صلح المشكلة لسه موجود زي ما هو
    user = db.query(User).filter(cast(User.id, UUID) == user_id).first()
    
    if user is None:
        raise credentials_exception
    
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user