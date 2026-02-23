import api from './api';
import { setAccessToken, clearAccessToken, setCSRFToken, clearCSRFToken } from '../store/authStore';

// 로그인 (JWT + CSRF)
export const login = async (email, password) => {
    const response = await api.post('/api/shop/login/', {
        email,
        password
    });

    // Access Token, CSRF Token을 메모리에 저장 (XSS 방어)
    const { access_token, csrf_token } = response.data;
    if (access_token) {
        setAccessToken(access_token);
    }
    if (csrf_token) {
        setCSRFToken(csrf_token);
    }

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

// 로그아웃 (JWT 삭제)
export const logout = async () => {
    // 메모리에서 토큰 제거
    clearAccessToken();
    clearCSRFToken();

    // Backend 로그아웃 API 호출 (jti 블랙리스트 + Refresh 삭제)
    try {
        await api.post('/api/shop/logout/');
    } catch (error) {
        console.error('Logout API error:', error);
    }
};

// 현재 로그인 사용자 정보
export const getMe = async () => {
    const response = await api.get('/api/shop/my_page/');
    return response.data;
};

export default {
    login,
    signup,
    logout,
    getMe
};
