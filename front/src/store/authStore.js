// Access Token 메모리 저장 (XSS 방어)
let accessToken = null;
let csrfToken = null;

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
};

export const getCSRFToken = () => {
    return csrfToken;
};

export const clearCSRFToken = () => {
    csrfToken = null;
};
