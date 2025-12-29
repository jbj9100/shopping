import api from './api';

export const orderService = {
    // 주문 생성
    createOrder: async (orderData) => {
        return await api.post('/orders', orderData);
    },

    // 주문 목록 조회
    getOrders: async () => {
        return await api.get('/orders');
    },

    // 주문 상세 조회
    getOrderById: async (id) => {
        return await api.get(`/orders/${id}`);
    }
};
