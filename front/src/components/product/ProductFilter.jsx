import { useState, useEffect, useMemo } from 'react';
import { Card } from '../common/Card';
import { Badge } from '../common/Badge';
import './ProductFilter.css';

export const ProductFilter = ({
    products,
    onFilterChange,
    priceUpdateCount = 0 // 실시간 가격 업데이트 카운터
}) => {
    const [selectedPriceRange, setSelectedPriceRange] = useState(null);
    const [selectedShipping, setSelectedShipping] = useState([]);
    const [selectedBrands, setSelectedBrands] = useState([]);

    // 실시간 가격대 범위 자동 계산
    const priceRanges = useMemo(() => {
        if (!products || products.length === 0) return [];

        const prices = products.map(p => p.price);
        const minPrice = Math.min(...prices);
        const maxPrice = Math.max(...prices);
        const range = maxPrice - minPrice;
        const step = Math.ceil(range / 5 / 10000) * 10000; // 만원 단위로 반올림

        const ranges = [];
        for (let i = 0; i < 5; i++) {
            const start = minPrice + (step * i);
            const end = i === 4 ? maxPrice : minPrice + (step * (i + 1));

            // 해당 범위에 속하는 상품 개수
            const count = products.filter(p => p.price >= start && p.price <= end).length;

            if (count > 0) {
                ranges.push({
                    id: i,
                    start,
                    end,
                    count,
                    label: `${(start / 10000).toFixed(0)}만원 - ${(end / 10000).toFixed(0)}만원`
                });
            }
        }

        return ranges;
    }, [products, priceUpdateCount]); // 가격 업데이트마다 재계산

    // 브랜드 목록 추출
    const brands = useMemo(() => {
        if (!products) return [];
        const brandSet = new Set(products.map(p => p.brand).filter(Boolean));
        return Array.from(brandSet).map(brand => ({
            name: brand,
            count: products.filter(p => p.brand === brand).length
        }));
    }, [products]);

    // 필터 적용
    useEffect(() => {
        const filters = {
            priceRange: selectedPriceRange,
            shipping: selectedShipping,
            brands: selectedBrands
        };
        onFilterChange?.(filters);
    }, [selectedPriceRange, selectedShipping, selectedBrands, onFilterChange]);

    const handlePriceRangeChange = (range) => {
        setSelectedPriceRange(selectedPriceRange?.id === range.id ? null : range);
    };

    const handleShippingChange = (option) => {
        setSelectedShipping(prev =>
            prev.includes(option)
                ? prev.filter(s => s !== option)
                : [...prev, option]
        );
    };

    const handleBrandChange = (brand) => {
        setSelectedBrands(prev =>
            prev.includes(brand)
                ? prev.filter(b => b !== brand)
                : [...prev, brand]
        );
    };

    const resetFilters = () => {
        setSelectedPriceRange(null);
        setSelectedShipping([]);
        setSelectedBrands([]);
    };

    return (
        <div className="product-filter">
            <div className="filter-header">
                <h3 className="filter-title">필터</h3>
                <button className="filter-reset" onClick={resetFilters}>
                    초기화
                </button>
            </div>

            {/* 가격대 필터 */}
            <Card className="filter-section">
                <div className="filter-section-header">
                    <h4 className="filter-section-title">가격대</h4>
                    {priceUpdateCount > 0 && (
                        <Badge variant="primary" size="small" className="price-update-badge">
                            {priceUpdateCount}개 업데이트
                        </Badge>
                    )}
                </div>

                <div className="filter-options">
                    {priceRanges.map((range) => (
                        <label
                            key={range.id}
                            className={`filter-option ${selectedPriceRange?.id === range.id ? 'filter-option-active' : ''
                                }`}
                        >
                            <input
                                type="checkbox"
                                checked={selectedPriceRange?.id === range.id}
                                onChange={() => handlePriceRangeChange(range)}
                                className="filter-checkbox"
                            />
                            <span className="filter-label">
                                {range.label}
                                <span className="filter-count">({range.count})</span>
                            </span>
                        </label>
                    ))}
                </div>
            </Card>

            {/* 배송 옵션 */}
            <Card className="filter-section">
                <h4 className="filter-section-title">배송</h4>
                <div className="filter-options">
                    <label className={`filter-option ${selectedShipping.includes('free') ? 'filter-option-active' : ''}`}>
                        <input
                            type="checkbox"
                            checked={selectedShipping.includes('free')}
                            onChange={() => handleShippingChange('free')}
                            className="filter-checkbox"
                        />
                        <span className="filter-label">무료배송</span>
                    </label>
                    <label className={`filter-option ${selectedShipping.includes('rocket') ? 'filter-option-active' : ''}`}>
                        <input
                            type="checkbox"
                            checked={selectedShipping.includes('rocket')}
                            onChange={() => handleShippingChange('rocket')}
                            className="filter-checkbox"
                        />
                        <span className="filter-label">로켓배송</span>
                    </label>
                </div>
            </Card>

            {/* 브랜드 필터 */}
            {brands.length > 0 && (
                <Card className="filter-section">
                    <h4 className="filter-section-title">브랜드</h4>
                    <div className="filter-options filter-options-scrollable">
                        {brands.slice(0, 10).map((brand) => (
                            <label
                                key={brand.name}
                                className={`filter-option ${selectedBrands.includes(brand.name) ? 'filter-option-active' : ''}`}
                            >
                                <input
                                    type="checkbox"
                                    checked={selectedBrands.includes(brand.name)}
                                    onChange={() => handleBrandChange(brand.name)}
                                    className="filter-checkbox"
                                />
                                <span className="filter-label">
                                    {brand.name}
                                    <span className="filter-count">({brand.count})</span>
                                </span>
                            </label>
                        ))}
                    </div>
                </Card>
            )}
        </div>
    );
};
