#!/usr/bin/env python3
"""Test script to understand Stripe session structure"""

import stripe
from config import Config

# Set API key
stripe.api_key = Config.STRIPE_SECRET_KEY

print("Testing Stripe Checkout Session structure...")
print("=" * 60)

# Get a recent checkout session
try:
    sessions = stripe.checkout.Session.list(limit=1)
    if sessions.data:
        session = sessions.data[0]
        print(f"\nFound session: {session.id}")
        print(f"Payment status: {session.payment_status}")
        print(f"Customer (direct): {session.customer}")
        print(f"Customer (dict): {session.get('customer')}")
        print(f"Subscription: {session.subscription}")
        print(f"Mode: {session.mode}")
        print(f"Customer email: {session.customer_email}")
        print(f"\nFull session object keys: {list(session.keys()) if hasattr(session, 'keys') else 'N/A'}")
        
        # Try to get subscription and customer from it
        if session.subscription:
            try:
                sub = stripe.Subscription.retrieve(session.subscription)
                print(f"\nSubscription customer: {sub.customer}")
                print(f"Subscription status: {sub.status}")
            except Exception as e:
                print(f"\nError retrieving subscription: {e}")
    else:
        print("No checkout sessions found")
        print("\nYou need to create a checkout session first to test this.")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)

