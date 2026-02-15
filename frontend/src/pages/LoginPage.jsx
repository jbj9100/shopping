import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/common/Button';
import { Card } from '../components/common/Card';
import './LoginPage.css';

export const LoginPage = () => {
    const navigate = useNavigate();
    const { login } = useAuth();  // ← Context 사용!
    const [formData, setFormData] = useState({
        email: '',
        password: ''
    });
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
        setError('');
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);

        try {
            await login(formData.email, formData.password);  // ← Context의 login 사용
            // 로그인 성공 - 리로드 없이 navigate!
            navigate('/');
        } catch (err) {
            setError(err.response?.data?.detail || '로그인에 실패했습니다.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="login-page">
            <div className="login-container">
                <Card className="login-card">
                    <div className="login-header">
                        <h1 className="login-title">로그인</h1>
                        <p className="login-subtitle">쇼핑몰에 오신 것을 환영합니다</p>
                    </div>

                    {error && (
                        <div className="login-error">
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="login-form">
                        <div className="form-group">
                            <label htmlFor="email">이메일</label>
                            <input
                                type="email"
                                id="email"
                                name="email"
                                value={formData.email}
                                onChange={handleChange}
                                placeholder="example@email.com"
                                required
                                className="form-input"
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="password">비밀번호</label>
                            <input
                                type="password"
                                id="password"
                                name="password"
                                value={formData.password}
                                onChange={handleChange}
                                placeholder="비밀번호 입력"
                                required
                                minLength={5}
                                className="form-input"
                            />
                        </div>

                        <Button
                            type="submit"
                            variant="primary"
                            size="large"
                            fullWidth
                            disabled={isLoading}
                        >
                            {isLoading ? '로그인 중...' : '로그인'}
                        </Button>
                    </form>

                    <div className="login-footer">
                        <p>
                            계정이 없으신가요?{' '}
                            <Link to="/signup" className="signup-link">
                                회원가입
                            </Link>
                        </p>
                    </div>
                </Card>
            </div>
        </div>
    );
};
