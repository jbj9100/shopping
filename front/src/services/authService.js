import api from './api';

// 로그인
export const login = async (email, password) => {
    const response = await api.post('/api/shop/login/', {
        email,
        password
    });
    return response.data;
};

// 회원가입
export const signup = async (username, email, password) => {
    const response = await api.post('/api/shop/signup/', {
        username,
        email,
        password
    });
    return response.data;
};

// 로그아웃
export const logout = async () => {
    const response = await api.post('/api/shop/logout/');
    return response.data;
};

// 현재 로그인 사용자 정보
export const getMe = async () => {
    const response = await api.get('/api/shop/login/me');
    return response.data;
};

export default {
    login,
    signup,
    logout,
    getMe
};
