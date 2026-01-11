import api from './api';

export const orderService = {
    // 주문 생성 (장바구니 기반)
    createOrder: async (orderData) => {
        const response = await api.post('/api/shop/orders', orderData);
        return response.data;
    },

    // 모든 주문 조회
    getAllOrders: async () => {
        const response = await api.get('/api/shop/orders');
        return response.data;
    },

    // 특정 주문 상세 조회
    getOrderById: async (orderId) => {
        const response = await api.get(`/api/shop/orders/${orderId}`);
        return response.data;
    }
};
