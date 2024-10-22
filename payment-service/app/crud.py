from sqlmodel import Session, select
from .models import Transaction
from .schemas import TransactionCreate, TransactionUpdate
from typing import Optional
from datetime import datetime

def create_transaction(session: Session, transaction_data: TransactionCreate) -> Transaction:
    db_transaction = Transaction(
        order_id=transaction_data.order_id,   # corrected from transaction to transaction_data
        user_id=transaction_data.user_id,     # corrected from transaction to transaction_data
        amount=transaction_data.amount,       # corrected from transaction to transaction_data
        currency=transaction_data.currency,   # corrected from transaction to transaction_data
        payment_method=transaction_data.payment_method,  # corrected from transaction to transaction_data
        status="pending"
    )
    session.add(db_transaction)
    session.commit()
    session.refresh(db_transaction)
    return db_transaction
    
def get_transaction(session: Session, transaction_id: int) -> Optional[Transaction]:
    return session.get(Transaction, transaction_id)

def get_transaction_by_order_id(session: Session, order_id: int) -> Optional[Transaction]:
    statement = select(Transaction).where(Transaction.order_id == order_id)
    return session.exec(statement).first()

def list_transactions(session: Session) -> list[Transaction]:
    statement = select(Transaction)
    results = session.exec(statement)
    return list(results.all())

def update_transaction(session: Session, transaction_id: int, transaction_update: TransactionUpdate) -> Optional[Transaction]:
    transaction = session.get(Transaction, transaction_id)
    if transaction:
        for key, value in transaction_update.dict(exclude_unset=True).items():
            setattr(transaction, key, value)
        transaction.updated_at = datetime.utcnow()
        session.add(transaction)
        session.commit()
        session.refresh(transaction)
    return transaction

def delete_transaction(session: Session, transaction_id: int) -> bool:
    transaction = session.get(Transaction, transaction_id)
    if transaction:
        session.delete(transaction)
        session.commit()
        return True
    return False
