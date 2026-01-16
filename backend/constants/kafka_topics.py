# """
# Kafka 관련 상수 정의 (Python 3.10 호환)

# - Enum을 사용하여 타입 안전성 보장
# - 네이밍 규칙 통일: 토픽(하이픈), 이벤트(dot)
# - aggregate_type, topic, event_type 모두 상수화
# """
from enum import Enum, unique


# ============================================================================
# Aggregate Type (엔티티 타입)
# ============================================================================
@unique # 값 중복 있으면 에러 내줘서 오타/중복 방지에 도움됨.
class AggregateType(str, Enum):
    # """
    # Outbox 이벤트의 aggregate_type 값
    
    # 사용: OutboxEvent(aggregate_type=AggregateType.ORDER, ...)
    # """
    ORDER = "order"
    PRODUCT = "product"
    CART = "cart"
    USER = "user"
    PAYMENT = "payment"


# ============================================================================
# Kafka Topic (토픽 이름 - 하이픈 규칙)
# ============================================================================
@unique
class KafkaTopic(str, Enum):
    # """
    # Kafka 토픽 이름
    # 
    # 네이밍 규칙: {entity}-events (하이픈 사용)
    # 사용: OutboxEvent(topic=KafkaTopic.ORDER_EVENTS, ...)
    # """
    ORDER_EVENTS = "order-events"
    PRODUCT_EVENTS = "product-events"
    CART_EVENTS = "cart-events"
    USER_EVENTS = "user-events"
    PAYMENT_EVENTS = "payment-events"
    NOTIFICATION_EVENTS = "notification-events"


# ============================================================================
# Event Type (이벤트 타입 - dot 규칙 통일)
# ============================================================================
@unique
class OrderEvent(str, Enum):
    # """
    # 주문 관련 이벤트 타입
    # 
    # 네이밍 규칙: order.{action} (전부 dot 사용)
    # 사용: OutboxEvent(event_type=OrderEvent.CREATED, ...)
    # """
    CREATED = "order.created"       # 주문 생성
    PAID = "order.paid"             # 결제 완료
    CANCELED = "order.canceled"     # 주문 취소
    COMPLETED = "order.completed"   # 주문 완료
    REFUNDED = "order.refunded"     # 환불 완료

@unique
class ProductEvent(str, Enum):
    # """
    # 상품 관련 이벤트 타입
    # 
    # 네이밍 규칙: product.{detail}.{action} (전부 dot 사용, underscore 제거)
    # """
    CREATED = "product.created"             # 상품 생성
    UPDATED = "product.updated"             # 상품 정보 수정
    DELETED = "product.deleted"             # 상품 삭제
    STOCK_CHANGED = "product.stock.changed" # 재고 변경 (dot 통일!)
    PRICE_CHANGED = "product.price.changed" # 가격 변경 (dot 통일!)
    OUT_OF_STOCK = "product.out.of.stock"   # 품절

@unique
class CartEvent(str, Enum):
    # """
    # 장바구니 관련 이벤트 타입
    
    # 네이밍 규칙: cart.item.{action} (전부 dot 사용)
    # """
    ITEM_ADDED = "cart.item.added"      # 상품 추가
    ITEM_UPDATED = "cart.item.updated"  # 상품 수정
    ITEM_REMOVED = "cart.item.removed"  # 상품 삭제
    CLEARED = "cart.cleared"            # 장바구니 비움

@unique
class UserEvent(str, Enum):
    # """
    # 사용자 관련 이벤트 타입
    
    # 네이밍 규칙: user.{action}
    # """
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
