import { Link, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import './Header.css';

export const Header = () => {
    const [searchQuery, setSearchQuery] = useState('');
    const { user, logout, loading } = useAuth();
    const navigate = useNavigate();

    const handleSearch = (e) => {
        e.preventDefault();
        if (searchQuery.trim()) {
            navigate(`/search?q=${encodeURIComponent(searchQuery)}`);
        }
    };

    const handleLogout = async () => {
        try {
            await logout();
            navigate('/');
        } catch (err) {
            console.error('로그아웃 실패:', err);
        }
    };

    return (
        <header className="header">
            <div className="header-top">
                <div className="container">
                    <div className="header-top-content">
                        <Link to="/" className="header-logo">
                            <span className="header-logo-icon">🛒</span>
                            <span className="header-logo-text">Shopping Mall</span>
                        </Link>

                        <form className="header-search" onSubmit={handleSearch}>
                            <input
                                type="text"
                                className="header-search-input"
                                placeholder="상품을 검색해보세요"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                            />
                            <button type="submit" className="header-search-button">
                                🔍
                            </button>
                        </form>

                        <nav className="header-nav">
                            <Link to="/cart" className="header-nav-item">
                                <span className="header-nav-icon">🛒</span>
                                <span className="header-nav-text">장바구니</span>
                            </Link>
                            <Link to="/orders" className="header-nav-item">
                                <span className="header-nav-icon">📦</span>
                                <span className="header-nav-text">주문내역</span>
                            </Link>

                            {loading ? (
                                // 로딩 중: 공간 유지 (투명)
                                <>
                                    <div className="header-nav-item" style={{ opacity: 0, pointerEvents: 'none' }}>
                                        <span className="header-nav-icon">👤</span>
                                        <span className="header-nav-text">username님</span>
                                    </div>
                                    <div className="header-nav-item" style={{ opacity: 0, pointerEvents: 'none' }}>
                                        <span className="header-nav-icon">🚪</span>
                                        <span className="header-nav-text">로그아웃</span>
                                    </div>
                                </>
                            ) : user ? (
                                <>
                                    {user.role === 'admin' && (
                                        <Link to="/admin" className="header-nav-item">
                                            <span className="header-nav-icon">🛡️</span>
                                            <span className="header-nav-text">관리자</span>
                                        </Link>
                                    )}
                                    <Link to="/my-page" className="header-nav-item">
                                        <span className="header-nav-icon">👤</span>
                                        <span className="header-nav-text">{user.username}님</span>
                                    </Link>
                                    <button onClick={handleLogout} className="header-nav-item header-logout-btn">
                                        <span className="header-nav-icon">🚪</span>
                                        <span className="header-nav-text">로그아웃</span>
                                    </button>
                                </>
                            ) : (
                                <Link to="/login" className="header-nav-item">
                                    <span className="header-nav-icon">👤</span>
                                    <span className="header-nav-text">로그인</span>
                                </Link>
                            )}
                        </nav>
                    </div>
                </div>
            </div>
        </header>
    );
};
