import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { orderService } from '../services/orderService';
import './OrderDetailPage.css';

export const OrderDetailPage = () => {
    const { orderId } = useParams();
    const navigate = useNavigate();
    const [order, setOrder] = useState(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        loadOrderDetail();
    }, [orderId]);

    const loadOrderDetail = async () => {
        try {
            setIsLoading(true);
            const data = await orderService.getOrderById(orderId);
            setOrder(data);
        } catch (err) {
            console.error('주문 상세 조회 실패:', err);
            alert('주문 정보를 불러오는데 실패했습니다.');
            navigate('/orders/history');
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
        return <div className="order-detail-loading">로딩 중...</div>;
    }

    if (!order) {
        return (
            <div className="order-detail-page">
                <div className="container">
                    <Card className="empty-order">
                        <p>주문 정보를 찾을 수 없습니다.</p>
                        <Button variant="primary" onClick={() => navigate('/orders/history')}>
                            주문 내역으로 돌아가기
                        </Button>
                    </Card>
                </div>
            </div>
        );
    }

    return (
        <div className="order-detail-page">
            <div className="container">
                <div className="page-header">
                    <h1 className="page-title">주문 상세</h1>
                    <Button variant="outline" onClick={() => navigate('/orders/history')}>
                        목록으로
                    </Button>
                </div>

                {/* 주문 정보 */}
                <Card className="order-info-card">
                    <h2 className="section-title">주문 정보</h2>
                    <div className="info-row">
                        <span className="info-label">주문 번호</span>
                        <span className="info-value">{order.order_number}</span>
                    </div>
                    <div className="info-row">
                        <span className="info-label">주문 일시</span>
                        <span className="info-value">{formatDate(order.created_at)}</span>
                    </div>
                </Card>

                {/* 주문 상품 */}
                <Card className="order-items-card">
                    <h2 className="section-title">주문 상품</h2>
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
                </Card>

                {/* 결제 금액 */}
                <Card className="order-summary-card">
                    <h2 className="section-title">결제 금액</h2>
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
                </Card>
            </div>
        </div>
    );
};
