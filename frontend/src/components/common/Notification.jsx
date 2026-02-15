import { useEffect, useState } from 'react';
import './Notification.css';

export const Notification = ({ message, type = 'info', duration = 3000, onClose }) => {
    const [isVisible, setIsVisible] = useState(true);

    useEffect(() => {
        if (duration > 0) {
            const timer = setTimeout(() => {
                setIsVisible(false);
                setTimeout(onClose, 300);
            }, duration);

            return () => clearTimeout(timer);
        }
    }, [duration, onClose]);

    const handleClose = () => {
        setIsVisible(false);
        setTimeout(onClose, 300);
    };

    return (
        <div className={`notification notification-${type} ${isVisible ? 'notification-visible' : 'notification-hidden'}`}>
            <div className="notification-content">
                <span className="notification-icon">
                    {type === 'success' && '✓'}
                    {type === 'error' && '✕'}
                    {type === 'warning' && '⚠'}
                    {type === 'info' && 'ℹ'}
                </span>
                <span className="notification-message">{message}</span>
            </div>
            <button className="notification-close" onClick={handleClose}>
                ✕
            </button>
        </div>
    );
};

export const NotificationContainer = ({ notifications, removeNotification }) => {
    return (
        <div className="notification-container">
            {notifications.map((notification) => (
                <Notification
                    key={notification.id}
                    message={notification.message}
                    type={notification.type}
                    duration={notification.duration}
                    onClose={() => removeNotification(notification.id)}
                />
            ))}
        </div>
    );
};
