import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { cartService } from '../services/cartService';
import './CartPage.css';

export const CartPage = () => {
    const [cartData, setCartData] = useState(null); // CartOut 스키마: { items, total_price, total_items }
    const [isLoading, setIsLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        loadCart();
    }, []);

    const loadCart = async () => {
        try {
            setIsLoading(true);
            const data = await cartService.getCart();
            setCartData(data);
        } catch (err) {
            console.error('Failed to load cart:', err);
            // 개발 중: 목업 데이터
            setCartData(getMockCartItems());
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
            await cartService.updateCartItem(itemId, newQuantity);
            setCartData(prev => ({
                ...prev,
                items: prev.items.map(item =>
                    item.id === itemId
                        ? { ...item, quantity: newQuantity }
                        : item
                )
            }));
        } catch (err) {
            console.error('Failed to update quantity:', err);
            // 목업: 낙관적 업데이트
            setCartData(prev => ({
                ...prev,
                items: prev.items.map(item =>
                    item.id === itemId
                        ? { ...item, quantity: newQuantity }
                        : item
                )
            }));
        }
    };

    const removeItem = async (itemId) => {
        try {
            await cartService.removeCartItem(itemId);
            setCartData(prev => ({
                ...prev,
                items: prev.items.filter(item => item.id !== itemId)
            }));
        } catch (err) {
            console.error('Failed to remove item:', err);
            // 목업: 낙관적 업데이트
            setCartData(prev => ({
                ...prev,
                items: prev.items.filter(item => item.id !== itemId)
            }));
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

    if (isLoading) {
        return (
            <div className="cart-page">
                <div className="container">
                    <div className="cart-loading">로딩 중...</div>
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
                                            {item.price.toLocaleString()}원
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
                                            {(item.price * item.quantity).toLocaleString()}원
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
