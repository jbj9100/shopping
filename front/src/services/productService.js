import api from './api';

export const productService = {
    // 상품 목록 조회
    getProducts: async (params = {}) => {
        return await api.get('/products', { params });
    },

    // 상품 상세 조회
    getProductById: async (id) => {
        return await api.get(`/products/${id}`);
    },

    // 상품 검색
    searchProducts: async (query, filters = {}) => {
        return await api.get('/products/search', {
            params: { q: query, ...filters }
        });
    },

    // 카테고리별 상품 조회
    getProductsByCategory: async (category, params = {}) => {
        return await api.get(`/products/category/${category}`, { params });
    }
};
