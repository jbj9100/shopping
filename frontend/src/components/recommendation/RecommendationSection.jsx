import { ProductCarousel } from '../common/ProductCarousel';
import './RecommendationSection.css';

export const RecommendationSection = ({ recommendations = [], userId }) => {
    if (!recommendations || recommendations.length === 0) {
        return null;
    }

    // 이유별로 그룹화
    const coViewedProducts = recommendations
        .filter(r => r.reason === 'co-viewed')
        .map(r => r);

    const similarProducts = recommendations
        .filter(r => r.reason === 'similar')
        .map(r => r);

    return (
        <section className="recommendation-section">
            {coViewedProducts.length > 0 && (
                <div className="recommendation-group">
                    <ProductCarousel
                        products={coViewedProducts}
                        title="👀 이 상품을 본 고객이 함께 본 상품"
                    />
                </div>
            )}

            {similarProducts.length > 0 && (
                <div className="recommendation-group">
                    <ProductCarousel
                        products={similarProducts}
                        title="🔍 비슷한 상품 추천"
                    />
                </div>
            )}
        </section>
    );
};
