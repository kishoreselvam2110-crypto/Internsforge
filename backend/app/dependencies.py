from fastapi import Header, HTTPException, Depends
from typing import Optional
from app.services.supabase import get_supabase_client
from supabase import Client

def get_auth_token(authorization: Optional[str] = Header(None)) -> str:
    """
    Extracts the Bearer token from the Authorization header.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header is missing.")
        
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization header format. Expected 'Bearer <token>'.")
        
    return parts[1]

def get_db_client(token: str = Depends(get_auth_token)) -> Client:
    """
    Dependency that returns an authenticated Supabase client for database operations.
    """
    try:
        return get_supabase_client(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Failed to authenticate with Supabase: {str(e)}")

def get_user_id_from_token(token: str = Depends(get_auth_token)):
    """
    Retrieves the user UUID from the Supabase JWT token.
    Returns None when using service-role / anon key (E2E / dev mode).
    """
    try:
        from app.config import settings
        # Admin or anon key → bypass auth, user_id will be NULL (allowed by schema)
        if token in (settings.SUPABASE_SERVICE_ROLE_KEY, settings.SUPABASE_ANON_KEY):
            return None

        client = get_supabase_client(token)
        user_response = client.auth.get_user(token)
        if not user_response or not user_response.user:
            raise HTTPException(status_code=401, detail="Invalid token. Could not retrieve user profile.")
        return user_response.user.id
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication check failed: {str(e)}")
