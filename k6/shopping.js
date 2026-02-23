import http from 'k6/http';
import { sleep, check } from 'k6';
import { SharedArray } from 'k6/data';
import papaparse from 'https://jslib.k6.io/papaparse/5.1.1/index.js';

//----------------------------------------------------------
// Configuration
//----------------------------------------------------------
const BASE_URL = 'https://shopping.project.com';
const API_SHOP = `${BASE_URL}/api/shop`;
const API_CARTS = `${BASE_URL}/api/carts`;
const API_ORDERS = `${BASE_URL}/api/shop/orders`;

// CSV에서 사용자 정보 로드
const users = new SharedArray('users', function () {
    return papaparse.parse(open('./users.csv'), { header: true }).data;
});

//----------------------------------------------------------
// Load Scenario Options
//----------------------------------------------------------
export const options = {
    insecureSkipTLSVerify: true,
    scenarios: {
        shopping_flow: {
            executor: 'ramping-vus',
            startVUs: 0,
            stages: [
                { duration: '30s', target: 10 },    // 워밍업
                { duration: '1m', target: 50 },     // 50명까지 증가
                { duration: '2m', target: 50 },     // 50명 유지
                { duration: '30s', target: 100 },   // 100명까지 스파이크
                { duration: '1m', target: 100 },    // 100명 유지
                { duration: '30s', target: 0 },     // 종료
            ],
        },
    },
    thresholds: {
        http_req_failed: ['rate<0.10'],       // 에러율 10% 미만
        http_req_duration: ['p(95)<5000'],    // 95% 요청이 5초 미만
    },
};

//----------------------------------------------------------
// Setup: 상품 목록 가져오기
//----------------------------------------------------------
export function setup() {
    const res = http.get(`${API_SHOP}/products/`, { insecureSkipTLSVerify: true });

    if (res.status !== 200) {
        console.error(`Failed to fetch products: ${res.status}`);
        return { productIds: [] };
    }

    const products = res.json();
    if (!products || products.length === 0) {
        console.error('No products found in database!');
        return { productIds: [] };
    }

    const productIds = products.map(p => p.id);
    console.log(`Setup: Loaded ${productIds.length} products, IDs: ${productIds.slice(0, 10).join(', ')}...`);
    return { productIds };
}

//----------------------------------------------------------
// Main Test Function: 쇼핑 플로우
//----------------------------------------------------------
export default function (data) {
    const { productIds } = data;

    if (!productIds || productIds.length === 0) {
        console.error('No products available. Exiting test.');
        return;
    }

    // ✅ VU별로 독립적인 쿠키 jar 생성 (Refresh Token 저장용)
    const jar = http.cookieJar();
    jar.set(BASE_URL, 'session', 'vu' + __VU);

    // VU별로 다른 사용자 선택 (순환)
    const user = users[__VU % users.length];
    const { email, password } = user;

    // 1️⃣ 로그인 (Refresh Token이 HttpOnly Cookie로 jar에 자동 저장됨)
    const tokens = login(email, password, jar);
    if (!tokens) {
        console.error(`[VU ${__VU}] Login failed for ${email}`);
        return;
    }

    sleep(1);

    // 2️⃣ 상품 선택 (랜덤으로 1~3개)
    const numProductsToAdd = randomIntBetween(1, 3);
    const selectedProducts = [];

    for (let i = 0; i < numProductsToAdd; i++) {
        const productId = productIds[randomIntBetween(0, productIds.length - 1)];
        selectedProducts.push(productId);
    }

    console.log(`[VU ${__VU}] Selected ${selectedProducts.length} products: ${selectedProducts.join(', ')}`);
    sleep(1);

    // 3️⃣ 장바구니에 추가
    for (const productId of selectedProducts) {
        const quantity = randomIntBetween(1, 2);
        const success = addToCart(tokens, productId, quantity, jar);

        // 실패 시 (재고 부족 등) 다른 상품으로 재시도
        if (!success && productIds.length > 1) {
            const retryProductId = productIds[randomIntBetween(0, productIds.length - 1)];
            if (retryProductId !== productId) {
                addToCart(tokens, retryProductId, quantity, jar);
            }
        }
        sleep(0.5);
    }

    // 4️⃣ 장바구니 확인
    const cartData = viewCart(tokens, jar);
    sleep(1);

    // 5️⃣ 주문하기 (장바구니에 상품이 있을 때만)
    if (cartData && cartData.items && cartData.items.length > 0) {
        checkout(tokens, cartData.items, jar);
    } else {
        console.log(`[VU ${__VU}] Cart is empty, skipping checkout`);
    }

    sleep(1);
}

//----------------------------------------------------------
// 1. 로그인 (JWT + HttpOnly Cookie)
//----------------------------------------------------------
function login(email, password, jar) {
    const payload = JSON.stringify({ email, password });

    const res = http.post(`${API_SHOP}/login/`, payload, {
        headers: { 'Content-Type': 'application/json' },
        jar: jar,
        tags: { name: 'login' },
    });

    const success = check(res, {
        'login OK': (r) => r.status === 200,
        'has access_token': (r) => r.json('access_token') !== undefined,
    });

    if (success) {
        const data = res.json();

        if (Math.random() < 0.1) {
            console.log(`[VU ${__VU}] Login Success - Cookies: ${JSON.stringify(Object.keys(jar.cookiesForURL(BASE_URL)))}`);
        }

        return {
            accessToken: data.access_token,
            csrfToken: data.csrf_token,
        };
    } else {
        console.error(`[Login Failed] ${email} - Status: ${res.status}, Body: ${res.body}`);
        return null;
    }
}

//----------------------------------------------------------
// 2. 장바구니에 추가
//----------------------------------------------------------
function addToCart(tokens, productId, quantity, jar) {
    const payload = JSON.stringify({
        product_id: productId,
        quantity: quantity,
    });

    const res = http.post(`${API_CARTS}/`, payload, {
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${tokens.accessToken}`,
        },
        jar: jar,
        tags: { name: 'add_to_cart' },
    });

    const success = check(res, {
        'add to cart OK': (r) => r.status === 200,
    });

    if (!success) {
        // 재고 부족이나 상품 없음은 정상 시나리오로 간주 (부하 테스트에서)
        if (res.status === 400 || res.status === 404 || res.status === 500) {
            // 에러 로그는 최소화 (10%만 출력)
            if (Math.random() < 0.1) {
                console.error(`[AddToCart Failed] Product: ${productId}, Status: ${res.status}, Body: ${res.body}`);
            }
        } else {
            console.error(`[AddToCart Failed] Product: ${productId}, Status: ${res.status}, Body: ${res.body}`);
        }
    }

    return success;
}

//----------------------------------------------------------
// 3. 장바구니 확인
//----------------------------------------------------------
function viewCart(tokens, jar) {
    const res = http.get(`${API_CARTS}/`, {
        headers: {
            'Authorization': `Bearer ${tokens.accessToken}`,
        },
        jar: jar,
        tags: { name: 'view_cart' },
    });

    const success = check(res, {
        'view cart OK': (r) => r.status === 200,
    });

    if (success) {
        return res.json();
    } else {
        console.error(`[ViewCart Failed] Status: ${res.status}, Body: ${res.body}`);
        return null;
    }
}

//----------------------------------------------------------
// 4. 주문하기 (장바구니 기반)
//----------------------------------------------------------
function checkout(tokens, cartItems, jar) {
    // 장바구니 아이템을 주문 아이템으로 변환
    const orderItems = cartItems.map(item => ({
        product_id: item.product_id,
        quantity: item.quantity,
    }));

    const payload = JSON.stringify({
        items: orderItems,
    });

    const res = http.post(`${API_ORDERS}/`, payload, {
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${tokens.accessToken}`,
        },
        jar: jar,
        tags: { name: 'checkout' },
    });

    const success = check(res, {
        'checkout OK': (r) => r.status === 200 || r.status === 201,
    });

    if (success) {
        const orderData = res.json();
        console.log(`[VU ${__VU}] Order placed successfully! Order ID: ${orderData.id}`);
    } else {
        console.error(`[Checkout Failed] Status: ${res.status}, Body: ${res.body}`);
    }
}

//----------------------------------------------------------
// Helper: 랜덤 정수 생성
//----------------------------------------------------------
function randomIntBetween(min, max) {
    return Math.floor(Math.random() * (max - min + 1) + min);
}
