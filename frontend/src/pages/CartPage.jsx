import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { cartService } from '../services/cartService';
import { useAuth } from '../contexts/AuthContext';
import './CartPage.css';

export const CartPage = () => {
    const [cartData, setCartData] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const navigate = useNavigate();
    const { user, loading: authLoading } = useAuth();

    useEffect(() => {
        loadCart();
    }, []);

    const loadCart = async () => {
        try {
            setIsLoading(true);
            setError(null);
            const data = await cartService.getCart();
            setCartData(data);
        } catch (err) {
            console.error('Failed to load cart:', err);

            // 401 에러: 로그인 필요
            if (err.response?.status === 401) {
                setError('로그인이 필요합니다.');
                // 2초 후 로그인 페이지로 이동
                setTimeout(() => {
                    navigate('/login');
                }, 2000);
            } else {
                setError('장바구니를 불러오는데 실패했습니다.');
            }
        } finally {
            setIsLoading(false);
        }
    };

    const getMockCartItems = () => ({
        items: [
            {
                id: 1,
                product_id: 1,
                name: '삼성 갤럭시 S24 Ultra 자급제',
                price: 1590000,
                quantity: 1,
                image: null
            },
            {
                id: 2,
                product_id: 3,
                name: '다이슨 V15 무선청소기',
                price: 890000,
                quantity: 2,
                image: null
            }
        ],
        total_price: 3370000,
        total_items: 3
    });

    const updateQuantity = async (itemId, newQuantity) => {
        if (newQuantity < 1) return;

        try {
            const result = await cartService.updateCartItem(itemId, newQuantity);
            // API가 전체 장바구니를 반환하므로 그것을 사용
            setCartData(result);
        } catch (err) {
            console.error('Failed to update quantity:', err);
            alert('수량 변경에 실패했습니다: ' + (err.response?.data?.detail || err.message));
        }
    };

    const removeItem = async (itemId) => {
        console.log('🗑️ 삭제 시도:', itemId);
        try {
            const result = await cartService.removeCartItem(itemId);
            console.log('✅ 삭제 성공:', result);
            // API가 전체 장바구니를 반환하므로 그것을 사용
            setCartData(result);
        } catch (err) {
            console.error('❌ 삭제 실패:', err);
            console.error('에러 응답:', err.response?.data);
            alert('삭제에 실패했습니다: ' + (err.response?.data?.detail || err.message));
        }
    };

    // 백엔드에서 total_price, total_items를 제공하지만, 없을 경우 계산
    const totalPrice = cartData?.total_price || cartData?.items?.reduce(
        (sum, item) => sum + item.price * item.quantity,
        0
    ) || 0;

    const totalItems = cartData?.total_items || cartData?.items?.reduce(
        (sum, item) => sum + item.quantity,
        0
    ) || 0;

    if (isLoading || authLoading) {
        return (
            <div className="cart-page">
                <div className="container">
                    <div className="cart-loading">로딩 중...</div>
                </div>
            </div>
        );
    }

    // 에러 상태 (로그인 필요 등)
    if (error) {
        return (
            <div className="cart-page">
                <div className="container">
                    <div className="cart-empty">
                        <div className="cart-empty-icon">⚠️</div>
                        <h2>{error}</h2>
                        <p>잠시 후 로그인 페이지로 이동합니다...</p>
                        <Button onClick={() => navigate('/login')}>지금 로그인하기</Button>
                    </div>
                </div>
            </div>
        );
    }

    if (!cartData || !cartData.items || cartData.items.length === 0) {
        return (
            <div className="cart-page">
                <div className="container">
                    <div className="cart-empty">
                        <div className="cart-empty-icon">🛒</div>
                        <h2>장바구니가 비어있습니다</h2>
                        <p>상품을 담아보세요!</p>
                        <Button onClick={() => navigate('/')}>쇼핑 계속하기</Button>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="cart-page">
            <div className="container">
                <h1 className="cart-title">장바구니</h1>

                <div className="cart-layout">
                    <div className="cart-items">
                        {cartData.items.map((item) => (
                            <Card key={item.id} className="cart-item-card">
                                <div className="cart-item">
                                    <div className="cart-item-image">
                                        {item.image ? (
                                            <img src={item.image} alt={item.name} />
                                        ) : (
                                            <div className="cart-item-image-placeholder">📦</div>
                                        )}
                                    </div>

                                    <div className="cart-item-info">
                                        <h3 className="cart-item-name">{item.name}</h3>
                                        <p className="cart-item-price">
                                            {item.price?.toLocaleString() || '0'}원
                                        </p>
                                    </div>

                                    <div className="cart-item-quantity">
                                        <button
                                            className="quantity-button"
                                            onClick={() => updateQuantity(item.id, item.quantity - 1)}
                                        >
                                            −
                                        </button>
                                        <span className="quantity-value">{item.quantity}</span>
                                        <button
                                            className="quantity-button"
                                            onClick={() => updateQuantity(item.id, item.quantity + 1)}
                                        >
                                            +
                                        </button>
                                    </div>

                                    <div className="cart-item-total">
                                        <p className="cart-item-total-price">
                                            {((item.price || 0) * item.quantity).toLocaleString()}원
                                        </p>
                                    </div>

                                    <button
                                        className="cart-item-remove"
                                        onClick={() => removeItem(item.id)}
                                    >
                                        ✕
                                    </button>
                                </div>
                            </Card>
                        ))}
                    </div>

                    <div className="cart-summary">
                        <Card>
                            <h2 className="cart-summary-title">주문 요약</h2>

                            <div className="cart-summary-row">
                                <span>상품 개수</span>
                                <span>{totalItems}개</span>
                            </div>

                            <div className="cart-summary-row">
                                <span>상품 금액</span>
                                <span>{totalPrice.toLocaleString()}원</span>
                            </div>

                            <div className="cart-summary-row">
                                <span>배송비</span>
                                <Badge variant="success">무료</Badge>
                            </div>

                            <div className="cart-summary-divider"></div>

                            <div className="cart-summary-row cart-summary-total">
                                <span>총 결제 금액</span>
                                <span className="cart-summary-total-price">
                                    {totalPrice.toLocaleString()}원
                                </span>
                            </div>

                            <Button
                                variant="primary"
                                size="large"
                                fullWidth
                                onClick={() => navigate('/order')}
                            >
                                주문하기
                            </Button>
                        </Card>
                    </div>
                </div>
            </div>
        </div>
    );
};
