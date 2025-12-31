#!/usr/bin/env python3
"""Test script to debug Supabase configuration"""

from config import Config
from supabase_client import supabase_service

print("=" * 60)
print("Supabase Configuration Test")
print("=" * 60)

print(f"\n1. Checking Config values:")
print(f"   SUPABASE_URL: {Config.SUPABASE_URL[:60] if Config.SUPABASE_URL else 'NOT SET'}...")
print(f"   SUPABASE_KEY: {len(Config.SUPABASE_KEY) if Config.SUPABASE_KEY else 'NOT SET'} characters")
print(f"   SUPABASE_KEY starts with 'your_': {Config.SUPABASE_KEY.startswith('your_') if Config.SUPABASE_KEY else 'N/A'}")

print(f"\n2. Checking validation:")
has_valid_url = Config.SUPABASE_URL and Config.SUPABASE_URL.startswith('http')
has_valid_key = Config.SUPABASE_KEY and not Config.SUPABASE_KEY.startswith('your_')
print(f"   URL is valid: {has_valid_url}")
print(f"   KEY is valid: {has_valid_key}")

print(f"\n3. Checking SupabaseService:")
print(f"   is_configured(): {supabase_service.is_configured()}")
print(f"   client is None: {supabase_service.client is None}")

if not supabase_service.is_configured():
    print(f"\n4. Testing client creation directly:")
    try:
        from supabase import create_client
        print("   Import successful")
        print(f"   Trying to create client with URL: {Config.SUPABASE_URL}")
        print(f"   Key length: {len(Config.SUPABASE_KEY)}")
        client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
        print("   ✅ Client created successfully!")
        print(f"   Client type: {type(client)}")
    except Exception as e:
        print(f"   ❌ ERROR creating client: {e}")
        import traceback
        print(f"\n   Full traceback:")
        traceback.print_exc()
else:
    print(f"\n4. Supabase is configured! ✅")

print("\n" + "=" * 60)

