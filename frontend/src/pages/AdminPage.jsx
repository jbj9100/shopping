import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import './AdminPage.css';

export const AdminPage = () => {
    const { user, loading } = useAuth();
    const navigate = useNavigate();
    const [users, setUsers] = useState([]);
    const [categories, setCategories] = useState([]);
    const [products, setProducts] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');

    // 테스트 계정 일괄 생성
    const [bulkAccountCount, setBulkAccountCount] = useState(10);
    const [bulkCreationProgress, setBulkCreationProgress] = useState(null);
    const [bulkCreationResults, setBulkCreationResults] = useState(null);

    // 사용자 일괄 삭제
    const [selectedUserIds, setSelectedUserIds] = useState([]);

    // 카테고리 폼
    const [newCategory, setNewCategory] = useState({ name: '', display_name: '', description: '', icon: '' });
    const [newCategoryImageFile, setNewCategoryImageFile] = useState(null);
    const [editingCategory, setEditingCategory] = useState(null);
    const [editingCategoryImageFile, setEditingCategoryImageFile] = useState(null);

    // 제품 폼
    const [newProduct, setNewProduct] = useState({
        name: '', price: 0, original_price: 0, brand: '',
        category_id: '', image: '', free_shipping: false, stock: 0, description: ''
    });
    const [newProductImageFile, setNewProductImageFile] = useState(null);
    const [editingProduct, setEditingProduct] = useState(null);
    const [editingProductImageFile, setEditingProductImageFile] = useState(null);
    const [showCategoryForm, setShowCategoryForm] = useState(false);
    const [showProductForm, setShowProductForm] = useState(false);

    useEffect(() => {
        if (!loading && (!user || user.role !== 'admin')) {
            navigate('/');
            return;
        }
        if (user) {
            fetchUsers();
            fetchCategories();
            fetchProducts();
        }
    }, [user, loading, navigate]);

    // API 함수들
    const fetchUsers = async () => {
        try {
            setIsLoading(true);
            const response = await api.get('/api/shop/admin/');
            setUsers(response.data.users || []);
        } catch (err) {
            setError('사용자 목록을 불러오는데 실패했습니다.');
        } finally {
            setIsLoading(false);
        }
    };

    const handleRoleToggle = async (userId, currentRole) => {
        try {
            const newRole = currentRole === 'admin' ? 'normal-user' : 'admin';
            await api.put('/api/shop/admin/', { user_id: userId, role: newRole });
            fetchUsers();
        } catch (err) {
            alert('권한 변경에 실패했습니다.');
        }
    };

    // 이미지 업로드 함수 (기존 이미지 자동 삭제)
    const handleImageUpload = async (file, bucket, oldUrl = null) => {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await api.post(`/api/shop/images/upload?bucket=${bucket}`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });

            // 기존 이미지가 있으면 삭제
            if (oldUrl && !oldUrl.startsWith('blob:')) {
                try {
                    const filename = oldUrl.split('/').pop();
                    await api.delete(`/api/shop/images/${filename}?bucket=${bucket}`);
                } catch (err) {
                    console.error('기존 이미지 삭제 실패:', err);
                }
            }

            return response.data.url;
        } catch (err) {
            setError('이미지 업로드 실패: ' + (err.response?.data?.detail || err.message));
            return null;
        }
    };

    const handleDeleteUser = async (userId) => {
        if (!window.confirm('정말 이 사용자를 삭제하시겠습니까?')) return;
        try {
            await api.delete('/api/shop/admin/', { data: { user_id: userId } });
            fetchUsers();
        } catch (err) {
            alert('사용자 삭제에 실패했습니다.');
        }
    };

    // 사용자 일괄 삭제
    const handleBulkDeleteUsers = async () => {
        if (selectedUserIds.length === 0) {
            alert('삭제할 사용자를 선택하세요.');
            return;
        }

        if (!window.confirm(`선택한 ${selectedUserIds.length}명의 사용자를 삭제하시겠습니까?`)) {
            return;
        }

        try {
            const response = await api.post('/api/shop/admin/bulk-delete', {
                user_ids: selectedUserIds
            });

            alert(`${response.data.deleted_count}명이 삭제되었습니다.`);
            setSelectedUserIds([]);
            await fetchUsers();
        } catch (err) {
            alert('일괄 삭제 실패: ' + (err.response?.data?.detail || err.message));
        }
    };

    // 전체 선택/해제
    const handleSelectAll = (checked) => {
        if (checked) {
            // 현재 사용자 제외한 모든 사용자 선택
            const allIds = users.filter(u => u.id !== user.id).map(u => u.id);
            setSelectedUserIds(allIds);
        } else {
            setSelectedUserIds([]);
        }
    };

    // 개별 선택/해제
    const handleSelectUser = (userId, checked) => {
        if (checked) {
            setSelectedUserIds([...selectedUserIds, userId]);
        } else {
            setSelectedUserIds(selectedUserIds.filter(id => id !== userId));
        }
    };

    // 테스트 계정 일괄 생성
    const handleBulkCreateAccounts = async () => {
        if (!bulkAccountCount || bulkAccountCount < 1 || bulkAccountCount > 1000) {
            alert('계정 개수는 1~1000 사이로 입력하세요.');
            return;
        }

        if (!window.confirm(`테스트 계정 ${bulkAccountCount}개를 생성하시겠습니까?`)) {
            return;
        }

        setBulkCreationProgress({ current: 0, total: bulkAccountCount });
        setBulkCreationResults({ success: 0, skipped: 0, failed: 0 });

        let successCount = 0;
        let skipCount = 0;
        let failCount = 0;

        for (let i = 1; i <= bulkAccountCount; i++) {
            const email = `loadtest${i}@test.com`;
            const username = `loadtest${i}`;
            const password = 'test1234';

            try {
                await api.post('/api/shop/signup/', {
                    email,
                    username,
                    password
                });
                successCount++;
            } catch (err) {
                // 이미 존재하는 계정인 경우
                if (err.response?.data?.detail?.toLowerCase().includes('already')) {
                    skipCount++;
                } else {
                    failCount++;
                    console.error(`계정 생성 실패 (${email}):`, err.response?.data?.detail || err.message);
                }
            }

            // 진행 상황 업데이트
            setBulkCreationProgress({ current: i, total: bulkAccountCount });
            setBulkCreationResults({ success: successCount, skipped: skipCount, failed: failCount });

            // Rate limiting 방지 (0.2초 대기)
            if (i < bulkAccountCount) {
                await new Promise(resolve => setTimeout(resolve, 200));
            }
        }

        // 완료 후 사용자 목록 새로고침
        await fetchUsers();

        // 진행 상태 초기화 (3초 후)
        setTimeout(() => {
            setBulkCreationProgress(null);
            setBulkCreationResults(null);
        }, 3000);
    };

    // 카테고리 관리
    const fetchCategories = async () => {
        try {
            const { data } = await api.get('/api/shop/categories/all');
            setCategories(data);
        } catch (err) {
            console.error('카테고리 로딩 실패:', err);
        }
    };

    const handleCreateCategory = async (e) => {
        e.preventDefault();
        if (!newCategory.name || !newCategory.display_name) {
            alert('카테고리 이름과 표시명을 입력하세요.');
            return;
        }
        try {
            let iconUrl = newCategory.icon;

            // 새 이미지 파일이 선택된 경우에만 업로드
            if (newCategoryImageFile) {
                iconUrl = await handleImageUpload(newCategoryImageFile, 'category');
                if (!iconUrl) {
                    alert('이미지 업로드에 실패했습니다.');
                    return;
                }
            }

            await api.post('/api/shop/categories', { ...newCategory, icon: iconUrl });
            setNewCategory({ name: '', display_name: '', description: '', icon: '' });
            setNewCategoryImageFile(null);
            setShowCategoryForm(false);
            fetchCategories();
            alert('카테고리가 생성되었습니다.');
        } catch (err) {
            alert('카테고리 생성 실패: ' + (err.response?.data?.detail || err.message));
        }
    };

    const handleUpdateCategory = async (categoryId) => {
        try {
            let iconUrl = editingCategory.icon;

            // 새 이미지 파일이 선택된 경우에만 업로드 (기존 이미지 자동 삭제)
            if (editingCategoryImageFile) {
                iconUrl = await handleImageUpload(editingCategoryImageFile, 'category', editingCategory.icon);
                if (!iconUrl) {
                    alert('이미지 업로드에 실패했습니다.');
                    return;
                }
            }

            await api.patch(`/api/shop/categories/${categoryId}`, { ...editingCategory, icon: iconUrl });
            setEditingCategory(null);
            setEditingCategoryImageFile(null);
            fetchCategories();
        } catch (err) {
            alert('카테고리 수정 실패');
        }
    };

    const handleDeleteCategory = async (categoryId) => {
        if (!window.confirm('정말 이 카테고리를 삭제하시겠습니까?')) return;
        try {
            await api.delete(`/api/shop/categories/${categoryId}`);
            fetchCategories();
        } catch (err) {
            alert('카테고리 삭제 실패');
        }
    };

    // 제품 관리
    const fetchProducts = async () => {
        try {
            const { data } = await api.get('/api/shop/products');
            setProducts(data);
        } catch (err) {
            console.error('제품 로딩 실패:', err);
        }
    };

    const handleCreateProduct = async (e) => {
        e.preventDefault();
        if (!newProduct.name || !newProduct.category_id) {
            alert('제품 이름과 카테고리를 입력하세요.');
            return;
        }
        try {
            let imageUrl = newProduct.image;

            // 새 이미지 파일이 선택된 경우에만 업로드
            if (newProductImageFile) {
                imageUrl = await handleImageUpload(newProductImageFile, 'product');
                if (!imageUrl) {
                    alert('이미지 업로드에 실패했습니다.');
                    return;
                }
            }

            await api.post('/api/shop/products', {
                ...newProduct,
                image: imageUrl,
                price: parseInt(newProduct.price),
                original_price: parseInt(newProduct.original_price),
                category_id: parseInt(newProduct.category_id),
                stock: parseInt(newProduct.stock)
            });
            setNewProduct({
                name: '', price: 0, original_price: 0, brand: '',
                category_id: '', image: '', free_shipping: false, stock: 0, description: ''
            });
            setNewProductImageFile(null);
            setShowProductForm(false);
            fetchProducts();
            alert('제품이 생성되었습니다.');
        } catch (err) {
            alert('제품 생성 실패');
        }
    };

    const handleUpdateProduct = async (productId) => {
        try {
            let imageUrl = editingProduct.image;

            // 새 이미지 파일이 선택된 경우에만 업로드 (기존 이미지 자동 삭제)
            if (editingProductImageFile) {
                imageUrl = await handleImageUpload(editingProductImageFile, 'product', editingProduct.image);
                if (!imageUrl) {
                    alert('이미지 업로드에 실패했습니다.');
                    return;
                }
            }

            await api.patch(`/api/shop/products/${productId}`, {
                ...editingProduct,
                image: imageUrl,
                price: parseInt(editingProduct.price),
                original_price: parseInt(editingProduct.original_price),
                category_id: parseInt(editingProduct.category_id),
                stock: parseInt(editingProduct.stock)
            });
            setEditingProduct(null);
            setEditingProductImageFile(null);
            fetchProducts();
        } catch (err) {
            alert('제품 수정 실패');
        }
    };

    const handleDeleteProduct = async (productId) => {
        if (!window.confirm('정말 이 제품을 삭제하시겠습니까?')) return;
        try {
            await api.delete(`/api/shop/products/${productId}`);
            fetchProducts();
        } catch (err) {
            alert('제품 삭제 실패');
        }
    };

    if (loading || isLoading) {
        return <div className="admin-page"><div className="loading">로딩 중...</div></div>;
    }

    if (!user || user.role !== 'admin') return null;

    return (
        <div className="admin-page">
            <div className="admin-container">
                {error && <div className="error-message">{error}</div>}

                {/* ===== 사용자 관리 ===== */}
                <div className="page-header">
                    <h1 className="page-title">사용자 관리</h1>
                    <button
                        className="btn-bulk-delete"
                        onClick={handleBulkDeleteUsers}
                        disabled={selectedUserIds.length === 0}
                    >
                        선택 삭제 ({selectedUserIds.length})
                    </button>
                </div>

                <div className="data-table-container">
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>
                                    <input
                                        type="checkbox"
                                        className="table-checkbox"
                                        checked={selectedUserIds.length > 0 && selectedUserIds.length === users.filter(u => u.id !== user.id).length}
                                        onChange={(e) => handleSelectAll(e.target.checked)}
                                    />
                                </th>
                                <th>번호</th>
                                <th>사용자명</th>
                                <th>이메일</th>
                                <th>Admin</th>
                                <th>가입일</th>
                                <th>관리</th>
                            </tr>
                        </thead>
                        <tbody>
                            {users.map((u, idx) => (
                                <tr key={u.id}>
                                    <td>
                                        <input
                                            type="checkbox"
                                            className="table-checkbox"
                                            checked={selectedUserIds.includes(u.id)}
                                            disabled={u.id === user.id}
                                            onChange={(e) => handleSelectUser(u.id, e.target.checked)}
                                        />
                                    </td>
                                    <td>{idx + 1}</td>
                                    <td>{u.username}</td>
                                    <td>{u.email}</td>
                                    <td>
                                        <input
                                            type="checkbox"
                                            className="table-checkbox"
                                            checked={u.role === 'admin'}
                                            disabled={u.id === user.id}
                                            onChange={() => handleRoleToggle(u.id, u.role)}
                                        />
                                    </td>
                                    <td>{new Date(u.created_at).toLocaleDateString()}</td>
                                    <td>
                                        <button
                                            className="btn-delete"
                                            disabled={u.id === user.id}
                                            onClick={() => handleDeleteUser(u.id)}
                                        >
                                            삭제
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                {/* ===== 테스트 계정 일괄 생성 ===== */}
                <div className="page-header">
                    <h1 className="page-title">🔧 테스트 계정 일괄 생성</h1>
                </div>

                <div className="create-form-section" style={{ marginBottom: '30px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '15px', marginBottom: '20px' }}>
                        <label style={{ fontWeight: 'bold', minWidth: '100px' }}>생성 개수:</label>
                        <input
                            type="number"
                            min="1"
                            max="1000"
                            value={bulkAccountCount}
                            onChange={(e) => setBulkAccountCount(parseInt(e.target.value) || 0)}
                            style={{ width: '100px', padding: '8px' }}
                        />
                        <span style={{ color: '#666', fontSize: '14px' }}>
                            loadtest1@test.com ~ loadtest{bulkAccountCount}@test.com
                        </span>
                    </div>

                    <button
                        className="btn-create"
                        onClick={handleBulkCreateAccounts}
                        disabled={bulkCreationProgress !== null}
                        style={{ opacity: bulkCreationProgress !== null ? 0.6 : 1 }}
                    >
                        {bulkCreationProgress ? '생성 중...' : '일괄 생성 시작'}
                    </button>

                    {/* 진행 상황 표시 */}
                    {bulkCreationProgress && (
                        <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#f5f5f5', borderRadius: '8px' }}>
                            <div style={{ marginBottom: '10px', fontWeight: 'bold' }}>
                                진행 상황: {bulkCreationProgress.current} / {bulkCreationProgress.total}
                            </div>
                            <div style={{ width: '100%', height: '20px', backgroundColor: '#ddd', borderRadius: '10px', overflow: 'hidden' }}>
                                <div
                                    style={{
                                        width: `${(bulkCreationProgress.current / bulkCreationProgress.total) * 100}%`,
                                        height: '100%',
                                        backgroundColor: '#4CAF50',
                                        transition: 'width 0.3s'
                                    }}
                                />
                            </div>
                            {bulkCreationResults && (
                                <div style={{ marginTop: '10px', fontSize: '14px', color: '#333' }}>
                                    ✓ 생성: {bulkCreationResults.success} |
                                    ○ 중복: {bulkCreationResults.skipped} |
                                    ✗ 실패: {bulkCreationResults.failed}
                                </div>
                            )}
                        </div>
                    )}
                </div>

                <div className="section-divider" />

                {/* ===== 카테고리 관리 ===== */}
                <div className="page-header">
                    <h1 className="page-title">카테고리 관리</h1>
                    <button className="btn-new" onClick={() => setShowCategoryForm(!showCategoryForm)}>
                        {showCategoryForm ? '✕ 취소' : '+ 신규등록'}
                    </button>
                </div>

                {showCategoryForm && (
                    <div className="create-form-section">
                        <h3>새 카테고리 등록</h3>
                        <form onSubmit={handleCreateCategory}>
                            <div className="form-grid">
                                <div className="form-group">
                                    <label>이름 (영문)</label>
                                    <input
                                        type="text"
                                        placeholder="food, living..."
                                        value={newCategory.name}
                                        onChange={(e) => setNewCategory({ ...newCategory, name: e.target.value })}
                                    />
                                </div>
                                <div className="form-group">
                                    <label>표시명</label>
                                    <input
                                        type="text"
                                        placeholder="식품, 생활용품..."
                                        value={newCategory.display_name}
                                        onChange={(e) => setNewCategory({ ...newCategory, display_name: e.target.value })}
                                    />
                                </div>
                                <div className="form-group">
                                    <label>아이콘 (이미지 파일)</label>
                                    <input
                                        type="file"
                                        accept="image/*"
                                        onChange={(e) => {
                                            const file = e.target.files[0];
                                            if (file) {
                                                setNewCategoryImageFile(file);
                                                // 미리보기용 로컬 URL 생성
                                                const previewUrl = URL.createObjectURL(file);
                                                setNewCategory({ ...newCategory, icon: previewUrl });
                                            }
                                        }}
                                    />
                                    {newCategory.icon && (
                                        <div style={{ marginTop: '8px' }}>
                                            <img src={newCategory.icon} alt="preview" style={{ width: '50px', height: '50px', objectFit: 'cover' }} />
                                        </div>
                                    )}
                                </div>
                                <div className="form-group">
                                    <label>설명</label>
                                    <input
                                        type="text"
                                        placeholder="선택사항"
                                        value={newCategory.description}
                                        onChange={(e) => setNewCategory({ ...newCategory, description: e.target.value })}
                                    />
                                </div>
                            </div>
                            <button type="submit" className="btn-create">등록</button>
                        </form>
                    </div>
                )}

                <div className="data-table-container">
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>번호</th>
                                <th>이름</th>
                                <th>표시명</th>
                                <th>아이콘</th>
                                <th>설명</th>
                                <th>생성일</th>
                                <th>관리</th>
                            </tr>
                        </thead>
                        <tbody>
                            {categories.map((cat, idx) => (
                                <tr key={cat.id}>
                                    <td>{idx + 1}</td>
                                    <td>
                                        {editingCategory?.id === cat.id ? (
                                            <input
                                                value={editingCategory.name}
                                                onChange={(e) => setEditingCategory({ ...editingCategory, name: e.target.value })}
                                            />
                                        ) : cat.name}
                                    </td>
                                    <td>
                                        {editingCategory?.id === cat.id ? (
                                            <input
                                                value={editingCategory.display_name}
                                                onChange={(e) => setEditingCategory({ ...editingCategory, display_name: e.target.value })}
                                            />
                                        ) : cat.display_name}
                                    </td>
                                    <td>
                                        {editingCategory?.id === cat.id ? (
                                            <div>
                                                <input
                                                    type="file"
                                                    accept="image/*"
                                                    onChange={(e) => {
                                                        const file = e.target.files[0];
                                                        if (file) {
                                                            setEditingCategoryImageFile(file);
                                                            // 미리보기용 로컬 URL 생성
                                                            const previewUrl = URL.createObjectURL(file);
                                                            setEditingCategory({ ...editingCategory, icon: previewUrl });
                                                        }
                                                    }}
                                                    style={{ fontSize: '12px' }}
                                                />
                                                {editingCategory.icon && (
                                                    <img src={editingCategory.icon} alt="icon" style={{ width: '30px', height: '30px', marginTop: '4px', display: 'block' }} />
                                                )}
                                            </div>
                                        ) : (
                                            cat.icon ? <img src={cat.icon} alt="icon" style={{ width: '30px', height: '30px' }} /> : '-'
                                        )}
                                    </td>
                                    <td>
                                        {editingCategory?.id === cat.id ? (
                                            <input
                                                value={editingCategory.description || ''}
                                                onChange={(e) => setEditingCategory({ ...editingCategory, description: e.target.value })}
                                            />
                                        ) : (cat.description || '-')}
                                    </td>
                                    <td>{new Date(cat.created_at).toLocaleDateString()}</td>
                                    <td>
                                        <div className="action-btns">
                                            {editingCategory?.id === cat.id ? (
                                                <>
                                                    <button className="btn-save" onClick={() => handleUpdateCategory(cat.id)}>저장</button>
                                                    <button className="btn-cancel" onClick={() => {
                                                        setEditingCategory(null);
                                                        setEditingCategoryImageFile(null);
                                                    }}>취소</button>
                                                </>
                                            ) : (
                                                <>
                                                    <button className="btn-edit" onClick={() => setEditingCategory(cat)}>수정</button>
                                                    <button className="btn-delete" onClick={() => handleDeleteCategory(cat.id)}>삭제</button>
                                                </>
                                            )}
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                <div className="section-divider" />

                {/* ===== 제품 관리 ===== */}
                <div className="page-header">
                    <h1 className="page-title">제품 관리</h1>
                    <button className="btn-new" onClick={() => setShowProductForm(!showProductForm)}>
                        {showProductForm ? '✕ 취소' : '+ 신규등록'}
                    </button>
                </div>

                {showProductForm && (
                    <div className="create-form-section">
                        <h3>새 제품 등록</h3>
                        <form onSubmit={handleCreateProduct}>
                            <div className="form-grid">
                                <div className="form-group">
                                    <label>제품명</label>
                                    <input
                                        type="text"
                                        value={newProduct.name}
                                        onChange={(e) => setNewProduct({ ...newProduct, name: e.target.value })}
                                    />
                                </div>
                                <div className="form-group">
                                    <label>가격</label>
                                    <input
                                        type="number"
                                        value={newProduct.price}
                                        onChange={(e) => setNewProduct({ ...newProduct, price: e.target.value })}
                                    />
                                </div>
                                <div className="form-group">
                                    <label>원가</label>
                                    <input
                                        type="number"
                                        value={newProduct.original_price}
                                        onChange={(e) => setNewProduct({ ...newProduct, original_price: e.target.value })}
                                    />
                                </div>
                                <div className="form-group">
                                    <label>브랜드</label>
                                    <input
                                        type="text"
                                        value={newProduct.brand}
                                        onChange={(e) => setNewProduct({ ...newProduct, brand: e.target.value })}
                                    />
                                </div>
                                <div className="form-group">
                                    <label>카테고리</label>
                                    <select
                                        value={newProduct.category_id}
                                        onChange={(e) => setNewProduct({ ...newProduct, category_id: e.target.value })}
                                    >
                                        <option value="">선택</option>
                                        {categories.map(cat => (
                                            <option key={cat.id} value={cat.id}>{cat.display_name}</option>
                                        ))}
                                    </select>
                                </div>
                                <div className="form-group">
                                    <label>재고</label>
                                    <input
                                        type="number"
                                        value={newProduct.stock}
                                        onChange={(e) => setNewProduct({ ...newProduct, stock: e.target.value })}
                                    />
                                </div>
                                <div className="form-group">
                                    <label>무료배송</label>
                                    <select
                                        value={newProduct.free_shipping ? 'true' : 'false'}
                                        onChange={(e) => setNewProduct({ ...newProduct, free_shipping: e.target.value === 'true' })}
                                    >
                                        <option value="false">아니오</option>
                                        <option value="true">예</option>
                                    </select>
                                </div>
                                <div className="form-group">
                                    <label>이미지 파일</label>
                                    <input
                                        type="file"
                                        accept="image/*"
                                        onChange={(e) => {
                                            const file = e.target.files[0];
                                            if (file) {
                                                setNewProductImageFile(file);
                                                // 미리보기용 로컬 URL 생성
                                                const previewUrl = URL.createObjectURL(file);
                                                setNewProduct({ ...newProduct, image: previewUrl });
                                            }
                                        }}
                                    />
                                    {newProduct.image && (
                                        <div style={{ marginTop: '8px' }}>
                                            <img src={newProduct.image} alt="preview" style={{ width: '80px', height: '80px', objectFit: 'cover' }} />
                                        </div>
                                    )}
                                </div>
                            </div>
                            <button type="submit" className="btn-create">등록</button>
                        </form>
                    </div>
                )}

                <div className="data-table-container">
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>번호</th>
                                <th>제품명</th>
                                <th>이미지</th>
                                <th>가격</th>
                                <th>브랜드</th>
                                <th>카테고리</th>
                                <th>재고</th>
                                <th>무료배송</th>
                                <th>관리</th>
                            </tr>
                        </thead>
                        <tbody>
                            {products.map((prod, idx) => (
                                <tr key={prod.id}>
                                    <td>{idx + 1}</td>
                                    <td>
                                        {editingProduct?.id === prod.id ? (
                                            <input
                                                value={editingProduct.name}
                                                onChange={(e) => setEditingProduct({ ...editingProduct, name: e.target.value })}
                                            />
                                        ) : prod.name}
                                    </td>
                                    <td>
                                        {editingProduct?.id === prod.id ? (
                                            <div>
                                                <input
                                                    type="file"
                                                    accept="image/*"
                                                    onChange={(e) => {
                                                        const file = e.target.files[0];
                                                        if (file) {
                                                            setEditingProductImageFile(file);
                                                            // 미리보기용 로컬 URL 생성
                                                            const previewUrl = URL.createObjectURL(file);
                                                            setEditingProduct({ ...editingProduct, image: previewUrl });
                                                        }
                                                    }}
                                                    style={{ fontSize: '11px' }}
                                                />
                                                {editingProduct.image && (
                                                    <img src={editingProduct.image} alt="product" style={{ width: '50px', height: '50px', marginTop: '4px', objectFit: 'cover', display: 'block' }} />
                                                )}
                                            </div>
                                        ) : (
                                            prod.image ? <img src={prod.image} alt="product" style={{ width: '50px', height: '50px', objectFit: 'cover' }} /> : '-'
                                        )}
                                    </td>
                                    <td>
                                        {editingProduct?.id === prod.id ? (
                                            <input
                                                type="number"
                                                value={editingProduct.price}
                                                onChange={(e) => setEditingProduct({ ...editingProduct, price: e.target.value })}
                                                style={{ width: '80px' }}
                                            />
                                        ) : prod.price?.toLocaleString()}
                                    </td>
                                    <td>{prod.brand}</td>
                                    <td>
                                        {editingProduct?.id === prod.id ? (
                                            <select
                                                value={editingProduct.category_id}
                                                onChange={(e) => setEditingProduct({ ...editingProduct, category_id: e.target.value })}
                                            >
                                                {categories.map(cat => (
                                                    <option key={cat.id} value={cat.id}>{cat.display_name}</option>
                                                ))}
                                            </select>
                                        ) : (categories.find(c => c.id === prod.category_id)?.display_name || '-')}
                                    </td>
                                    <td>
                                        {editingProduct?.id === prod.id ? (
                                            <input
                                                type="number"
                                                value={editingProduct.stock}
                                                onChange={(e) => setEditingProduct({ ...editingProduct, stock: e.target.value })}
                                                style={{ width: '60px' }}
                                            />
                                        ) : prod.stock}
                                    </td>
                                    <td>{prod.free_shipping ? '✓' : '-'}</td>
                                    <td>
                                        <div className="action-btns">
                                            {editingProduct?.id === prod.id ? (
                                                <>
                                                    <button className="btn-save" onClick={() => handleUpdateProduct(prod.id)}>저장</button>
                                                    <button className="btn-cancel" onClick={() => {
                                                        setEditingProduct(null);
                                                        setEditingProductImageFile(null);
                                                    }}>취소</button>
                                                </>
                                            ) : (
                                                <>
                                                    <button className="btn-edit" onClick={() => setEditingProduct(prod)}>수정</button>
                                                    <button className="btn-delete" onClick={() => handleDeleteProduct(prod.id)}>삭제</button>
                                                </>
                                            )}
                                        </div>
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
