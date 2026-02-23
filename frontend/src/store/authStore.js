// Access Token 메모리 저장 (XSS 방어)
let accessToken = null;
// CSRF Token은 Refresh 시 필요하므로 LocalStorage에 저장 (새로고침 대응)
let csrfToken = localStorage.getItem('csrf_token') || null;

export const setAccessToken = (token) => {
    accessToken = token;
};

export const getAccessToken = () => {
    return accessToken;
};

export const clearAccessToken = () => {
    accessToken = null;
};

export const setCSRFToken = (token) => {
    csrfToken = token;
    if (token) {
        localStorage.setItem('csrf_token', token);
    }
};

export const getCSRFToken = () => {
    return csrfToken;
};

export const clearCSRFToken = () => {
    csrfToken = null;
    localStorage.removeItem('csrf_token');
};
