import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import './AdminPage.css';

export const AdminPage = () => {
    const { user, loading } = useAuth();
    const navigate = useNavigate();
    const [users, setUsers] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        // Admin 권한 체크
        if (!loading && (!user || user.role !== 'admin')) {
            navigate('/');
            return;
        }

        if (user) {
            fetchUsers();
        }
    }, [user, loading, navigate]);

    const fetchUsers = async () => {
        try {
            setIsLoading(true);
            const response = await api.get('/api/shop/admin/');
            setUsers(response.data.users || []);
        } catch (err) {
            setError('사용자 목록을 불러오는데 실패했습니다.');
            console.error(err);
        } finally {
            setIsLoading(false);
        }
    };

    const handleRoleToggle = async (userId, currentRole) => {
        try {
            const newRole = currentRole === 'admin' ? 'normal-user' : 'admin';
            await api.put('/api/shop/admin/', { user_id: userId, role: newRole });

            // 목록 새로고침
            fetchUsers();
        } catch (err) {
            alert('권한 변경에 실패했습니다.');
            console.error(err);
        }
    };

    const handleDelete = async (userId) => {
        if (!window.confirm('정말 이 사용자를 삭제하시겠습니까?')) {
            return;
        }

        try {
            await api.delete('/api/shop/admin/', { data: { user_id: userId } });
            fetchUsers();
        } catch (err) {
            alert('사용자 삭제에 실패했습니다.');
            console.error(err);
        }
    };

    if (loading || isLoading) {
        return <div className="admin-page"><div className="loading">로딩 중...</div></div>;
    }

    if (!user || user.role !== 'admin') {
        return null;
    }

    return (
        <div className="admin-page">
            <div className="admin-container">
                <h1 className="admin-title">사용자 관리</h1>

                {error && <div className="error-message">{error}</div>}

                <div className="users-table-wrapper">
                    <table className="users-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>사용자명</th>
                                <th>이메일</th>
                                <th>Admin 권한</th>
                                <th>가입일</th>
                                <th>삭제</th>
                            </tr>
                        </thead>
                        <tbody>
                            {users.map((u) => (
                                <tr key={u.id}>
                                    <td>{u.id}</td>
                                    <td>{u.username}</td>
                                    <td>{u.email}</td>
                                    <td>
                                        <label className="checkbox-wrapper">
                                            <input
                                                type="checkbox"
                                                checked={u.role === 'admin'}
                                                disabled={u.id === user.id}
                                                onChange={() => handleRoleToggle(u.id, u.role)}
                                            />
                                            <span className="checkbox-label">
                                                {u.id === user.id ? '(본인)' : ''}
                                            </span>
                                        </label>
                                    </td>
                                    <td>{new Date(u.created_at).toLocaleDateString()}</td>
                                    <td>
                                        <button
                                            className="delete-btn"
                                            disabled={u.id === user.id}
                                            onClick={() => handleDelete(u.id)}
                                        >
                                            삭제
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default AdminPage;
