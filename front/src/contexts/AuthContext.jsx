import { createContext, useContext, useState, useEffect } from 'react';
import authService from '../services/authService';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    // 초기 로드 시 사용자 정보 확인
    useEffect(() => {
        checkAuth();
    }, []);

    const checkAuth = async () => {
        try {
            const data = await authService.getMe();
            if (data.username) {
                setUser(data);
            }
        } catch (err) {
            // 401 에러는 정상 동작 (비로그인 상태)
            if (err.response?.status !== 401) {
                console.error('인증 확인 실패:', err);
            }
            setUser(null);
        } finally {
            setLoading(false);
        }
    };

    // 로그인
    const login = async (email, password) => {
        await authService.login(email, password);
        await checkAuth(); // 로그인 후 사용자 정보 갱신
    };

    // 로그아웃
    const logout = async () => {
        await authService.logout();
        setUser(null);
    };

    const value = {
        user,
        loading,
        login,
        logout,
        refreshUser: checkAuth
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};

// Hook
export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within AuthProvider');
    }
    return context;
};
