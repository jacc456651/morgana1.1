import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()


def get_supabase() -> Client:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_ANON_KEY")
    if not url:
        raise ValueError("SUPABASE_URL es requerida en .env")
    if not key:
        raise ValueError("SUPABASE_ANON_KEY es requerida en .env")
    return create_client(url, key)
