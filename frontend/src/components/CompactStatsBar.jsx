import { Link } from 'react-router-dom';
import '../styles/AdminDashboard.css';

export default function CompactStatsBar({ data, topProducts, activeUsers }) {
    return (
        <div className="compact-stats-bar">
            <div className="container">
                {/* 매출 요약 */}
                <div className="stats-summary">
                    <div className="stat-badge">
                        <span className="stat-icon">👥</span>
                        <div className="stat-content">
                            <span className="stat-label">실시간 접속자</span>
                            <span className="stat-value">{activeUsers}명</span>
                        </div>
                    </div>

                    <div className="stat-badge">
                        <span className="stat-icon">📦</span>
                        <div className="stat-content">
                            <span className="stat-label">총 주문</span>
                            <span className="stat-value">{data.total_orders}건</span>
                        </div>
                    </div>

                    <div className="stat-badge">
                        <span className="stat-icon">💰</span>
                        <div className="stat-content">
                            <span className="stat-label">총 매출</span>
                            <span className="stat-value">{data.total_revenue.toLocaleString()}원</span>
                        </div>
                    </div>
                </div>

                {/* 실시간 자세히 보기 버튼 */}
                <Link to="/dashboard" className="view-dashboard-btn">
                    실시간 자세히 보기 →
                </Link>
            </div>
        </div>
    );
}
