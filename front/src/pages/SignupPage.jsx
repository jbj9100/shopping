import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import authService from '../services/authService';
import { Button } from '../components/common/Button';
import { Card } from '../components/common/Card';
import './SignupPage.css';

export const SignupPage = () => {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
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

        // 비밀번호 확인
        if (formData.password !== formData.confirmPassword) {
            setError('비밀번호가 일치하지 않습니다.');
            return;
        }

        setIsLoading(true);

        try {
            await authService.signup(
                formData.username,
                formData.email,
                formData.password
            );
            // 회원가입 성공 - 로그인 페이지로 이동
            alert('회원가입이 완료되었습니다. 로그인해주세요.');
            navigate('/login');
        } catch (err) {
            const detail = err.response?.data?.detail;
            if (detail?.includes('username')) {
                setError('이미 사용 중인 사용자명입니다.');
            } else if (detail?.includes('email')) {
                setError('이미 사용 중인 이메일입니다.');
            } else {
                setError(detail || '회원가입에 실패했습니다.');
            }
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="signup-page">
            <div className="signup-container">
                <Card className="signup-card">
                    <div className="signup-header">
                        <h1 className="signup-title">회원가입</h1>
                        <p className="signup-subtitle">새 계정을 만들어보세요</p>
                    </div>

                    {error && (
                        <div className="signup-error">
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="signup-form">
                        <div className="form-group">
                            <label htmlFor="username">사용자명</label>
                            <input
                                type="text"
                                id="username"
                                name="username"
                                value={formData.username}
                                onChange={handleChange}
                                placeholder="영문 소문자만 입력 (예: johndoe)"
                                required
                                pattern="^[a-z]+$"
                                maxLength={30}
                                className="form-input"
                            />
                            <span className="form-help">영문 소문자만 사용 가능</span>
                        </div>

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
                                maxLength={128}
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
                                placeholder="최소 6자 이상"
                                required
                                minLength={6}
                                maxLength={128}
                                className="form-input"
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="confirmPassword">비밀번호 확인</label>
                            <input
                                type="password"
                                id="confirmPassword"
                                name="confirmPassword"
                                value={formData.confirmPassword}
                                onChange={handleChange}
                                placeholder="비밀번호 재입력"
                                required
                                minLength={6}
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
                            {isLoading ? '가입 중...' : '회원가입'}
                        </Button>
                    </form>

                    <div className="signup-footer">
                        <p>
                            이미 계정이 있으신가요?{' '}
                            <Link to="/login" className="login-link">
                                로그인
                            </Link>
                        </p>
                    </div>
                </Card>
            </div>
        </div>
    );
};
