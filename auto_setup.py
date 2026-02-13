"""
Auto Setup - Tao bang app_users va tai khoan admin mac dinh
Chay: python -X utf8 auto_setup.py
"""

import hashlib
import secrets
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

HEADERS = {
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
    "Content-Type": "application/json",
}


def hash_password(password: str) -> tuple:
    salt = secrets.token_hex(16)
    pw_hash = hashlib.sha256((salt + password).encode()).hexdigest()
    return pw_hash, salt


def create_app_users_table():
    """Tao bang app_users (neu chua co)."""
    print("\n[1] Tao bang app_users...")

    sql = """
    CREATE TABLE IF NOT EXISTS public.app_users (
        id BIGSERIAL PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        display_name TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('admin', 'user')),
        created_at TIMESTAMPTZ DEFAULT NOW()
    );

    ALTER TABLE public.app_users ENABLE ROW LEVEL SECURITY;

    DROP POLICY IF EXISTS "Service role full access app_users" ON public.app_users;
    CREATE POLICY "Service role full access app_users"
        ON public.app_users FOR ALL
        USING (true)
        WITH CHECK (true);
    """

    # Try using the SQL exec RPC if available
    url = f"{SUPABASE_URL}/rest/v1/rpc/exec_sql"
    resp = httpx.post(url, headers=HEADERS, json={"query": sql}, timeout=30)

    if resp.status_code in (200, 201, 204):
        print("  -> Bang app_users da tao thanh cong!")
        return True

    # If RPC not available, check if table already exists
    check_url = f"{SUPABASE_URL}/rest/v1/app_users?select=id&limit=1"
    resp2 = httpx.get(check_url, headers=HEADERS, timeout=10)
    if resp2.status_code == 200:
        print("  -> Bang app_users da ton tai!")
        return True

    print("  -> KHONG THE TAO BANG TU DONG!")
    print("  -> Vui long chay SQL sau trong Supabase Dashboard > SQL Editor:")
    print()
    print(sql)
    return False


def create_user(username: str, password: str, display_name: str, role: str):
    """Tao tai khoan."""
    print(f"\n  Tao: {username} ({role})...")

    # Check neu da ton tai
    check_url = f"{SUPABASE_URL}/rest/v1/app_users?username=eq.{username}&select=id"
    resp = httpx.get(check_url, headers=HEADERS, timeout=10)
    if resp.status_code == 200 and resp.json():
        print(f"    -> '{username}' da ton tai, bo qua.")
        return True

    pw_hash, salt = hash_password(password)
    payload = {
        "username": username,
        "display_name": display_name,
        "password_hash": pw_hash,
        "salt": salt,
        "role": role,
    }

    url = f"{SUPABASE_URL}/rest/v1/app_users"
    insert_headers = {**HEADERS, "Prefer": "return=representation"}
    resp = httpx.post(url, headers=insert_headers, json=payload, timeout=10)

    if resp.status_code in (200, 201):
        print(f"    -> Tao thanh cong!")
        return True
    else:
        print(f"    -> LOI: {resp.status_code} - {resp.text}")
        return False


def verify():
    """Kiem tra."""
    print("\n[3] Kiem tra ket qua...")
    url = f"{SUPABASE_URL}/rest/v1/app_users?select=username,display_name,role"
    resp = httpx.get(url, headers=HEADERS, timeout=10)

    if resp.status_code == 200:
        users = resp.json()
        print(f"  Tong: {len(users)} tai khoan")
        for u in users:
            icon = "[ADMIN]" if u["role"] == "admin" else "[USER]"
            print(f"    {icon} {u['username']} - {u['display_name']}")
    else:
        print(f"  LOI: {resp.status_code}")


def main():
    print("=" * 50)
    print("  Tra Cuu Gia Thuoc - Auto Setup")
    print("=" * 50)
    print(f"  URL: {SUPABASE_URL}")

    if not SUPABASE_URL or not SERVICE_KEY:
        print("  LOI: Thieu SUPABASE_URL hoac SUPABASE_SERVICE_ROLE_KEY!")
        return

    # Step 1: Create table
    if not create_app_users_table():
        return

    # Step 2: Create default accounts
    print("\n[2] Tao tai khoan mac dinh...")
    create_user("admin", "123456", "Admin", "admin")
    create_user("user", "123456", "Nguoi dung", "user")

    # Step 3: Verify
    verify()

    print("\n" + "=" * 50)
    print("  HOAN TAT!")
    print("=" * 50)
    print("\n  Dang nhap:")
    print("  Admin: admin / 123456")
    print("  User:  user  / 123456")
    print("\n  Chay app: python main.py")


if __name__ == "__main__":
    main()
