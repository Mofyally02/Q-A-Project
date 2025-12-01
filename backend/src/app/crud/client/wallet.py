"""
Client wallet CRUD operations
"""

from typing import Dict, Any, Optional
import asyncpg
from uuid import UUID
from datetime import datetime
import json


async def get_wallet_info(
    db: asyncpg.Connection,
    user_id: UUID
) -> Dict[str, Any]:
    """Get wallet information"""
    user = await db.fetchrow("""
        SELECT credits, created_at
        FROM users
        WHERE id = $1
    """, user_id)
    
    if not user:
        raise ValueError("User not found")
    
    credits_balance = user["credits"] or 0
    
    # Get transaction history
    transactions = await db.fetch("""
        SELECT 
            id, transaction_type, amount, credits, status, created_at, details
        FROM transactions
        WHERE user_id = $1
        ORDER BY created_at DESC
        LIMIT 20
    """, user_id)
    
    # Calculate totals
    credits_used_total = await db.fetchval("""
        SELECT COALESCE(SUM(ABS(credits)), 0)
        FROM transactions
        WHERE user_id = $1 AND credits < 0
    """, user_id) or 0
    
    credits_purchased_total = await db.fetchval("""
        SELECT COALESCE(SUM(credits), 0)
        FROM transactions
        WHERE user_id = $1 AND transaction_type = 'purchase' AND credits > 0
    """, user_id) or 0
    
    last_transaction = transactions[0]["created_at"] if transactions else None
    
    transaction_history = []
    for txn in transactions:
        transaction_history.append({
            "id": txn["id"],
            "type": txn["transaction_type"],
            "amount": float(txn["amount"]) if txn["amount"] else 0.0,
            "credits": txn["credits"],
            "status": txn["status"],
            "created_at": txn["created_at"],
            "details": txn["details"] if isinstance(txn["details"], dict) else json.loads(txn["details"]) if txn["details"] else {}
        })
    
    return {
        "user_id": user_id,
        "credits_balance": credits_balance,
        "credits_used_total": int(credits_used_total),
        "credits_purchased_total": int(credits_purchased_total),
        "last_transaction_at": last_transaction,
        "transaction_history": transaction_history
    }


async def initiate_topup(
    db: asyncpg.Connection,
    user_id: UUID,
    amount: float,
    payment_method: str = "credit_card"
) -> Dict[str, Any]:
    """Initiate topup"""
    # Calculate credits (simplified: 1 credit = $1)
    credits_to_add = int(amount)
    
    # Create pending transaction
    transaction_id = await db.fetchval("""
        INSERT INTO transactions 
        (user_id, transaction_type, amount, credits, status, details)
        VALUES ($1, 'purchase', $2, $3, 'pending', $4::jsonb)
        RETURNING id
    """, user_id, amount, credits_to_add, json.dumps({
        "payment_method": payment_method
    }))
    
    # TODO: Integrate with payment gateway (Stripe, PayPal, etc.)
    # For now, we'll simulate payment success
    
    # Update transaction to completed
    await db.execute("""
        UPDATE transactions
        SET status = 'completed'
        WHERE id = $1
    """, transaction_id)
    
    # Add credits to user
    current_credits = await db.fetchval("SELECT credits FROM users WHERE id = $1", user_id) or 0
    new_balance = current_credits + credits_to_add
    
    await db.execute("""
        UPDATE users
        SET credits = $1
        WHERE id = $2
    """, new_balance, user_id)
    
    return {
        "transaction_id": transaction_id,
        "amount": amount,
        "credits_added": credits_to_add,
        "new_balance": new_balance,
        "payment_url": None,  # Would be payment gateway URL
        "status": "completed"
    }

