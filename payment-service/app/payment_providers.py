import asyncio

# async def process_payfast_payment(order_id: int, amount: float, currency: str) -> bool:
#     """
#     Mock function to process payment via PayFast.
#     Replace with actual PayFast API integration.
#     """
#     await asyncio.sleep(2)  # Simulate network delay
#     print(f"Processed PayFast payment for order_id: {order_id}")
#     return True

async def process_stripe_payment(order_id: int, amount: float, currency: str) -> bool:
    """
    Mock function to process payment via Stripe.
    Replace with actual Stripe API integration.
    """
    await asyncio.sleep(2)  # Simulate network delay
    print(f"Processed Stripe payment for order_id: {order_id}")
    return True
