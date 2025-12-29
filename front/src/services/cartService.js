import api from './api';

export const cartService = {
    // 장바구니 조회
    getCart: async () => {
        return await api.get('/cart');
    },

    // 장바구니에 상품 추가
    addToCart: async (item) => {
        return await api.post('/cart', item);
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
