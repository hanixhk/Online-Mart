from sqlmodel import Session, select
from .models import Product
from .schemas import ProductCreate, ProductUpdate
from typing import Optional
from datetime import datetime

def create_product(session: Session, product: ProductCreate) -> Product:
    db_product = Product(
        name=product.name,
        description=product.description,
        price=product.price,
        quantity=product.quantity
    )
    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return db_product

def get_product(session: Session, product_id: int) -> Optional[Product]:
    return session.get(Product, product_id)

def get_product_by_name(session: Session, name: str) -> Optional[Product]:
    statement = select(Product).where(Product.name == name)
    return session.exec(statement).first()

def list_products(session: Session) -> list[Product]:
    statement = select(Product)
    results = session.exec(statement)
    return list(results.all())

def update_product(session: Session, product_id: int, product_update: ProductUpdate) -> Optional[Product]:
    product = session.get(Product, product_id)
    if product:
        for key, value in product_update.dict(exclude_unset=True).items():
            setattr(product, key, value)
        product.updated_at = datetime.utcnow()
        session.add(product)
        session.commit()
        session.refresh(product)
    return product

def delete_product(session: Session, product_id: int) -> bool:
    product = session.get(Product, product_id)
    if product:
        session.delete(product)
        session.commit()
        return True
    return False
