from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
import os
import dotenv

dotenv.load_dotenv()

url: str = os.environ.get("SUPABASE_URL")

key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

adminkey: str = os.environ.get("SUPABASE_ADMIN_KEY")
adminsupabase: Client = create_client(url, adminkey)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
):
    try:
        user = supabase.auth.get_user(credentials.credentials)
        return user.user

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
