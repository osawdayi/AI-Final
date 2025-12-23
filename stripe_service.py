"""
Stripe service for payment processing
"""
import stripe
from config import Config
from typing import Optional, Dict
from supabase_client import supabase_service

class StripeService:
    """Service class for Stripe operations"""
    
    def __init__(self):
        if Config.STRIPE_SECRET_KEY:
            stripe.api_key = Config.STRIPE_SECRET_KEY
            self.configured = True
        else:
            self.configured = False
    
    def is_configured(self) -> bool:
        """Check if Stripe is configured"""
        return self.configured
    
    def create_checkout_session(self, user_id: str, user_email: str, base_url: str = 'http://localhost:5000') -> Optional[Dict]:
        """Create Stripe checkout session for premium subscription"""
        if not self.is_configured() or not Config.PREMIUM_PRICE_ID:
            return None
        
        try:
            checkout_session = stripe.checkout.Session.create(
                customer_email=user_email,
                payment_method_types=['card'],
                line_items=[{
                    'price': Config.PREMIUM_PRICE_ID,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=f'{base_url}/payment/success?session_id={{CHECKOUT_SESSION_ID}}',
                cancel_url=f'{base_url}/payment/cancel',
                metadata={
                    'user_id': user_id
                }
            )
            
            return {
                'session_id': checkout_session.id,
                'url': checkout_session.url
            }
        except Exception as e:
            print(f"Error creating checkout session: {e}")
            return None
    
    def create_customer_portal_session(self, customer_id: str, return_url: str = 'http://localhost:5000/dashboard') -> Optional[str]:
        """Create Stripe customer portal session for managing subscription"""
        if not self.is_configured():
            return None
        
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url,
            )
            return session.url
        except Exception as e:
            print(f"Error creating portal session: {e}")
            return None
    
    def handle_webhook(self, payload: bytes, sig_header: str) -> Optional[Dict]:
        """Handle Stripe webhook events"""
        if not self.is_configured() or not Config.STRIPE_WEBHOOK_SECRET:
            return None
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, Config.STRIPE_WEBHOOK_SECRET
            )
            
            # Handle the event
            if event['type'] == 'checkout.session.completed':
                session = event['data']['object']
                user_id = session.get('metadata', {}).get('user_id')
                customer_id = session.get('customer')
                
                # Update user profile with Stripe customer ID
                if user_id and customer_id:
                    supabase_service.update_user_profile(user_id, {
                        'stripe_customer_id': customer_id,
                        'subscription_tier': 'premium'
                    })
            
            elif event['type'] == 'customer.subscription.created':
                subscription = event['data']['object']
                customer_id = subscription.get('customer')
                
                # Get user_id from customer metadata or lookup
                customer = stripe.Customer.retrieve(customer_id)
                user_id = customer.metadata.get('user_id')
                
                if user_id:
                    supabase_service.create_subscription(
                        user_id=user_id,
                        stripe_subscription_id=subscription['id'],
                        stripe_price_id=subscription['items']['data'][0]['price']['id'],
                        status=subscription['status'],
                        period_start=subscription['current_period_start'],
                        period_end=subscription['current_period_end']
                    )
                    
                    supabase_service.update_user_profile(user_id, {
                        'subscription_tier': 'premium'
                    })
            
            elif event['type'] == 'customer.subscription.updated':
                subscription = event['data']['object']
                updates = {
                    'status': subscription['status'],
                    'current_period_start': subscription['current_period_start'],
                    'current_period_end': subscription['current_period_end'],
                    'cancel_at_period_end': subscription.get('cancel_at_period_end', False)
                }
                
                supabase_service.update_subscription(
                    subscription['id'],
                    updates
                )
                
                # Update subscription tier if canceled or past_due
                if subscription['status'] in ['canceled', 'past_due', 'incomplete']:
                    # Get subscription to find user_id
                    if supabase_service.is_configured():
                        sub_data = supabase_service.client.table('subscriptions').select('user_id').eq('stripe_subscription_id', subscription['id']).execute()
                        if sub_data.data and len(sub_data.data) > 0:
                            user_id = sub_data.data[0]['user_id']
                            supabase_service.update_user_profile(user_id, {
                                'subscription_tier': 'free'
                            })
            
            elif event['type'] == 'customer.subscription.deleted':
                subscription = event['data']['object']
                updates = {
                    'status': 'canceled'
                }
                supabase_service.update_subscription(
                    subscription['id'],
                    updates
                )
                
                # Update user tier to free
                if supabase_service.is_configured():
                    sub_data = supabase_service.client.table('subscriptions').select('user_id').eq('stripe_subscription_id', subscription['id']).execute()
                    if sub_data.data and len(sub_data.data) > 0:
                        user_id = sub_data.data[0]['user_id']
                        supabase_service.update_user_profile(user_id, {
                            'subscription_tier': 'free'
                        })
            
            return {'status': 'success'}
        except ValueError as e:
            print(f"Invalid payload: {e}")
            return None
        except stripe.error.SignatureVerificationError as e:
            print(f"Invalid signature: {e}")
            return None
        except Exception as e:
            print(f"Error handling webhook: {e}")
            return None

# Global instance
stripe_service = StripeService()

