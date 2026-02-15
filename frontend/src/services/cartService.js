import api from './api';

// 백엔드 응답을 프론트엔드 형식으로 변환
const transformCartData = (backendData) => ({
    items: backendData.items.map(item => ({
        id: item.id,
        product_id: item.product_id,
        name: item.product_name,       // product_name → name
        price: item.discount_price,    // discount_price → price (백엔드 스키마 변경됨)
        quantity: item.quantity,
        image: item.product_image       // product_image → image
    })),
    total_price: backendData.total_price,
    total_items: backendData.total_items
});

export const cartService = {
    // 장바구니 조회
    getCart: async () => {
        const response = await api.get('/api/carts');
        return transformCartData(response.data);
    },

    // 장바구니에 상품 추가
    addToCart: async (product_id, quantity = 1) => {
        const response = await api.post('/api/carts', {
            product_id,
            quantity
        });
        return transformCartData(response.data);
    },

    // 장바구니 아이템 수량 변경
    updateCartItem: async (item_id, quantity) => {
        const response = await api.patch(`/api/carts/${item_id}`, { quantity });
        return transformCartData(response.data);
    },

    // 장바구니 아이템 삭제
    removeCartItem: async (item_id) => {
        const response = await api.delete(`/api/carts/${item_id}`);
        return transformCartData(response.data);
    },

    // 장바구니 전체 삭제
    clearCart: async () => {
        const response = await api.delete('/api/carts');
        return transformCartData(response.data);
    }
};
