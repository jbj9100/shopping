import api from './api';

export const cartService = {
    // 장바구니 조회
    // 백엔드 응답: { items: CartItemOut[], total_price: number, total_items: number }
    getCart: async () => {
        return await api.get('/cart');
    },

    // 장바구니에 상품 추가
    // 백엔드 요청: { product_id: number, quantity: number }
    addToCart: async (product_id, quantity) => {
        return await api.post('/cart', { product_id, quantity });
    },

    // 장바구니 아이템 수량 변경
    updateCartItem: async (id, quantity) => {
        return await api.put(`/cart/${id}`, { quantity });
    },

    // 장바구니 아이템 삭제
    removeCartItem: async (id) => {
        return await api.delete(`/cart/${id}`);
    },

    // 장바구니 전체 삭제
    clearCart: async () => {
        return await api.delete('/cart');
    }
};
