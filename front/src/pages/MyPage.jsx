import { useState, useEffect } from 'react';
import axios from 'axios';
import './MyPage.css';

const MyPage = () => {
    const [userInfo, setUserInfo] = useState({ email: '', username: '' });
    const [isEditing, setIsEditing] = useState(false);
    const [formData, setFormData] = useState({ username: '', password: '' });
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');

    // 내 정보 조회
    useEffect(() => {
        fetchUserInfo();
    }, []);

    const fetchUserInfo = async () => {
        try {
            const response = await axios.get('http://localhost:8000/api/shop/my_page', {
                withCredentials: true, // 쿠키 전송
            });
            setUserInfo(response.data);
            setFormData({ username: response.data.username, password: '' });
        } catch (error) {
            console.error('Failed to fetch user info:', error);
            setMessage('사용자 정보를 불러오는데 실패했습니다.');
        }
    };

    // 정보 수정 제출
    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setMessage('');

        try {
            // 변경된 필드만 전송
            const updateData = {};
            if (formData.username !== userInfo.username) {
                updateData.username = formData.username;
            }
            if (formData.password) {
                updateData.password = formData.password;
            }

            const response = await axios.put(
                'http://localhost:8000/api/shop/my_page',
                { ...userInfo, ...updateData }, // email 포함
                { withCredentials: true }
            );

            if (response.data.ok) {
                setMessage('✅ 정보가 성공적으로 수정되었습니다!');
                setIsEditing(false);
                fetchUserInfo(); // 새로고침
                setFormData({ ...formData, password: '' }); // 비밀번호 초기화
            }
        } catch (error) {
            console.error('Update failed:', error);
            setMessage('❌ 정보 수정에 실패했습니다: ' + (error.response?.data?.detail || error.message));
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="mypage-container">
            <div className="mypage-card">
                <h1>마이페이지</h1>

                {message && (
                    <div className={`message ${message.includes('✅') ? 'success' : 'error'}`}>
                        {message}
                    </div>
                )}

                <div className="user-info">
                    <div className="info-row">
                        <label>이메일</label>
                        <div className="value">{userInfo.email}</div>
                    </div>

                    {!isEditing ? (
                        <>
                            <div className="info-row">
                                <label>사용자명</label>
                                <div className="value">{userInfo.username}</div>
                            </div>
                            <button className="btn-edit" onClick={() => setIsEditing(true)}>
                                정보 수정
                            </button>
                        </>
                    ) : (
                        <form onSubmit={handleSubmit}>
                            <div className="form-group">
                                <label htmlFor="username">사용자명</label>
                                <input
                                    type="text"
                                    id="username"
                                    value={formData.username}
                                    onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                                    placeholder="새 사용자명"
                                />
                            </div>

                            <div className="form-group">
                                <label htmlFor="password">새 비밀번호</label>
                                <input
                                    type="password"
                                    id="password"
                                    value={formData.password}
                                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                                    placeholder="비밀번호 변경 시 입력"
                                    minLength={6}
                                />
                                <small>※ 비밀번호를 변경하지 않으려면 비워두세요</small>
                            </div>

                            <div className="button-group">
                                <button type="submit" className="btn-save" disabled={loading}>
                                    {loading ? '저장 중...' : '저장'}
                                </button>
                                <button
                                    type="button"
                                    className="btn-cancel"
                                    onClick={() => {
                                        setIsEditing(false);
                                        setFormData({ username: userInfo.username, password: '' });
                                        setMessage('');
                                    }}
                                >
                                    취소
                                </button>
                            </div>
                        </form>
                    )}
                </div>
            </div>
        </div>
    );
};

export default MyPage;
