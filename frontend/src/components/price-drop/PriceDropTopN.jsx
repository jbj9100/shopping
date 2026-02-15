import { Card } from '../common/Card';
import { Badge } from '../common/Badge';
import './PriceDropTopN.css';
import { Link } from 'react-router-dom';

export const PriceDropTopN = ({ topProducts = [] }) => {
    if (!topProducts || topProducts.length === 0) {
        return null;
    }

    return (
        <section className="price-drop-top-n">
            <div className="top-n-header">
                <h2 className="top-n-title">🔥 지금 가장 많이 떨어진 상품 TOP 10</h2>
                <Badge variant="error">실시간</Badge>
            </div>

            <div className="top-n-grid">
                {topProducts.slice(0, 10).map((product, index) => (
                    <Link
                        key={product.productId}
                        to={`/products/${product.productId}`}
                        className="top-n-item-link"
                    >
                        <Card hover className="top-n-item">
                            <div className="top-n-rank">{index + 1}</div>

                            <div className="top-n-content">
                                <h3 className="top-n-product-name">{product.name || `상품 ${product.productId}`}</h3>

                                <div className="top-n-prices">
                                    <span className="top-n-old-price">
                                        {product.oldPrice.toLocaleString()}원
                                    </span>
                                    <span className="top-n-arrow">→</span>
                                    <span className="top-n-new-price">
                                        {product.newPrice.toLocaleString()}원
                                    </span>
                                </div>

                                <div className="top-n-drop">
                                    <Badge variant="error" size="large">
                                        ⬇️ {product.dropPercent}% 하락
                                    </Badge>
                                    <span className="top-n-drop-amount">
                                        {(product.oldPrice - product.newPrice).toLocaleString()}원 할인
                                    </span>
                                </div>
                            </div>
                        </Card>
                    </Link>
                ))}
            </div>
        </section>
    );
};
