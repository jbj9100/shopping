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
        originalPrice,
        discount,
        image,
        rating,
        reviewCount,
        freeShipping,
        rocketShipping,
        stock,
        priceChanged,
        brand,
        depletionEtaMinutes,
        isAnomalous
    } = product;

    const discountPercent = discount ? Math.round((discount / originalPrice) * 100) : 0;

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
                    {discountPercent > 0 && !isAnomalous && (
                        <Badge variant="error" className="product-card-discount-badge">
                            {discountPercent}%
                        </Badge>
                    )}
                    {isAnomalous && (
                        <Badge variant="default" className="product-card-status-badge">
                            일시 품절
                        </Badge>
                    )}
                    {stock < 10 && stock > 0 && !isAnomalous && (
                        <Badge variant="warning" className="product-card-stock-badge">
                            재고 {stock}개
                        </Badge>
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
                        {originalPrice && discountPercent > 0 ? (
                            <>
                                <span className="product-card-original-price">
                                    {originalPrice.toLocaleString()}원
                                </span>
                                <span className="product-card-price">
                                    {price.toLocaleString()}원
                                </span>
                            </>
                        ) : (
                            <span className="product-card-price">
                                {price.toLocaleString()}원
                            </span>
                        )}
                    </div>

                    {(rating || reviewCount) && (
                        <div className="product-card-rating">
                            <span className="product-card-stars">⭐ {rating?.toFixed(1)}</span>
                            {reviewCount > 0 && (
                                <span className="product-card-reviews">({reviewCount.toLocaleString()})</span>
                            )}
                        </div>
                    )}

                    <div className="product-card-shipping">
                        {rocketShipping && (
                            <Badge variant="primary" size="small">로켓배송</Badge>
                        )}
                        {freeShipping && !rocketShipping && (
                            <Badge variant="success" size="small">무료배송</Badge>
                        )}
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
