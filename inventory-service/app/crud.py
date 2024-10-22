from sqlmodel import Session, select
from .models import Inventory
from .schemas import InventoryCreate, InventoryUpdate
from typing import Optional
from datetime import datetime

def create_inventory(session: Session, inventory: InventoryCreate) -> Inventory:
    db_inventory = Inventory(
        product_id=inventory.product_id,
        quantity=inventory.quantity
    )
    # Determine availability based on quantity
    db_inventory.is_available = inventory.quantity > 0
    session.add(db_inventory)
    session.commit()
    session.refresh(db_inventory)
    return db_inventory

def get_inventory(session: Session, inventory_id: int) -> Optional[Inventory]:
    return session.get(Inventory, inventory_id)

def get_inventory_by_product_id(session: Session, product_id: int) -> Optional[Inventory]:
    statement = select(Inventory).where(Inventory.product_id == product_id)
    return session.exec(statement).first()

def list_inventories(session: Session) -> list[Inventory]:
    statement = select(Inventory)
    results = session.exec(statement)
    return results.all()

def update_inventory(session: Session, inventory_id: int, inventory_update: InventoryUpdate) -> Optional[Inventory]:
    inventory = session.get(Inventory, inventory_id)
    if inventory:
        if inventory_update.quantity is not None:
            inventory.quantity = inventory_update.quantity
            inventory.is_available = inventory.quantity > 0
        if inventory_update.is_available is not None:
            inventory.is_available = inventory_update.is_available
        inventory.updated_at = datetime.utcnow()
        session.add(inventory)
        session.commit()
        session.refresh(inventory)
    return inventory

def delete_inventory(session: Session, inventory_id: int) -> bool:
    inventory = session.get(Inventory, inventory_id)
    if inventory:
        session.delete(inventory)
        session.commit()
        return True
    return False

def decrease_inventory(session: Session, product_id: int, quantity: int) -> Optional[Inventory]:
    inventory = get_inventory_by_product_id(session, product_id)
    if inventory and inventory.quantity >= quantity:
        inventory.quantity -= quantity
        inventory.is_available = inventory.quantity > 0
        inventory.updated_at = datetime.utcnow()
        session.add(inventory)
        session.commit()
        session.refresh(inventory)
        return inventory
    return None

def increase_inventory(session: Session, product_id: int, quantity: int) -> Optional[Inventory]:
    inventory = get_inventory_by_product_id(session, product_id)
    if inventory:
        inventory.quantity += quantity
        inventory.is_available = inventory.quantity > 0
        inventory.updated_at = datetime.utcnow()
        session.add(inventory)
        session.commit()
        session.refresh(inventory)
        return inventory
    return None
