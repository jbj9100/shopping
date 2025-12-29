import axios from 'axios';

const api = axios.create({
    baseURL: '',
    headers: {
        'Content-Type': 'application/json'
    },
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
        console.error('API Error:', error);

        if (error.response) {
            // 서버 응답이 있는 경우
            const message = error.response.data?.message || '요청 처리 중 오류가 발생했습니다.';
            return Promise.reject(new Error(message));
        } else if (error.request) {
            // 요청은 보냈지만 응답이 없는 경우
            return Promise.reject(new Error('서버에 연결할 수 없습니다.'));
        } else {
            // 요청 설정 중 오류가 발생한 경우
            return Promise.reject(error);
        }
    }
);

export default api;
