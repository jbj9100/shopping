import { Link, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import authService from '../../services/authService';
import './Header.css';

export const Header = () => {
    const [searchQuery, setSearchQuery] = useState('');
    const [user, setUser] = useState(null);
    const navigate = useNavigate();

    // 로그인 상태 확인
    useEffect(() => {
        checkLoginStatus();
    }, []);

    const checkLoginStatus = async () => {
        try {
            const data = await authService.getMe();
            if (data.username) {
                setUser({ username: data.username });
            }
        } catch (err) {
            // 로그인 안됨
            setUser(null);
        }
    };

    const handleSearch = (e) => {
        e.preventDefault();
        if (searchQuery.trim()) {
            navigate(`/search?q=${encodeURIComponent(searchQuery)}`);
        }
    };

    const handleLogout = async () => {
        try {
            await authService.logout();
            setUser(null);
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

                            {user ? (
                                <>
                                    <span className="header-nav-item header-user-info">
                                        <span className="header-nav-icon">👤</span>
                                        <span className="header-nav-text">{user.username}님</span>
                                    </span>
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

            <div className="header-categories">
                <div className="container">
                    <nav className="categories-nav">
                        <Link to="/category/food" className="category-item">식품</Link>
                        <Link to="/category/living" className="category-item">생활용품</Link>
                        <Link to="/category/beauty" className="category-item">뷰티</Link>
                        <Link to="/category/interior" className="category-item">홈인테리어</Link>
                        <Link to="/category/electronics" className="category-item">가전디지털</Link>
                        <Link to="/category/kitchen" className="category-item">주방용품</Link>
                        <Link to="/category/pet" className="category-item">반려동물</Link>
                        <Link to="/category/sports" className="category-item">스포츠/레저</Link>
                        <Link to="/category/books" className="category-item">도서/음반</Link>
                        <Link to="/category/health" className="category-item">헬스/건강</Link>
                    </nav>
                </div>
            </div>
        </header>
    );
};
