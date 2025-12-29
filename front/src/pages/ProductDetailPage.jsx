import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { StockDepletionBadge } from '../components/stock/StockDepletionBadge';
import { PriceAlertModal } from '../components/price-alert/PriceAlertModal';
import { RecommendationSection } from '../components/recommendation/RecommendationSection';
import { productService } from '../services/productService';
import './ProductDetailPage.css';

export const ProductDetailPage = () => {
    const { id } = useParams();
    const [product, setProduct] = useState(null);
    const [quantity, setQuantity] = useState(1);
    const [showAlertModal, setShowAlertModal] = useState(false);
    const [recommendations, setRecommendations] = useState([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        loadProduct();
    }, [id]);

    const loadProduct = async () => {
        try {
            setIsLoading(true);
            const data = await productService.getProductById(id);
            setProduct(data);
        } catch (err) {
            // 목업 데이터
            setProduct({
                id: Number(id),
                name: '슬라이스 식빵 통밀, 65g, 1개',
                price: 1550,
                originalPrice: 2000,
                discount: 450,
                brand: 'R.LUX',
                image: null,
                rating: 4.8,
                reviewCount: 1809,
                freeShipping: true,
                rocketShipping: false,
                stock: 15,
                depletionEtaMinutes: 8,
                description: '건강한 통밀로 만든 식빵입니다. 촉촉하고 부드러운 식감이 특징입니다.'
            });

            // 목업 추천
            setRecommendations([
                { id: 2, name: '호밀빵 500g', price: 5800, reason: 'co-viewed', image: null },
                { id: 3, name: '바게트 300g', price: 3200, reason: 'co-viewed', image: null },
                { id: 4, name: '크루아상 6개', price: 4900, reason: 'similar', image: null }
            ]);
        } finally {
            setIsLoading(false);
        }
    };

    const handlePriceAlert = (alertData) => {
        console.log('가격 알림 설정:', alertData);
        // API 호출하여 알림 저장
    };

    if (isLoading) {
        return <div className="product-loading">로딩 중...</div>;
    }

    if (!product) {
        return <div className="product-error">상품을 찾을 수 없습니다.</div>;
    }

    const discountPercent = product.discount
        ? Math.round((product.discount / product.originalPrice) * 100)
        : 0;

    return (
        <div className="product-detail-page">
            <div className="container">
                {/* 상품 상단 */}
                <div className="product-detail-header">
                    <div className="product-image-section">
                        {product.image ? (
                            <img src={product.image} alt={product.name} className="product-detail-image" />
                        ) : (
                            <div className="product-detail-placeholder">🍞</div>
                        )}
                    </div>

                    <div className="product-info-section">
                        {product.brand && (
                            <div className="product-brand">{product.brand}</div>
                        )}

                        <h1 className="product-detail-title">{product.name}</h1>

                        {(product.rating || product.reviewCount) && (
                            <div className="product-rating-section">
                                <span className="product-stars">⭐ {product.rating?.toFixed(1)}</span>
                                {product.reviewCount > 0 && (
                                    <span className="product-reviews">
                                        리뷰 {product.reviewCount.toLocaleString()}개
                                    </span>
                                )}
                            </div>
                        )}

                        {/* 품절 예측 */}
                        {product.depletionEtaMinutes && (
                            <div className="product-depletion-alert">
                                <StockDepletionBadge depletionEtaMinutes={product.depletionEtaMinutes} />
                            </div>
                        )}

                        {/* 가격 */}
                        <div className="product-price-section">
                            {discountPercent > 0 && (
                                <>
                                    <div className="product-discount-badge-large">
                                        <Badge variant="error" size="large">{discountPercent}% 할인</Badge>
                                    </div>
                                    <div className="product-original-price-large">
                                        {product.originalPrice.toLocaleString()}원
                                    </div>
                                </>
                            )}
                            <div className="product-current-price">
                                {product.price.toLocaleString()}원
                            </div>
                        </div>

                        {/* 배송 */}
                        <div className="product-shipping-section">
                            {product.rocketShipping && (
                                <Badge variant="primary">로켓배송</Badge>
                            )}
                            {product.freeShipping && !product.rocketShipping && (
                                <Badge variant="success">무료배송</Badge>
                            )}
                        </div>

                        {/* 수량 선택 */}
                        <div className="product-quantity-section">
                            <label>수량</label>
                            <div className="quantity-selector">
                                <button onClick={() => setQuantity(Math.max(1, quantity - 1))}>-</button>
                                <span>{quantity}</span>
                                <button onClick={() => setQuantity(quantity + 1)}>+</button>
                            </div>
                        </div>

                        {/* 액션 버튼 */}
                        <div className="product-actions">
                            <Button variant="outline" size="large" onClick={() => setShowAlertModal(true)}>
                                🔔 가격 알림 설정
                            </Button>
                            <Button variant="primary" size="large" fullWidth>
                                장바구니 담기
                            </Button>
                            <Button variant="secondary" size="large" fullWidth>
                                바로 구매
                            </Button>
                        </div>
                    </div>
                </div>

                {/* 상품 설명 */}
                <Card className="product-description-section">
                    <h2>상품 설명</h2>
                    <p>{product.description}</p>
                </Card>

                {/* 추천 상품 */}
                <RecommendationSection recommendations={recommendations} />
            </div>

            {/* 가격 알림 모달 */}
            {showAlertModal && (
                <PriceAlertModal
                    product={product}
                    onClose={() => setShowAlertModal(false)}
                    onSubmit={handlePriceAlert}
                />
            )}
        </div>
    );
};
