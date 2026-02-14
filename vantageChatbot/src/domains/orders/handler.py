from sqlalchemy.orm import Session

from src.core.responseComposer import compose
from src.core.types import InboundMessage, OutboundMessage
from src.storage.models import Order, OrderItem, Product


def handle(inbound: InboundMessage, db: Session, user_id: int) -> OutboundMessage:
    products = db.query(Product).filter(Product.tenant_id == inbound.tenant_id).all()
    if not products:
        return compose('No products configured yet.')
    if 'yes' in inbound.text.lower():
        order = Order(tenant_id=inbound.tenant_id, user_id=user_id, status='placed', total_cents=products[0].price_cents)
        db.add(order)
        db.flush()
        db.add(OrderItem(order_id=order.id, product_id=products[0].id, qty=1, price_cents=products[0].price_cents))
        db.commit()
        return compose(f'Order placed #{order.id}.')
    return compose(f'We have: {", ".join([p.name for p in products])}. Confirm place order?')
