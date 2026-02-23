import { ProductCard } from './ProductCard';
import './ProductGrid.css';

export const ProductGrid = ({ products, isLoading }) => {
    if (isLoading) {
        return (
            <div className="product-grid-loading">
                <div className="loading-spinner">로딩 중...</div>
            </div>
        );
    }

    if (!products || products.length === 0) {
        return (
            <div className="product-grid-empty">
                <p>상품이 없습니다.</p>
            </div>
        );
    }

    return (
        <div className="product-grid">
            {products.map((product) => (
                <ProductCard key={product.id} product={product} />
            ))}
        </div>
    );
};
