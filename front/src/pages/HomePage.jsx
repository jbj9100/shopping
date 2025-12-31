import { useState, useEffect, useCallback, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { ProductGrid } from '../components/product/ProductGrid';
import { ProductFilter } from '../components/product/ProductFilter';
import { PriceDropTopN } from '../components/price-drop/PriceDropTopN';
import { RecommendationSection } from '../components/recommendation/RecommendationSection';
import { Badge } from '../components/common/Badge';
import { productService } from '../services/productService';
import { useWebSocket } from '../hooks/useWebSocket';
import './HomePage.css';

export const HomePage = () => {
    const { category } = useParams(); // URL에서 카테고리 파라미터 추출
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
    }, [category]); // 카테고리 변경 시 다시 로드

    const loadProducts = async () => {
        try {
            setIsLoading(true);
            // 백엔드 상품 API가 아직 없으므로 목업 데이터 사용
            let mockData = getMockProducts();

            // URL에 카테고리가 있으면 해당 카테고리만 필터링
            if (category) {
                mockData = mockData.filter(p => p.category === category);
            }

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

    // 목업 데이터 (백엔드 준비 전까지) - 10개 카테고리 × 4개 상품 = 40개
    const getMockProducts = () => [
        // 식품 (food)
        { id: 1, category: 'food', name: '곰표 우유 식빵 660g', price: 4050, originalPrice: 5000, discount: 950, brand: '곰표', image: null, rating: 4.7, reviewCount: 32053, freeShipping: true, rocketShipping: false, stock: 25 },
        { id: 2, category: 'food', name: '신라면 멀티팩 5개입', price: 4480, originalPrice: 5500, discount: 1020, brand: '농심', image: null, rating: 4.8, reviewCount: 15234, freeShipping: true, rocketShipping: true, stock: 100 },
        { id: 3, category: 'food', name: '제주 감귤 3kg', price: 19800, originalPrice: 25000, discount: 5200, brand: '제주농협', image: null, rating: 4.6, reviewCount: 8921, freeShipping: true, rocketShipping: false, stock: 50 },
        { id: 4, category: 'food', name: '코카콜라 제로 500ml 24개', price: 22900, brand: '코카콜라', image: null, rating: 4.9, reviewCount: 45123, freeShipping: true, rocketShipping: true, stock: 200 },

        // 생활용품 (living)
        { id: 5, category: 'living', name: '다우니 섬유유연제 3.2L', price: 15900, originalPrice: 19900, discount: 4000, brand: '다우니', image: null, rating: 4.8, reviewCount: 28901, freeShipping: true, rocketShipping: true, stock: 150 },
        { id: 6, category: 'living', name: '코멧 3겹 화장지 30롤', price: 18900, brand: '코멧', image: null, rating: 4.7, reviewCount: 52341, freeShipping: true, rocketShipping: true, stock: 200 },
        { id: 7, category: 'living', name: '페리오 치약 클리닉 3개', price: 8900, originalPrice: 11900, discount: 3000, brand: 'LG생활건강', image: null, rating: 4.6, reviewCount: 15678, freeShipping: true, rocketShipping: false, stock: 100 },
        { id: 8, category: 'living', name: '테크 세탁세제 리필 2.4L', price: 12900, brand: 'LG생활건강', image: null, rating: 4.5, reviewCount: 34521, freeShipping: true, rocketShipping: true, stock: 80 },

        // 뷰티 (beauty)
        { id: 9, category: 'beauty', name: '아이오페 레티놀 세럼 30ml', price: 52000, originalPrice: 65000, discount: 13000, brand: 'IOPE', image: null, rating: 4.8, reviewCount: 9234, freeShipping: true, rocketShipping: true, stock: 40 },
        { id: 10, category: 'beauty', name: '라로슈포제 선크림 50ml', price: 24900, brand: '라로슈포제', image: null, rating: 4.7, reviewCount: 18567, freeShipping: true, rocketShipping: false, stock: 70 },
        { id: 11, category: 'beauty', name: '메디힐 마스크팩 10매', price: 9900, originalPrice: 15000, discount: 5100, brand: '메디힐', image: null, rating: 4.6, reviewCount: 45678, freeShipping: true, rocketShipping: true, stock: 200 },
        { id: 12, category: 'beauty', name: 'MAC 립스틱 레드', price: 33000, brand: 'MAC', image: null, rating: 4.9, reviewCount: 7821, freeShipping: false, rocketShipping: false, stock: 25 },

        // 홈인테리어 (interior)
        { id: 13, category: 'interior', name: '이케아 LED 스탠드', price: 29900, brand: 'IKEA', image: null, rating: 4.5, reviewCount: 4532, freeShipping: false, rocketShipping: false, stock: 30 },
        { id: 14, category: 'interior', name: '무인양품 소파쿠션', price: 19900, originalPrice: 25000, discount: 5100, brand: 'MUJI', image: null, rating: 4.6, reviewCount: 3421, freeShipping: true, rocketShipping: false, stock: 45 },
        { id: 15, category: 'interior', name: '자라홈 러그 150x200', price: 89000, brand: '자라홈', image: null, rating: 4.4, reviewCount: 1892, freeShipping: false, rocketShipping: false, stock: 15 },
        { id: 16, category: 'interior', name: '모던하우스 벽시계', price: 24900, originalPrice: 32000, discount: 7100, brand: '모던하우스', image: null, rating: 4.3, reviewCount: 2341, freeShipping: true, rocketShipping: true, stock: 40 },

        // 가전디지털 (electronics)
        { id: 17, category: 'electronics', name: '애플 맥북 에어 M3', price: 1590000, originalPrice: 1690000, discount: 100000, brand: 'Apple', image: null, rating: 4.9, reviewCount: 8934, freeShipping: true, rocketShipping: false, stock: 15 },
        { id: 18, category: 'electronics', name: '삼성 갤럭시 버즈 FE', price: 89000, brand: '삼성', image: null, rating: 4.7, reviewCount: 12456, freeShipping: true, rocketShipping: true, stock: 80 },
        { id: 19, category: 'electronics', name: 'LG 울트라기어 27인치', price: 329000, originalPrice: 400000, discount: 71000, brand: 'LG', image: null, rating: 4.8, reviewCount: 5678, freeShipping: true, rocketShipping: false, stock: 25 },
        { id: 20, category: 'electronics', name: '아이패드 10세대 64GB', price: 599000, brand: 'Apple', image: null, rating: 4.9, reviewCount: 23456, freeShipping: true, rocketShipping: true, stock: 30 },

        // 주방용품 (kitchen)
        { id: 21, category: 'kitchen', name: '휘슬러 압력솥 6L', price: 289000, originalPrice: 350000, discount: 61000, brand: '휘슬러', image: null, rating: 4.8, reviewCount: 3456, freeShipping: true, rocketShipping: false, stock: 20 },
        { id: 22, category: 'kitchen', name: '테팔 프라이팬 28cm', price: 39900, brand: '테팔', image: null, rating: 4.6, reviewCount: 18234, freeShipping: true, rocketShipping: true, stock: 100 },
        { id: 23, category: 'kitchen', name: '코렐 접시세트 16P', price: 79000, originalPrice: 99000, discount: 20000, brand: '코렐', image: null, rating: 4.7, reviewCount: 5678, freeShipping: true, rocketShipping: false, stock: 35 },
        { id: 24, category: 'kitchen', name: '쿠쿠 전기밥솥 10인용', price: 189000, originalPrice: 250000, discount: 61000, brand: '쿠쿠', image: null, rating: 4.8, reviewCount: 8901, freeShipping: true, rocketShipping: false, stock: 25 },

        // 반려동물 (pet)
        { id: 25, category: 'pet', name: '로얄캐닌 사료 3kg', price: 32900, originalPrice: 39900, discount: 7000, brand: '로얄캐닌', image: null, rating: 4.8, reviewCount: 12345, freeShipping: true, rocketShipping: true, stock: 100 },
        { id: 26, category: 'pet', name: '하림펫푸드 간식 300g', price: 8900, brand: '하림', image: null, rating: 4.6, reviewCount: 8765, freeShipping: true, rocketShipping: false, stock: 150 },
        { id: 27, category: 'pet', name: '캣타워 대형 180cm', price: 89000, originalPrice: 120000, discount: 31000, brand: '펫모닝', image: null, rating: 4.7, reviewCount: 3456, freeShipping: false, rocketShipping: false, stock: 20 },
        { id: 28, category: 'pet', name: '강아지 패드 100매', price: 19900, brand: '코멧', image: null, rating: 4.5, reviewCount: 23456, freeShipping: true, rocketShipping: true, stock: 200 },

        // 스포츠/레저 (sports)
        { id: 29, category: 'sports', name: '나이키 에어맥스 270', price: 169000, originalPrice: 199000, discount: 30000, brand: 'Nike', image: null, rating: 4.8, reviewCount: 12345, freeShipping: true, rocketShipping: false, stock: 40 },
        { id: 30, category: 'sports', name: '요가매트 NBR 10mm', price: 19900, brand: '에바', image: null, rating: 4.6, reviewCount: 8765, freeShipping: true, rocketShipping: true, stock: 100 },
        { id: 31, category: 'sports', name: '덤벨 세트 20kg', price: 89000, originalPrice: 120000, discount: 31000, brand: '헬스메이트', image: null, rating: 4.7, reviewCount: 5678, freeShipping: false, rocketShipping: false, stock: 30 },
        { id: 32, category: 'sports', name: '캠핑 텐트 4인용', price: 159000, originalPrice: 200000, discount: 41000, brand: '코베아', image: null, rating: 4.8, reviewCount: 3456, freeShipping: true, rocketShipping: false, stock: 20 },

        // 도서/음반 (books)
        { id: 33, category: 'books', name: '트렌드 코리아 2025', price: 17100, originalPrice: 19000, discount: 1900, brand: '미래의창', image: null, rating: 4.9, reviewCount: 23456, freeShipping: true, rocketShipping: true, stock: 200 },
        { id: 34, category: 'books', name: '아웃라이어', price: 15300, brand: '김영사', image: null, rating: 4.8, reviewCount: 34567, freeShipping: true, rocketShipping: false, stock: 150 },
        { id: 35, category: 'books', name: 'BTS 앨범 정규 4집', price: 45000, originalPrice: 50000, discount: 5000, brand: 'HYBE', image: null, rating: 4.9, reviewCount: 67890, freeShipping: true, rocketShipping: true, stock: 100 },
        { id: 36, category: 'books', name: '해리포터 전집 세트', price: 89000, brand: '문학수첩', image: null, rating: 4.9, reviewCount: 12345, freeShipping: true, rocketShipping: false, stock: 40 },

        // 헬스/건강 (health)
        { id: 37, category: 'health', name: '종근당 비타민C 1000', price: 19900, originalPrice: 25000, discount: 5100, brand: '종근당', image: null, rating: 4.7, reviewCount: 28901, freeShipping: true, rocketShipping: true, stock: 150 },
        { id: 38, category: 'health', name: '락토핏 유산균 60포', price: 23900, brand: '종근당', image: null, rating: 4.8, reviewCount: 45678, freeShipping: true, rocketShipping: false, stock: 200 },
        { id: 39, category: 'health', name: '홍삼정 에브리타임', price: 89000, originalPrice: 110000, discount: 21000, brand: '정관장', image: null, rating: 4.9, reviewCount: 12345, freeShipping: true, rocketShipping: true, stock: 60 },
        { id: 40, category: 'health', name: '오메가3 120캡슐', price: 29900, brand: '뉴트리원', image: null, rating: 4.6, reviewCount: 8765, freeShipping: true, rocketShipping: false, stock: 100 }
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
