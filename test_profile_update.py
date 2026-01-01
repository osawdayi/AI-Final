#!/usr/bin/env python3
"""Test profile update functionality"""

from supabase_client import supabase_service
from config import Config

# Get a test user ID (you'll need to replace this with an actual user ID)
# For testing, let's try to get the first profile
print("Testing profile update...")

try:
    # Get first profile to test update
    result = supabase_service.client.table('profiles').select('id, email, subscription_tier').limit(1).execute()
    
    if result.data and len(result.data) > 0:
        test_user_id = result.data[0]['id']
        current_tier = result.data[0].get('subscription_tier', 'free')
        print(f"\nFound test user:")
        print(f"  ID: {test_user_id}")
        print(f"  Email: {result.data[0].get('email', 'N/A')}")
        print(f"  Current tier: {current_tier}")
        
        # Test update
        print(f"\nAttempting to update subscription_tier to 'premium'...")
        update_success = supabase_service.update_user_profile(test_user_id, {
            'subscription_tier': 'premium'
        })
        
        if update_success:
            print("✅ Update call returned True")
            
            # Verify the update
            verify_result = supabase_service.client.table('profiles').select('subscription_tier').eq('id', test_user_id).execute()
            if verify_result.data:
                updated_tier = verify_result.data[0].get('subscription_tier')
                print(f"✅ Verified: subscription_tier is now '{updated_tier}'")
                
                if updated_tier == 'premium':
                    print("✅ SUCCESS: Database was updated correctly!")
                else:
                    print(f"❌ ERROR: Database shows '{updated_tier}' instead of 'premium'")
            else:
                print("❌ ERROR: Could not verify update - profile not found")
        else:
            print("❌ Update call returned False")
    else:
        print("No profiles found in database")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

