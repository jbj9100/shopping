import { Link } from 'react-router-dom';
import { Card } from '../common/Card';
import { Badge } from '../common/Badge';
import { StockDepletionBadge } from '../stock/StockDepletionBadge';
import './ProductCard.css';

export const ProductCard = ({ product }) => {
    const {
        id,
        name,
        price,
        original_price,
        discount_percent, // 백엔드에서 계산된 값 사용
        image,
        rating,
        review_count,
        view_count,  // 조회수 추가
        free_shipping,
        stock,
        priceChanged,
        brand,
        depletionEtaMinutes,
        isAnomalous
    } = product;

    return (
        <Link
            to={isAnomalous ? '#' : `/products/${id}`}
            className={`product-card-link ${isAnomalous ? 'disabled' : ''}`}
            onClick={(e) => isAnomalous && e.preventDefault()}
        >
            <Card hover={!isAnomalous} padding="none" className={`product-card ${priceChanged ? 'price-changed' : ''} ${isAnomalous ? 'anomalous' : ''}`}>
                <div className="product-card-image-wrapper">
                    {image ? (
                        <img src={image} alt={name} className="product-card-image" />
                    ) : (
                        <div className="product-card-image-placeholder">🍞</div>
                    )}
                    {isAnomalous && (
                        <Badge variant="default" className="product-card-status-badge">
                            일시 품절
                        </Badge>
                    )}
                    {/* 재고 0개일 때 OUT OF STOCK 오버레이 */}
                    {stock === 0 && !isAnomalous && (
                        <div className="product-card-out-of-stock-overlay">
                            <div className="out-of-stock-stamp">
                                OUT OF STOCK
                            </div>
                        </div>
                    )}
                </div>

                <div className="product-card-content">
                    {/* 품절 예측 배지 */}
                    {depletionEtaMinutes && !isAnomalous && (
                        <div className="product-card-depletion">
                            <StockDepletionBadge depletionEtaMinutes={depletionEtaMinutes} />
                        </div>
                    )}

                    <h3 className="product-card-title">{name}</h3>

                    <div className="product-card-price-wrapper">
                        {original_price && discount_percent > 0 ? (
                            <>
                                <span className="product-card-original-price">
                                    {original_price.toLocaleString()}원
                                </span>
                                <div className="product-card-sale-price">
                                    <span className="product-card-price">
                                        {price.toLocaleString()}원
                                    </span>
                                    <Badge variant="error" size="small" className="product-card-discount-chip">
                                        {discount_percent}%
                                    </Badge>
                                </div>
                            </>
                        ) : (
                            <span className="product-card-price">
                                {price.toLocaleString()}원
                            </span>
                        )}
                    </div>

                    {(rating || review_count) && (
                        <div className="product-card-rating">
                            <span className="product-card-stars">⭐ {rating?.toFixed(1)}</span>
                            {review_count > 0 && (
                                <span className="product-card-reviews">({review_count.toLocaleString()})</span>
                            )}
                        </div>
                    )}

                    <div className="product-card-shipping">
                        {free_shipping && (
                            <Badge variant="success" size="small">무료배송</Badge>
                        )}
                        {/* 재고 정보 항상 표시 */}
                        {!isAnomalous && (
                            <Badge
                                variant={stock === 0 ? 'error' : stock < 10 ? 'warning' : 'default'}
                                size="small"
                            >
                                재고 {stock}개
                            </Badge>
                        )}
                    </div>

                    {/* 조회수 표시 */}
                    <div className="product-card-meta">
                        <span className="product-card-view-count">
                            👁️ {view_count?.toLocaleString() || 0}
                        </span>
                    </div>

                    {isAnomalous && (
                        <div className="product-card-anomaly-notice">
                            일시적으로 판매가 중단되었습니다
                        </div>
                    )}
                </div>
            </Card>
        </Link>
    );
};
