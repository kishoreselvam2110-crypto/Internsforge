from supabase import create_client, Client, ClientOptions

from ..config import settings

def get_supabase_client(jwt: str = None) -> Client:
    """
    Creates a Supabase client. If a JWT token is passed, it sets it on the client
    so that Row Level Security (RLS) policies are applied in the database.
    """
    options = ClientOptions(headers={"Authorization": f"Bearer {jwt}"}) if jwt else None
    client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY, options=options)
        
    return client

def get_supabase_admin_client() -> Client:
    """
    Creates a Supabase client using the Service Role Key.
    This client bypasses RLS and should be used only for internal, trusted operations.
    """
    if not settings.SUPABASE_SERVICE_ROLE_KEY:
        raise ValueError("SUPABASE_SERVICE_ROLE_KEY environment variable is not set.")
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
