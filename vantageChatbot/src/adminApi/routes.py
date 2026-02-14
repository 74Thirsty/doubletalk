from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.adminApi.auth import require_admin_key
from src.storage.db import get_db
from src.storage.models import FAQ, Product, Service, Tenant

router = APIRouter(prefix='/admin', dependencies=[Depends(require_admin_key)])


class TenantIn(BaseModel):
    name: str
    timezone: str = 'UTC'


@router.post('/tenants')
def create_tenant(payload: TenantIn, db: Session = Depends(get_db)):
    tenant = Tenant(name=payload.name, timezone=payload.timezone)
    db.add(tenant)
    db.commit()
    return {'id': tenant.id}


class ServiceIn(BaseModel):
    tenant_id: int
    name: str
    duration_min: int
    price_cents: int


@router.post('/services')
def create_service(payload: ServiceIn, db: Session = Depends(get_db)):
    service = Service(**payload.model_dump())
    db.add(service)
    db.commit()
    return {'id': service.id}


class ProductIn(BaseModel):
    tenant_id: int
    name: str
    sku: str
    price_cents: int


@router.post('/products')
def create_product(payload: ProductIn, db: Session = Depends(get_db)):
    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()
    return {'id': product.id}


class FAQIn(BaseModel):
    tenant_id: int
    question: str
    answer: str


@router.post('/faqs')
def create_faq(payload: FAQIn, db: Session = Depends(get_db)):
    faq = FAQ(**payload.model_dump())
    db.add(faq)
    db.commit()
    return {'id': faq.id}
