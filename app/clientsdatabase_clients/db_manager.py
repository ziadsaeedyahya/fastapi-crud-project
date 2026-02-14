from app.core.config import settings
from app.clientsdatabase_clients.postgres_client import PostgresClient
from app.clientsdatabase_clients.supabase_client import SupabaseClient

# Initialize database clients
postgres_client = PostgresClient(
    connection_string=settings.DATABASE_URL,
    pool_size=5
)

supabase_client = SupabaseClient(
    connection_string=settings.SUPABASE_DB_URL,
    supabase_url=settings.SUPABASE_URL,
    supabase_key=settings.SUPABASE_KEY,
    pool_size=5
)

# Dependency injection functions
def get_postgres_db():
    """Dependency for PostgreSQL database session"""
    yield from postgres_client.get_session()


def get_supabase_db():
    """Dependency for Supabase database session"""
    yield from supabase_client.get_session()


def get_db_by_source(db_source: str = "postgres"):
    """دالة بتختار الداتا بيز بناءً على النوع اللي بنبعته لها"""
    if db_source == "supabase":
        yield from supabase_client.get_session()
    else:
        yield from postgres_client.get_session()

get_db = get_postgres_db       

# Cleanup function (optional - for app shutdown)
def close_all_connections():
    """Close all database connections"""
    postgres_client.close()
    supabase_client.close()