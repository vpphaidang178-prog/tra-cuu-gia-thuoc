
from auth.supabase_client import SupabaseAuth
import sys

def test_login():
    auth = SupabaseAuth()
    print(f"Testing login with URL: {auth.supabase_url}")
    
    username = "admin"
    password = "123456"
    
    success, message, user_data = auth.login(username, password)
    
    if success:
        print(f"SUCCESS: Login successful for {username}")
        print(f"User Data: {user_data}")
    else:
        print(f"FAILED: {message}")

if __name__ == "__main__":
    test_login()
