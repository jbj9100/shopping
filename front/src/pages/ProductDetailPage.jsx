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
            // 곰표 우유식빵 660g Mock 데이터
            if (id === '1') {
                setProduct({
                    id: 1,
                    name: '곰표 우유 식빵 660g',
                    price: 4050,
                    original_price: 5000,
                    brand: '곰표',
                    category_id: 1,
                    image: null,
                    free_shipping: true,
                    stock: 25,
                    depletionEtaMinutes: 12,
                    description: `촉촉하고 부드러운 곰표 우유 식빵입니다.

**제품 특징**
- 신선한 우유를 듬뿍 넣어 더욱 촉촉하고 부드러워요
- 100% 국내산 밀가루 사용
- 인공색소, 인공향료 무첨가
- 아이들 간식으로 좋아요

**제품 정보**
- 용량: 660g
- 원재료: 밀가루, 우유, 설탕, 버터, 이스트, 소금
- 보관방법: 실온보관 (개봉 후 냉장보관)
- 유통기한: 제조일로부터 7일`,
                    additionalInfo: {
                        nutrition: '1회 제공량(33g) 기준 - 열량 90kcal, 나트륨 190mg, 탄수화물 17g, 당류 3g, 지방 1.5g, 단백질 3g',
                        origin: '국내산',
                        manufacturer: '곰표제과',
                        customerService: '1588-0000'
                    }
                });

                setRecommendations([
                    { id: 2, name: '신라면 멀티팩 5개입', price: 4480, reason: 'co-viewed', brand: '농심', image: null },
                    { id: 3, name: '제주 감귤 3kg', price: 19800, reason: 'similar', brand: '제주농협', image: null },
                    { id: 4, name: '코카콜라 제로 500ml 24개', price: 22900, reason: 'co-viewed', brand: '코카콜라', image: null }
                ]);
            } else {
                // 다른 상품 기본 Mock
                setProduct({
                    id: Number(id),
                    name: '상품 이름',
                    price: 10000,
                    original_price: 15000,
                    brand: '브랜드명',
                    image: null,
                    free_shipping: true,
                    stock: 50,
                    description: '상품 설명입니다.'
                });
            }
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

    // discount 계산 (original_price - price)
    const discount = product.original_price ? product.original_price - product.price : 0;
    const discountPercent = discount > 0 ? Math.round((discount / product.original_price) * 100) : 0;

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

                        {(product.rating || product.review_count) && (
                            <div className="product-rating-section">
                                <span className="product-stars">⭐ {product.rating?.toFixed(1)}</span>
                                {product.review_count > 0 && (
                                    <span className="product-reviews">
                                        리뷰 {product.review_count.toLocaleString()}개
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
                                        {product.original_price.toLocaleString()}원
                                    </div>
                                </>
                            )}
                            <div className="product-current-price">
                                {product.price.toLocaleString()}원
                            </div>
                        </div>

                        {/* 배송 */}
                        <div className="product-shipping-section">
                            {product.free_shipping && (
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
                    <p style={{ whiteSpace: 'pre-line' }}>{product.description}</p>

                    {product.additionalInfo && (
                        <div className="product-additional-info" style={{ marginTop: '2rem', borderTop: '1px solid #eee', paddingTop: '1rem' }}>
                            <h3>추가 정보</h3>
                            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                                <tbody>
                                    {product.additionalInfo.nutrition && (
                                        <tr style={{ borderBottom: '1px solid #f0f0f0' }}>
                                            <td style={{ padding: '0.75rem', fontWeight: 'bold', width: '150px' }}>영양성분</td>
                                            <td style={{ padding: '0.75rem' }}>{product.additionalInfo.nutrition}</td>
                                        </tr>
                                    )}
                                    {product.additionalInfo.origin && (
                                        <tr style={{ borderBottom: '1px solid #f0f0f0' }}>
                                            <td style={{ padding: '0.75rem', fontWeight: 'bold' }}>원산지</td>
                                            <td style={{ padding: '0.75rem' }}>{product.additionalInfo.origin}</td>
                                        </tr>
                                    )}
                                    {product.additionalInfo.manufacturer && (
                                        <tr style={{ borderBottom: '1px solid #f0f0f0' }}>
                                            <td style={{ padding: '0.75rem', fontWeight: 'bold' }}>제조사</td>
                                            <td style={{ padding: '0.75rem' }}>{product.additionalInfo.manufacturer}</td>
                                        </tr>
                                    )}
                                    {product.additionalInfo.customerService && (
                                        <tr style={{ borderBottom: '1px solid #f0f0f0' }}>
                                            <td style={{ padding: '0.75rem', fontWeight: 'bold' }}>고객센터</td>
                                            <td style={{ padding: '0.75rem' }}>{product.additionalInfo.customerService}</td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                    )}
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
