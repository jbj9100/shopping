import { useState, useEffect } from 'react';
import './ConnectionStatus.css';

export default function ConnectionStatus({ isConnected, lastUpdate }) {
    const [timeSince, setTimeSince] = useState('방금 전');

    useEffect(() => {
        if (!lastUpdate) return;

        const updateTimeSince = () => {
            const seconds = Math.floor((Date.now() - lastUpdate) / 1000);

            if (seconds < 10) {
                setTimeSince('방금 전');
            } else if (seconds < 60) {
                setTimeSince(`${seconds}초 전`);
            } else {
                const minutes = Math.floor(seconds / 60);
                setTimeSince(`${minutes}분 전`);
            }
        };

        updateTimeSince();
        const interval = setInterval(updateTimeSince, 1000);

        return () => clearInterval(interval);
    }, [lastUpdate]);

    return (
        <div className="connection-status">
            <div className="status-indicator">
                <span className={`status-dot ${isConnected ? 'connected' : 'disconnected'}`} />
                <span className="status-text">
                    {isConnected ? 'Connected' : 'Reconnecting...'}
                </span>
            </div>

            {lastUpdate && (
                <div className="last-update">
                    <span className="update-icon">⏰</span>
                    <span className="update-text">{timeSince} 업데이트</span>
                </div>
            )}
        </div>
    );
}
