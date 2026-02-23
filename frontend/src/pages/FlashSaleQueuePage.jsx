import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { formatDistanceToNow } from 'date-fns';
import { ko } from 'date-fns/locale';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import './FlashSaleQueuePage.css';

export const FlashSaleQueuePage = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [queueData, setQueueData] = useState(null);
    const [isMyTurn, setIsMyTurn] = useState(false);

    useEffect(() => {
        // 목업 데이터
        setQueueData({
            queueId: id,
            position: 245,
            totalWaiting: 500,
            estimatedWaitSeconds: 490,
            productName: '플래시 세일 베이커리 세트'
        });

        // WebSocket으로 실시간 업데이트 받아야 함
    }, [id]);

    if (!queueData) {
        return <div className="queue-loading">대기열에 진입 중...</div>;
    }

    if (isMyTurn) {
        return (
            <div className="queue-page">
                <div className="container">
                    <Card className="queue-card queue-your-turn">
                        <div className="queue-success-icon">🎉</div>
                        <h1 className="queue-title">내 차례입니다!</h1>
                        <p className="queue-subtitle">
                            5분 내에 결제를 완료해주세요
                        </p>

                        <div className="reservation-timer">
                            <div className="timer-label">남은 시간</div>
                            <div className="timer-value">04:59</div>
                        </div>

                        <div className="queue-actions">
                            <Button variant="primary" size="large" fullWidth>
                                결제하기
                            </Button>
                        </div>

                        <p className="queue-warning">
                            ⚠️ 시간 내 결제하지 않으면 재고가 반환됩니다
                        </p>
                    </Card>
                </div>
            </div>
        );
    }

    const progressPercent = ((queueData.totalWaiting - queueData.position) / queueData.totalWaiting) * 100;

    return (
        <div className="queue-page">
            <div className="container">
                <Card className="queue-card">
                    <h1 className="queue-title">대기열</h1>
                    <p className="queue-subtitle">{queueData.productName}</p>

                    <div className="queue-position-box">
                        <div className="queue-position-label">현재 대기 순번</div>
                        <div className="queue-position-value">{queueData.position}번</div>
                    </div>

                    <div className="queue-progress">
                        <div
                            className="queue-progress-bar"
                            style={{ width: `${progressPercent}%` }}
                        />
                    </div>

                    <div className="queue-info">
                        <div className="queue-info-item">
                            <span className="queue-info-label">대기 인원</span>
                            <span className="queue-info-value">{queueData.totalWaiting}명</span>
                        </div>
                        <div className="queue-info-item">
                            <span className="queue-info-label">예상 대기 시간</span>
                            <span className="queue-info-value">
                                약 {Math.ceil(queueData.estimatedWaitSeconds / 60)}분
                            </span>
                        </div>
                    </div>

                    <div className="queue-tips">
                        <h3>💡 대기 중 안내</h3>
                        <ul>
                            <li>이 페이지를 닫지 마세요</li>
                            <li>자동으로 순번이 업데이트됩니다</li>
                            <li>내 차례가 되면 알림이 표시됩니다</li>
                        </ul>
                    </div>
                </Card>
            </div>
        </div>
    );
};
