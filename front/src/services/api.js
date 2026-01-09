import axios from 'axios';

const api = axios.create({
    baseURL: '',
    headers: {
        'Content-Type': 'application/json'
    },
    withCredentials: true,  // ← 쿠키 자동 전송!
    timeout: 10000
});

// 요청 인터셉터
api.interceptors.request.use(
    (config) => {
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// 응답 인터셉터
api.interceptors.response.use(
    (response) => {
        return response;
    },
    (error) => {
        // 401 에러(Unauthorized)는 조용히 처리 (비로그인 상태는 정상)
        if (error.response?.status !== 401) {
            console.error('API Error:', error);
        }

        // 원래 에러 객체를 그대로 전달 (AuthContext에서 status 확인 가능)
        return Promise.reject(error);
    }
);

export default api;
