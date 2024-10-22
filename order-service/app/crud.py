from sqlmodel import Session, select
from .models import Order
from .schemas import OrderCreate
from typing import Optional
from datetime import datetime

def create_order(session: Session, order: OrderCreate) -> Order:
    order_data = order.dict()
    order_data['total'] = order.quantity * order.price
    db_order = Order(**order_data)  # Use direct instantiation
    session.add(db_order)
    session.commit()
    session.refresh(db_order)
    return db_order
    
def get_order(session: Session, order_id: int) -> Optional[Order]:
    return session.get(Order, order_id)

def list_orders(session: Session) -> list[Order]:
    statement = select(Order)
    results = session.exec(statement)
    return list(results.all())  


def update_order_status(session: Session, order_id: int, status: str) -> Optional[Order]:
    order = session.get(Order, order_id)
    if order:
        order.status = status
        order.updated_at = datetime.utcnow()
        session.add(order)
        session.commit()
        session.refresh(order)
    return order

def delete_orders(session: Session, order_id: int) -> bool:
    order = session.get(Order, order_id)
    if not order:
        return False  # Order not found
    session.delete(order)
    session.commit()
    return True  # Order successfully deleted