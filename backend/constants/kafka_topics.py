"""
Kafka 관련 상수 정의 (Python 3.10 호환)

## 왜 클래스를 나눴는가?

Kafka 이벤트를 발행/소비할 때 필요한 정보를 역할별로 명확히 분리하기 위함:

1. **AggregateType**: "어떤 엔티티에서 일어난 이벤트인가?"
   - 예: PRODUCT, ORDER, CART, USER
   - 용도: Outbox 테이블의 aggregate_type 컬럼

2. **KafkaTopic**: "이 이벤트를 어느 Kafka 토픽으로 보낼까?"
   - 예: product-events, order-events
   - 용도: Publisher가 Kafka로 발행할 때 토픽 지정

3. **ProductEvent / OrderEvent / CartEvent / UserEvent**: "정확히 무슨 일이 일어났는가?"
   - 예: product.stock.changed, order.created
   - 용도: Consumer가 이벤트를 분류/처리할 때

## 사용 예시

```python
# Backend 서비스에서 이벤트 발행:
outbox_event = OutboxEvent(
    aggregate_type=AggregateType.PRODUCT,      # ← 1. 어떤 엔티티?
    aggregate_id=product_id,
    event_type=ProductEvent.STOCK_CHANGED,     # ← 2. 무슨 일?
    topic=KafkaTopic.PRODUCT_EVENTS,          # ← 3. 어디로 보낼까?
    payload={...},
    status="PENDING"
)
db.add(outbox_event)
```

## Enum의 장점

1. **IDE 자동완성**: ProductEvent. 입력하면 상품 관련 이벤트만 표시
2. **타입 체크**: 잘못된 값 입력 시 경고
3. **오타 방지**: "product.stok.changed" 같은 오타 불가능
4. **가독성**: 코드만 봐도 역할이 명확

## 네이밍 규칙

- **토픽**: 하이픈 사용 (product-events, order-events)
- **이벤트 타입**: dot 사용 (product.stock.changed, order.created)
"""
from enum import Enum, unique


# ============================================================================
# Aggregate Type (엔티티 타입)
# ============================================================================
@unique # 값 중복 있으면 에러 내줘서 오타/중복 방지에 도움됨.
class AggregateType(str, Enum):
    ORDER = "order"
    PRODUCT = "product"
    CART = "cart"
    USER = "user"


# ============================================================================
# Kafka Topic (토픽 이름 - 하이픈 규칙)
# ============================================================================
@unique
class KafkaTopic(str, Enum):
    ORDER_EVENTS = "order-events"
    PRODUCT_EVENTS = "product-events"
    CART_EVENTS = "cart-events"
    USER_EVENTS = "user-events"
    NOTIFICATION_EVENTS = "notification-events"


# ============================================================================
# Event Type (이벤트 타입 - dot 규칙 통일)
# ============================================================================
@unique
class OrderEvent(str, Enum):
    CREATED = "order.created"       # 주문 생성
    PAID = "order.paid"             # 결제 완료
    CANCELED = "order.canceled"     # 주문 취소
    COMPLETED = "order.completed"   # 주문 완료
    REFUNDED = "order.refunded"     # 환불 완료

@unique
class ProductEvent(str, Enum):
    CREATED = "product.created"             # 상품 생성
    UPDATED = "product.updated"             # 상품 정보 수정
    DELETED = "product.deleted"             # 상품 삭제
    STOCK_CHANGED = "product.stock.changed" # 재고 변경 (dot 통일!)
    PRICE_CHANGED = "product.price.changed" # 가격 변경 (dot 통일!)
    OUT_OF_STOCK = "product.out.of.stock"   # 품절

@unique
class CartEvent(str, Enum):
    ITEM_ADDED = "cart.item.added"      # 상품 추가
    ITEM_UPDATED = "cart.item.updated"  # 상품 수정
    ITEM_REMOVED = "cart.item.removed"  # 상품 삭제
    CLEARED = "cart.cleared"            # 장바구니 비움

@unique
class UserEvent(str, Enum):
    REGISTERED = "user.registered"  # 회원 가입
    UPDATED = "user.updated"        # 정보 수정
    DELETED = "user.deleted"        # 회원 탈퇴
    LOGIN = "user.login"            # 로그인
    LOGOUT = "user.logout"          # 로그아웃


# ============================================================================
# 사용 예시
# ============================================================================
# """
# # Backend 서비스에서:
# from core.kafka_topics import AggregateType, KafkaTopic, OrderEvent
# from models.kafka.m_outbox import OutboxEvent

# outbox_event = OutboxEvent(
#     aggregate_type=AggregateType.ORDER,     # ← Enum 사용!
#     aggregate_id=order_id,
#     event_type=OrderEvent.CREATED,          # ← Enum 사용!
#     topic=KafkaTopic.ORDER_EVENTS,          # ← Enum 사용!
#     payload={...},
#     status="PENDING"
# )
# db.add(outbox_event)

# # Enum의 장점:
# # 1. IDE 자동완성: AggregateType. 입력하면 목록 표시
# # 2. 타입 체크: 잘못된 값 입력 시 경고
# # 3. 오타 방지: "ORDR" 같은 오타 불가능
# # 4. 값 확인: OrderEvent.CREATED.value == "order.created"
# """


# ============================================================================
# 하위 호환을 위한 별칭 (선택사항 - 기존 코드가 있다면)
# ============================================================================
# TOPIC_ORDER_EVENTS = KafkaTopic.ORDER_EVENTS
# TOPIC_PRODUCT_EVENTS = KafkaTopic.PRODUCT_EVENTS
# OrderEvents = OrderEvent  # 기존 클래스명과 호환
