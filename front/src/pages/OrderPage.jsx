import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { cartService } from '../services/cartService';
import { orderService } from '../services/orderService';
import { useAuth } from '../contexts/AuthContext';
import './OrderPage.css';

export const OrderPage = () => {
    const navigate = useNavigate();
    const { user } = useAuth(); // 로그인한 사용자 정보
    const [cartItems, setCartItems] = useState([]);
    const [orderInfo, setOrderInfo] = useState({
        address: '' // 통합된 주소만
    });
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        loadCartItems();
    }, []);

    const loadCartItems = async () => {
        try {
            setIsLoading(true);
            const data = await cartService.getCart();
            setCartItems(data.items || []);
        } catch (err) {
            console.error('장바구니 조회 실패:', err);
            // Mock 데이터
            setCartItems([
                {
                    id: 1,
                    product_id: 1,
                    product_name: '곰표 우유 식빵 660g',
                    product_price: 4050,
                    product_image: '',
                    quantity: 2
                },
                {
                    id: 2,
                    product_id: 2,
                    product_name: '신라면 멀티팩 5개입',
                    product_price: 4480,
                    product_image: '',
                    quantity: 1
                }
            ]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setOrderInfo(prev => ({ ...prev, [name]: value }));
    };

    const calculateTotal = () => {
        return cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    };

    const handleOrder = async () => {
        // 입력 검증
        if (!orderInfo.address) {
            alert('배송지 주소를 입력해주세요.');
            return;
        }

        try {
            // 백엔드 형식에 맞게 데이터 변환
            const orderPayload = {
                items: cartItems.map(item => ({
                    product_id: item.product_id,
                    quantity: item.quantity
                })),
                shipping_address: orderInfo.address
            };

            // 주문 API 호출
            await orderService.createOrder(orderPayload);

            alert('주문이 완료되었습니다!');
            navigate('/orders/history');
        } catch (err) {
            console.error('주문 실패:', err);
            alert('주문에 실패했습니다. 다시 시도해주세요.');
        }
    };

    if (isLoading) {
        return <div className="order-loading">로딩 중...</div>;
    }

    const totalAmount = calculateTotal();
    const shippingFee = 0; // 무료배송
    const finalAmount = totalAmount + shippingFee;

    return (
        <div className="order-page">
            <div className="container">
                <h1 className="order-title">주문/결제</h1>

                {/* 주문 상품 */}
                <Card className="order-section">
                    <h2 className="section-title">주문 상품</h2>
                    <div className="order-items">
                        {cartItems.map(item => (
                            <div key={item.id} className="order-item">
                                <div className="order-item-image">
                                    {item.image ? (
                                        <img src={item.image} alt={item.name} />
                                    ) : (
                                        <div className="order-item-placeholder">🍞</div>
                                    )}
                                </div>
                                <div className="order-item-info">
                                    <h3>{item.name}</h3>
                                    <p className="order-item-price">
                                        {item.price?.toLocaleString() || '0'}원 × {item.quantity}개
                                    </p>
                                </div>
                                <div className="order-item-total">
                                    {((item.price || 0) * item.quantity).toLocaleString()}원
                                </div>
                            </div>
                        ))}
                    </div>
                </Card>

                {/* 주문자 정보 */}
                <Card className="order-section">
                    <h2 className="section-title">주문자 정보</h2>
                    <div className="order-form">
                        <div className="form-group">
                            <label>이름</label>
                            <input
                                type="text"
                                value={user?.username || '로그인이 필요합니다'}
                                disabled
                                className="readonly-input"
                            />
                        </div>
                    </div>
                </Card>

                {/* 배송지 정보 */}
                <Card className="order-section">
                    <h2 className="section-title">배송지 정보</h2>
                    <div className="order-form">
                        <div className="form-group">
                            <label>주소 *</label>
                            <textarea
                                name="address"
                                value={orderInfo.address}
                                onChange={handleInputChange}
                                placeholder="배송받을 주소를 입력하세요"
                                rows="3"
                            />
                        </div>
                    </div>
                </Card>

                {/* 결제 금액 */}
                <Card className="order-section order-summary">
                    <h2 className="section-title">결제 금액</h2>
                    <div className="summary-row">
                        <span>상품 금액</span>
                        <span>{totalAmount.toLocaleString()}원</span>
                    </div>
                    <div className="summary-row">
                        <span>배송비</span>
                        <span>
                            {shippingFee === 0 ? (
                                <Badge variant="success" size="small">무료배송</Badge>
                            ) : (
                                `${shippingFee.toLocaleString()}원`
                            )}
                        </span>
                    </div>
                    <div className="summary-divider" />
                    <div className="summary-row summary-total">
                        <span>최종 결제 금액</span>
                        <span className="total-amount">{finalAmount.toLocaleString()}원</span>
                    </div>
                </Card>

                {/* 주문 버튼 */}
                <div className="order-actions">
                    <Button variant="outline" size="large" onClick={() => navigate('/cart')}>
                        장바구니로 돌아가기
                    </Button>
                    <Button variant="primary" size="large" onClick={handleOrder}>
                        {finalAmount.toLocaleString()}원 결제하기
                    </Button>
                </div>
            </div>
        </div>
    );
};
