#!/usr/bin/env python3
"""Test script to debug Stripe configuration"""

from config import Config
from stripe_service import stripe_service

print("=" * 60)
print("Stripe Configuration Test")
print("=" * 60)

print(f"\n1. Checking Config values:")
print(f"   STRIPE_SECRET_KEY set: {bool(Config.STRIPE_SECRET_KEY)}")
if Config.STRIPE_SECRET_KEY:
    print(f"   STRIPE_SECRET_KEY length: {len(Config.STRIPE_SECRET_KEY)}")
    print(f"   STRIPE_SECRET_KEY first 10 chars: {Config.STRIPE_SECRET_KEY[:10]}...")
    print(f"   Starts with 'sk_test' or 'sk_live': {Config.STRIPE_SECRET_KEY.startswith(('sk_test', 'sk_live'))}")
    print(f"   Contains 'your_': {'your_' in Config.STRIPE_SECRET_KEY}")

print(f"   STRIPE_PREMIUM_PRICE_ID set: {bool(Config.PREMIUM_PRICE_ID)}")
if Config.PREMIUM_PRICE_ID:
    print(f"   STRIPE_PREMIUM_PRICE_ID value: {Config.PREMIUM_PRICE_ID[:30]}...")
    print(f"   Starts with 'price_': {Config.PREMIUM_PRICE_ID.startswith('price_')}")

print(f"\n2. Checking StripeService:")
print(f"   is_configured(): {stripe_service.is_configured()}")
print(f"   configured flag: {stripe_service.configured}")

print(f"\n3. Testing Stripe module:")
try:
    import stripe
    print(f"   ✅ Stripe module imported successfully")
    print(f"   Stripe version: {stripe.__version__ if hasattr(stripe, '__version__') else 'unknown'}")
    print(f"   stripe.api_key set: {bool(stripe.api_key)}")
    if stripe.api_key:
        print(f"   stripe.api_key starts with 'sk': {stripe.api_key.startswith('sk')}")
    
    # Test if checkout is available
    if hasattr(stripe, 'checkout'):
        print(f"   ✅ stripe.checkout available")
        if hasattr(stripe.checkout, 'Session'):
            print(f"   ✅ stripe.checkout.Session available")
        else:
            print(f"   ❌ stripe.checkout.Session NOT available")
    else:
        print(f"   ❌ stripe.checkout NOT available")
        
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)

