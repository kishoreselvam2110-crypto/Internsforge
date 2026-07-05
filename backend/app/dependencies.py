from fastapi import Header, HTTPException, Depends
from typing import Optional
from supabase import Client

from .config import settings
from .services.supabase import get_supabase_admin_client, get_supabase_client

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
    Dependency that returns a Supabase client for database operations.
    Uses admin client for service or anon tokens in prototype mode.
    """
    try:
        if token in (settings.SUPABASE_SERVICE_ROLE_KEY, settings.SUPABASE_ANON_KEY):
            return get_supabase_admin_client()
        return get_supabase_client(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Failed to authenticate with Supabase: {str(e)}")

def get_user_id_from_token(token: str = Depends(get_auth_token)):
    """
    Retrieves the user UUID from the Supabase JWT token.
    Falls back to a configured default user ID when using anon/service role keys.
    """
    try:
        if token in (settings.SUPABASE_SERVICE_ROLE_KEY, settings.SUPABASE_ANON_KEY):
            if not settings.SUPABASE_DEFAULT_USER_ID:
                raise HTTPException(
                    status_code=401,
                    detail="SUPABASE_DEFAULT_USER_ID must be set when using anon/service role tokens."
                )
            return settings.SUPABASE_DEFAULT_USER_ID

        client = get_supabase_client(token)
        user_response = client.auth.get_user(token)
        if not user_response or not user_response.user:
            raise HTTPException(status_code=401, detail="Invalid token. Could not retrieve user profile.")
        return user_response.user.id
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication check failed: {str(e)}")
