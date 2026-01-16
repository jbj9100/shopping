from repositories.orders.rep_orders import rep_create_order, rep_all_orders, rep_order_detail
from sqlalchemy.ext.asyncio import AsyncSession
from services.carts.svc_carts import svc_clear_cartItems, svc_get_cart_with_items
from schemas.sc_orders import OrderItemOut, OrderCreateIn, OrderOut
from models.m_user import Users
from datetime import datetime
import uuid

# Outbox Pattern
from models.kafka.m_outbox import OutboxEvent
from constants.kafka_topics import AggregateType, KafkaTopic, OrderEvent

async def svc_create_order(db: AsyncSession, order_create_in: OrderCreateIn, user: Users):
    cartItems = await svc_get_cart_with_items(db, user.id)
    if cartItems.total_items == 0:
        raise ValueError("장바구니가 비어있습니다.")
    
    order_number = "ORD-" + str(uuid.uuid4())[:10].upper()
    
    # DB에 주문 저장 (order_db는 SQLAlchemy 모델)
    order_db = await rep_create_order(db, user, order_create_in, cartItems, order_number)

    # 응답용 OrderItemOut 리스트 생성
    order_items = []
    items_amount = 0
    for item in cartItems.items:
        item_total = item.discount_price * item.quantity
        items_amount += item_total
        order_items.append(OrderItemOut(
            product_id=item.product_id,
            name=item.product_name,
            quantity=item.quantity,
            price=item.discount_price
        ))
    
    # 배송비 계산 (예: 무료배송)
    shipping_fee = 0
    total_price = items_amount + shipping_fee
    
    # OutboxEvent 생성 (Kafka 이벤트 발행)
    outbox_event = OutboxEvent(
        aggregate_type=AggregateType.ORDER,
        aggregate_id=order_db.id,
        event_type=OrderEvent.CREATED,
        topic=KafkaTopic.ORDER_EVENTS,
        payload={
            "order_id": order_db.id,
            "user_id": user.id,
            "order_number": order_number,
            "items_amount": items_amount,
            "shipping_fee": shipping_fee,
            "total_amount": total_price,
            "items": [
                {
                    "product_id": item.product_id,
                    "name": item.name,
                    "quantity": item.quantity,
                    "price": item.price
                }
                for item in order_items
            ],
            "shipping_address": order_create_in.shipping_address
        },
        status="PENDING"
    )
    db.add(outbox_event)
    
    # Pydantic OrderOut 생성
    order = OrderOut(
        id=order_db.id,
        order_number=order_number,
        items_amount=items_amount,
        shipping_fee=shipping_fee,
        total_price=total_price,
        created_at=order_db.created_at,
        items=order_items
    )
    
    # 장바구니 비우기
    await svc_clear_cartItems(db, user.id)
    await db.commit()  # 주문 + outbox_event 함께 커밋
    
    return order


async def svc_all_orders(db: AsyncSession, users: Users):
    """사용자의 모든 주문 조회"""
    orders_db = await rep_all_orders(db, users)
    
    # SQLAlchemy 모델을 Pydantic 스키마로 변환
    orders_out = []
    for order_db in orders_db:
        # OrderItems를 OrderItemOut으로 변환
        items_out = []
        for item in order_db.items:
            items_out.append(OrderItemOut(
                product_id=item.product_id,
                name=item.name_snapshot,
                quantity=item.quantity,
                price=item.price_snapshot
            ))
        
        # OrderOut 생성
        order_out = OrderOut(
            id=order_db.id,
            order_number=order_db.order_number,
            items_amount=order_db.items_amount,
            shipping_fee=order_db.shipping_fee,
            total_price=order_db.total_amount,
            created_at=order_db.created_at,
            items=items_out
        )
        orders_out.append(order_out)
    
    return orders_out


async def svc_order_detail(db: AsyncSession, order_id: int, users: Users):
    """특정 주문 상세 조회"""
    order_db = await rep_order_detail(db, order_id, users)
    
    if not order_db:
        raise ValueError(f"주문 ID {order_id}를 찾을 수 없습니다.")
    
    # OrderItems를 OrderItemOut으로 변환
    items_out = []
    for item in order_db.items:
        items_out.append(OrderItemOut(
            product_id=item.product_id,
            name=item.name_snapshot,
            quantity=item.quantity,
            price=item.price_snapshot
        ))
    
    # OrderOut 생성
    order_out = OrderOut(
        id=order_db.id,
        order_number=order_db.order_number,
        items_amount=order_db.items_amount,
        shipping_fee=order_db.shipping_fee,
        total_price=order_db.total_amount,
        created_at=order_db.created_at,
        items=items_out
    )
    
    return order_out