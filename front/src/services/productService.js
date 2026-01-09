import api from './api';

export const productService = {
    // 상품 목록 조회
    getProducts: async (params = {}) => {
        const response = await api.get('/api/shop/products', { params });
        return response.data;
    },

    // 상품 상세 조회
    getProductById: async (id) => {
        const response = await api.get(`/api/shop/products/${id}`);
        return response.data;
    },

    // 상품 검색
    searchProducts: async (query, filters = {}) => {
        const response = await api.get('/api/shop/products/search', {
            params: { q: query, ...filters }
        });
        return response.data;
    },

    // 카테고리별 상품 조회
    getProductsByCategory: async (category, params = {}) => {
        const response = await api.get(`/api/shop/products/category/${category}`, { params });
        return response.data;
    }
};
