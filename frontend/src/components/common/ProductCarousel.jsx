import './ProductCarousel.css';
import { useState } from 'react';

export const ProductCarousel = ({ products, title }) => {
    const [currentIndex, setCurrentIndex] = useState(0);

    if (!products || products.length === 0) {
        return null;
    }

    const itemsPerSlide = 4;
    const totalSlides = Math.ceil(products.length / itemsPerSlide);

    const handlePrev = () => {
        setCurrentIndex((prev) => (prev === 0 ? totalSlides - 1 : prev - 1));
    };

    const handleNext = () => {
        setCurrentIndex((prev) => (prev === totalSlides - 1 ? 0 : prev + 1));
    };

    const visibleProducts = products.slice(
        currentIndex * itemsPerSlide,
        (currentIndex + 1) * itemsPerSlide
    );

    return (
        <div className="product-carousel">
            {title && <h3 className="carousel-title">{title}</h3>}

            <div className="carousel-container">
                <button
                    className="carousel-button carousel-button-prev"
                    onClick={handlePrev}
                    aria-label="이전"
                >
                    ‹
                </button>

                <div className="carousel-track">
                    {visibleProducts.map((product) => (
                        <div key={product.id} className="carousel-item">
                            <a href={`/products/${product.id}`} className="carousel-product-link">
                                <div className="carousel-product-image">
                                    {product.image ? (
                                        <img src={product.image} alt={product.name} />
                                    ) : (
                                        <div className="carousel-product-placeholder">🍞</div>
                                    )}
                                </div>
                                <div className="carousel-product-info">
                                    <h4 className="carousel-product-name">{product.name}</h4>
                                    <p className="carousel-product-price">
                                        {product.price.toLocaleString()}원
                                    </p>
                                </div>
                            </a>
                        </div>
                    ))}
                </div>

                <button
                    className="carousel-button carousel-button-next"
                    onClick={handleNext}
                    aria-label="다음"
                >
                    ›
                </button>
            </div>

            <div className="carousel-indicators">
                {Array.from({ length: totalSlides }).map((_, index) => (
                    <button
                        key={index}
                        className={`carousel-indicator ${index === currentIndex ? 'active' : ''}`}
                        onClick={() => setCurrentIndex(index)}
                        aria-label={`슬라이드 ${index + 1}`}
                    />
                ))}
            </div>
        </div>
    );
};
