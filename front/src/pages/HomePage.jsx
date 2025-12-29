import { useState, useEffect, useCallback, useRef } from 'react';
import { ProductGrid } from '../components/product/ProductGrid';
import { ProductFilter } from '../components/product/ProductFilter';
import { PriceDropTopN } from '../components/price-drop/PriceDropTopN';
import { RecommendationSection } from '../components/recommendation/RecommendationSection';
import { Badge } from '../components/common/Badge';
import { productService } from '../services/productService';
import { useWebSocket } from '../hooks/useWebSocket';
import './HomePage.css';

export const HomePage = () => {
    const [products, setProducts] = useState([]);
    const [filteredProducts, setFilteredProducts] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const [currentFilters, setCurrentFilters] = useState({});
    const [priceUpdateCount, setPriceUpdateCount] = useState(0);

    // 대량 이벤트 배칭을 위한 ref
    const priceUpdateQueueRef = useRef([]);
    const batchTimerRef = useRef(null);

    // 배칭된 가격 업데이트 처리 (성능 최적화)
    const processPriceUpdates = useCallback(() => {
        if (priceUpdateQueueRef.current.length === 0) return;

        setProducts(prev => {
            let updated = [...prev];
            const updateMap = new Map(
                priceUpdateQueueRef.current.map(u => [u.productId, u.newPrice])
            );

            updated = updated.map(p =>
                updateMap.has(p.id)
                    ? { ...p, price: updateMap.get(p.id), priceChanged: true }
                    : p
            );

            return updated;
        });

        setPriceUpdateCount(priceUpdateQueueRef.current.length);
        priceUpdateQueueRef.current = [];

        // 3초 후 priceChanged 플래그 및 카운터 제거
        setTimeout(() => {
            setProducts(prev => prev.map(p => ({ ...p, priceChanged: false })));
            setPriceUpdateCount(0);
        }, 3000);
    }, []);

    // WebSocket 연결 (실시간 업데이트)
    const { lastMessage } = useWebSocket('ws://localhost:8000/ws', {
        onMessage: (data) => {
            console.log('WebSocket message received:', data);

            // 단일 가격 업데이트 이벤트 - 배칭 처리
            if (data.type === 'PRICE_UPDATE') {
                priceUpdateQueueRef.current.push({
                    productId: data.productId,
                    newPrice: data.newPrice
                });

                // 100ms 내 추가 이벤트를 모아서 한번에 처리
                if (batchTimerRef.current) {
                    clearTimeout(batchTimerRef.current);
                }
                batchTimerRef.current = setTimeout(processPriceUpdates, 100);
            }

            // 대량 가격 업데이트 (Kafka 배치 이벤트)
            if (data.type === 'PRICE_BATCH_UPDATE') {
                priceUpdateQueueRef.current.push(...data.updates);
                if (batchTimerRef.current) {
                    clearTimeout(batchTimerRef.current);
                }
                batchTimerRef.current = setTimeout(processPriceUpdates, 100);
            }

            // 재고 알림 이벤트 처리
            if (data.type === 'STOCK_ALERT') {
                setProducts(prev => prev.map(p =>
                    p.id === data.productId
                        ? { ...p, stock: data.stock }
                        : p
                ));
            }

            // 프로모션 이벤트
            if (data.type === 'PROMOTION') {
                console.log('Promotion:', data.title, data.products);
            }
        },
        onError: (error) => {
            console.log('WebSocket error (백엔드 준비 시 자동 연결)');
        }
    });

    useEffect(() => {
        loadProducts();
    }, []);

    const loadProducts = async () => {
        try {
            setIsLoading(true);
            // 백엔드 상품 API가 아직 없으므로 목업 데이터 사용
            const mockData = getMockProducts();
            setProducts(mockData);
            setFilteredProducts(mockData);

            // 목업 가격 하락 TOP N 데이터
            setPriceTopDrops([
                { productId: 1, name: '슬라이스 식빵 통밀', dropPercent: 22, oldPrice: 2000, newPrice: 1550 },
                { productId: 2, name: '삼립 호빵', dropPercent: 8, oldPrice: 12000, newPrice: 10980 },
                { productId: 7, name: '호밀빵 통호밀', dropPercent: 10, oldPrice: 6500, newPrice: 5800 },
            ]);

            // 목업 추천 데이터
            setRecommendations([
                { id: 3, name: '곰표 우유 식빵, 660g', price: 4050, reason: 'co-viewed', image: null },
                { id: 4, name: '파스쾨르 슬라이스 브리오슈', price: 8980, reason: 'co-viewed', image: null },
                { id: 5, name: '크루아상 플레인', price: 4900, reason: 'similar', image: null },
                { id: 6, name: '바게트 프렌치', price: 3200, reason: 'similar', image: null },
            ]);
        } catch (err) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    // 목업 데이터 (백엔드 준비 전까지)
    const getMockProducts = () => [
        {
            id: 1,
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
            stock: 15
        },
        {
            id: 2,
            name: '삼립 호빵 밤앙금호빵 단팥, 92g, 12개',
            price: 10980,
            originalPrice: 12000,
            discount: 1020,
            brand: '삼립',
            image: null,
            rating: 4.5,
            reviewCount: 58196,
            freeShipping: true,
            rocketShipping: true,
            stock: 8
        },
        {
            id: 3,
            name: '곰표 우유 식빵, 660g, 1개',
            price: 4050,
            brand: '곰표',
            image: null,
            rating: 4.7,
            reviewCount: 320530,
            freeShipping: true,
            rocketShipping: false,
            stock: 25
        },
        {
            id: 4,
            name: '파스쾨르 슬라이스 브리오슈 (냉동), 500g, 1개',
            price: 8980,
            originalPrice: 10000,
            discount: 1020,
            brand: 'Pasquier',
            image: null,
            rating: 4.6,
            reviewCount: 2692,
            freeShipping: true,
            rocketShipping: true,
            stock: 50
        },
        {
            id: 5,
            name: '크루아상 플레인, 70g, 6개',
            price: 4900,
            brand: '베이커리',
            image: null,
            rating: 4.4,
            reviewCount: 892,
            freeShipping: false,
            rocketShipping: false,
            stock: 5
        },
        {
            id: 6,
            name: '바게트 프렌치, 300g, 2개',
            price: 3200,
            brand: '베이커리',
            image: null,
            rating: 4.7,
            reviewCount: 1523,
            freeShipping: false,
            rocketShipping: false,
            stock: 100
        },
        {
            id: 7,
            name: '호밀빵 통호밀, 500g, 1개',
            price: 5800,
            originalPrice: 6500,
            discount: 700,
            brand: 'R.LUX',
            image: null,
            rating: 4.9,
            reviewCount: 3421,
            freeShipping: true,
            rocketShipping: true,
            stock: 30
        },
        {
            id: 8,
            name: '단팥빵 앙버터, 100g, 4개',
            price: 6200,
            brand: '삼립',
            image: null,
            rating: 4.6,
            reviewCount: 5234,
            freeShipping: true,
            rocketShipping: false,
            stock: 12
        }
    ];

    // 필터 적용 로직
    const handleFilterChange = useCallback((filters) => {
        setCurrentFilters(filters);

        let filtered = [...products];

        // 가격대 필터
        if (filters.priceRange) {
            filtered = filtered.filter(p =>
                p.price >= filters.priceRange.start &&
                p.price <= filters.priceRange.end
            );
        }

        // 배송 필터
        if (filters.shipping && filters.shipping.length > 0) {
            filtered = filtered.filter(p => {
                if (filters.shipping.includes('free') && filters.shipping.includes('rocket')) {
                    return p.freeShipping || p.rocketShipping;
                }
                if (filters.shipping.includes('free')) {
                    return p.freeShipping;
                }
                if (filters.shipping.includes('rocket')) {
                    return p.rocketShipping;
                }
                return true;
            });
        }

        // 브랜드 필터
        if (filters.brands && filters.brands.length > 0) {
            filtered = filtered.filter(p => filters.brands.includes(p.brand));
        }

        setFilteredProducts(filtered);
    }, [products]);

    // products 변경 시 필터 재적용
    useEffect(() => {
        handleFilterChange(currentFilters);
    }, [products, currentFilters, handleFilterChange]);

    return (
        <div className="home-page">
            {/* 프로모션 배너 */}
            <section className="promotion-banner">
                <div className="container">
                    <div className="promotion-content">
                        <h2 className="promotion-title">🎉 베이커리 특가 세일!</h2>
                        <p className="promotion-subtitle">신선한 빵, 매일 최저가 + 무료배송</p>
                    </div>
                </div>
            </section>

            {/* 카테고리 아이콘 */}
            <section className="category-icons">
                <div className="container">
                    <div className="category-icons-grid">
                        <CategoryIcon icon="🍞" label="식빵/곡물빵" />
                        <CategoryIcon icon="🥖" label="양빵/일반빵" />
                        <CategoryIcon icon="🥐" label="샌드위치/버거" />
                        <CategoryIcon icon="🍰" label="쿠키/파이" />
                        <CategoryIcon icon="🧁" label="케이크/제과" />
                        <CategoryIcon icon="🍪" label="생지" />
                        <CategoryIcon icon="🍩" label="베이커리 선물세트" />
                        <CategoryIcon icon="🥧" label="잼/꿀/시럽" />
                    </div>
                </div>
            </section>

            {/* 메인 콘텐츠 (필터 + 상품 목록) */}
            <section className="main-content-section">
                <div className="container">
                    {priceUpdateCount > 0 && (
                        <div className="price-update-alert">
                            ⚡ {priceUpdateCount}개 상품 가격이 실시간 업데이트 되었습니다!
                        </div>
                    )}

                    <div className="content-layout">
                        {/* 왼쪽: 필터 사이드바 */}
                        <aside className="filter-sidebar">
                            <ProductFilter
                                products={products}
                                onFilterChange={handleFilterChange}
                                priceUpdateCount={priceUpdateCount}
                            />
                        </aside>

                        {/* 오른쪽: 상품 목록 */}
                        <main className="products-main">
                            <div className="section-header">
                                <h2 className="section-title">
                                    베이커리 카테고리
                                    <span className="product-count">({filteredProducts.length}개 상품)</span>
                                </h2>
                                <Badge variant="primary">실시간 업데이트</Badge>
                            </div>

                            {error && (
                                <div className="error-message">
                                    <p>⚠️ {error}</p>
                                    <p className="error-note">개발 중: 목업 데이터를 표시합니다</p>
                                </div>
                            )}

                            <ProductGrid products={filteredProducts} isLoading={isLoading} />
                        </main>
                    </div>
                </div>
            </section>
        </div>
    );
};

const CategoryIcon = ({ icon, label }) => (
    <div className="category-icon-item">
        <div className="category-icon-circle">{icon}</div>
        <span className="category-icon-label">{label}</span>
    </div>
);
