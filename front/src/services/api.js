import axios from 'axios';
import { getAccessToken, setAccessToken, getCSRFToken, setCSRFToken } from '../store/authStore';

const api = axios.create({
    baseURL: '',
    headers: {
        'Content-Type': 'application/json'
    },
    withCredentials: true,  // Refresh Token Cookie 자동 전송
    timeout: 10000
});

// 요청 인터셉터 (JWT 자동 추가)
api.interceptors.request.use(
    (config) => {
        // 메모리에서 JWT 토큰 가져오기
        const token = getAccessToken();

        if (token) {
            // Authorization 헤더에 Bearer 토큰 추가
            config.headers.Authorization = `Bearer ${token}`;
        }

        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// 응답 인터셉터 (401 시 자동 Refresh)
api.interceptors.response.use(
    (response) => {
        return response;
    },
    async (error) => {
        const originalRequest = error.config;

        // 401/403 에러 && 재시도 아님 (HTTPBearer는 토큰 없을 때 403 반환)
        if ((error.response?.status === 401 || error.response?.status === 403) && !originalRequest._retry) {
            originalRequest._retry = true;

            try {
                // Refresh Token으로 새 Access Token 발급
                // CSRF 검증 제거됨 - HttpOnly Cookie만으로 안전
                const refreshResponse = await axios.post(
                    '/api/shop/refresh/',
                    {},
                    {
                        withCredentials: true  // Refresh Cookie 전송
                    }
                );

                const { access_token, csrf_token } = refreshResponse.data;

                // 새 토큰 저장
                setAccessToken(access_token);
                if (csrf_token) {
                    setCSRFToken(csrf_token);
                }

                // 원래 요청 재시도
                originalRequest.headers.Authorization = `Bearer ${access_token}`;
                return api(originalRequest);

            } catch (refreshError) {
                // Refresh 실패 → 로그아웃 처리
                console.error('Refresh token expired. Please login again.');
                // 로그인 페이지로 리다이렉트 등 처리
                return Promise.reject(refreshError);
            }
        }

        // 401/403 외 에러는 조용히 처리
        if (error.response?.status !== 401 && error.response?.status !== 403) {
            console.error('API Error:', error);
        }

        return Promise.reject(error);
    }
);

export default api;
