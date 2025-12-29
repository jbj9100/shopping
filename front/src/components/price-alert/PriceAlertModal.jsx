import { useState } from 'react';
import { Button } from '../common/Button';
import './PriceAlertModal.css';

export const PriceAlertModal = ({ product, onClose, onSubmit }) => {
    const [targetPrice, setTargetPrice] = useState(product?.price || '');
    const [notificationType, setNotificationType] = useState('browser');

    const handleSubmit = (e) => {
        e.preventDefault();

        if (!targetPrice || targetPrice >= product.price) {
            alert('목표가는 현재 가격보다 낮아야 합니다.');
            return;
        }

        onSubmit?.({
            productId: product.id,
            productName: product.name,
            targetPrice: Number(targetPrice),
            notificationType
        });

        onClose?.();
    };

    if (!product) return null;

    return (
        <div className="price-alert-modal-overlay" onClick={onClose}>
            <div className="price-alert-modal" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h2 className="modal-title">🔔 가격 알림 설정</h2>
                    <button className="modal-close" onClick={onClose}>✕</button>
                </div>

                <div className="modal-body">
                    <div className="product-info">
                        <div className="product-image-small">
                            {product.image ? (
                                <img src={product.image} alt={product.name} />
                            ) : (
                                <div className="product-placeholder-small">🍞</div>
                            )}
                        </div>
                        <div>
                            <h3 className="product-name-modal">{product.name}</h3>
                            <p className="current-price">
                                현재 가격: <strong>{product.price.toLocaleString()}원</strong>
                            </p>
                        </div>
                    </div>

                    <form onSubmit={handleSubmit}>
                        <div className="form-group">
                            <label htmlFor="targetPrice">목표가 (원)</label>
                            <input
                                type="number"
                                id="targetPrice"
                                value={targetPrice}
                                onChange={(e) => setTargetPrice(e.target.value)}
                                placeholder="희망 가격을 입력하세요"
                                className="price-input"
                                required
                            />
                            <p className="help-text">
                                이 가격 이하로 떨어지면 알림을 받습니다
                            </p>
                        </div>

                        <div className="form-group">
                            <label>알림 수단</label>
                            <div className="notification-options">
                                <label className="radio-option">
                                    <input
                                        type="radio"
                                        name="notificationType"
                                        value="browser"
                                        checked={notificationType === 'browser'}
                                        onChange={(e) => setNotificationType(e.target.value)}
                                    />
                                    <span>브라우저 알림</span>
                                </label>
                                <label className="radio-option">
                                    <input
                                        type="radio"
                                        name="notificationType"
                                        value="email"
                                        checked={notificationType === 'email'}
                                        onChange={(e) => setNotificationType(e.target.value)}
                                    />
                                    <span>이메일</span>
                                </label>
                            </div>
                        </div>

                        <div className="modal-footer">
                            <Button type="button" variant="ghost" onClick={onClose}>
                                취소
                            </Button>
                            <Button type="submit" variant="primary">
                                알림 설정
                            </Button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
};
