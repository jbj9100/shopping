import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { orderService } from '../services/orderService';
import './OrderHistoryPage.css';

export const OrderHistoryPage = () => {
    const navigate = useNavigate();
    const [orders, setOrders] = useState([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        loadOrders();
    }, []);

    const loadOrders = async () => {
        try {
            setIsLoading(true);
            const data = await orderService.getAllOrders();
            setOrders(data);
        } catch (err) {
            console.error('주문 내역 조회 실패:', err);
            setOrders([]);
        } finally {
            setIsLoading(false);
        }
    };

    const formatDate = (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('ko-KR', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    if (isLoading) {
        return <div className="order-history-loading">로딩 중...</div>;
    }

    if (orders.length === 0) {
        return (
            <div className="order-history-page">
                <div className="container">
                    <h1 className="page-title">주문 내역</h1>
                    <Card className="empty-orders">
                        <p>주문 내역이 없습니다.</p>
                        <Button variant="primary" onClick={() => navigate('/')}>
                            쇼핑 계속하기
                        </Button>
                    </Card>
                </div>
            </div>
        );
    }

    return (
        <div className="order-history-page">
            <div className="container">
                <h1 className="page-title">주문 내역</h1>

                <div className="orders-list">
                    {orders.map(order => (
                        <Card
                            key={order.id}
                            className="order-card"
                            onClick={() => navigate(`/orders/${order.id}`)}
                            style={{ cursor: 'pointer' }}
                        >
                            {/* 주문 헤더 */}
                            <div className="order-header">
                                <div className="order-info">
                                    <span className="order-number">{order.order_number}</span>
                                    <span className="order-date">{formatDate(order.created_at)}</span>
                                </div>
                            </div>

                            {/* 주문 상품 */}
                            <div className="order-items">
                                {order.items.map((item, idx) => (
                                    <div key={idx} className="order-item">
                                        <div className="order-item-image">
                                            {item.product_image ? (
                                                <img src={item.product_image} alt={item.name} />
                                            ) : (
                                                <div className="order-item-placeholder">🍞</div>
                                            )}
                                        </div>
                                        <div className="order-item-details">
                                            <h3>{item.name}</h3>
                                            <p className="item-quantity">
                                                {item.price.toLocaleString()}원 × {item.quantity}개
                                            </p>
                                        </div>
                                        <div className="order-item-price">
                                            {(item.price * item.quantity).toLocaleString()}원
                                        </div>
                                    </div>
                                ))}
                            </div>

                            {/* 주문 요약 */}
                            <div className="order-summary">
                                <div className="summary-row">
                                    <span>상품 금액</span>
                                    <span>{order.items_amount.toLocaleString()}원</span>
                                </div>
                                <div className="summary-row">
                                    <span>배송비</span>
                                    <span>
                                        {order.shipping_fee === 0 ? (
                                            <Badge variant="success" size="small">무료배송</Badge>
                                        ) : (
                                            `${order.shipping_fee.toLocaleString()}원`
                                        )}
                                    </span>
                                </div>
                                <div className="summary-divider" />
                                <div className="summary-row summary-total">
                                    <span>총 결제 금액</span>
                                    <span className="total-amount">
                                        {order.total_price.toLocaleString()}원
                                    </span>
                                </div>
                            </div>
                        </Card>
                    ))}
                </div>
            </div>
        </div>
    );
};
