#!/usr/bin/env python3
"""Script to manually fix customer IDs for users who already paid"""

import stripe
from config import Config
from supabase_client import supabase_service

stripe.api_key = Config.STRIPE_SECRET_KEY

print("Fixing customer IDs for existing premium users...")
print("=" * 60)

try:
    # Get all premium users without customer IDs
    profiles = supabase_service.client.table('profiles').select('*').eq('subscription_tier', 'premium').execute()
    
    if not profiles.data:
        print("No premium users found")
    else:
        print(f"\nFound {len(profiles.data)} premium user(s)")
        
        for profile in profiles.data:
            user_id = profile['id']
            email = profile.get('email')
            current_customer_id = profile.get('stripe_customer_id')
            
            print(f"\nProcessing user: {email}")
            print(f"  Current customer_id: {current_customer_id}")
            
            if current_customer_id:
                print(f"  ✅ Already has customer ID, skipping")
                continue
            
            if not email:
                print(f"  ❌ No email found, skipping")
                continue
            
            # Try to find customer by email
            try:
                customers = stripe.Customer.list(email=email, limit=1)
                if customers.data:
                    customer_id = customers.data[0].id
                    print(f"  Found customer ID: {customer_id}")
                    
                    # Update profile
                    update_result = supabase_service.update_user_profile(user_id, {
                        'stripe_customer_id': customer_id
                    })
                    
                    if update_result:
                        print(f"  ✅ Updated profile with customer ID")
                    else:
                        print(f"  ❌ Failed to update profile")
                else:
                    print(f"  ❌ No Stripe customer found for email: {email}")
            except Exception as e:
                print(f"  ❌ Error: {e}")
                
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Done!")

