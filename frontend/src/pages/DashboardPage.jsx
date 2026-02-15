import { useState } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import '../styles/Dashboard.css';

export default function DashboardPage() {
    const [dailySales, setDailySales] = useState({
        date: new Date().toISOString().split('T')[0],
        total_orders: 0,
        total_revenue: 0
    });
    const [topProducts, setTopProducts] = useState([]);
    const [activeUsers, setActiveUsers] = useState(0);

    // Analytics WebSocket
    useWebSocket('ws://localhost:8001/websocket/ws/analytics', {
        onMessage: (data) => {
            if (data.type === 'STATS_UPDATED') {
                setDailySales(data.data.daily_sales);
                setTopProducts(data.data.top_products || []);
            }
            if (data.type === 'USER_COUNT_UPDATED') {
                setActiveUsers(data.count);
            }
        }
    });

    return (
        <div className="dashboard-page">
            <div className="dashboard-container">
                {/* 헤더 */}
                <div className="dashboard-header">
                    <h1>📊 실시간 대시보드</h1>
                    <div className="header-badges">
                        <span className="badge-realtime">● 실시간</span>
                        <span className="badge-connected">● Connected</span>
                    </div>
                </div>

                {/* 통계 카드 */}
                <div className="stats-cards">
                    <div className="stat-card">
                        <div className="stat-card-header">
                            <span className="stat-icon">👥</span>
                            <span className="stat-title">실시간 접속자</span>
                        </div>
                        <div className="stat-value-large">{activeUsers}</div>
                        <div className="stat-trend">
                            <span className="trend-chart">📈</span>
                            <span className="trend-value">1,300명 ↑</span>
                        </div>
                    </div>

                    <div className="stat-card">
                        <div className="stat-card-header">
                            <span className="stat-icon">📦</span>
                            <span className="stat-title">오늘 주문</span>
                        </div>
                        <div className="stat-value-large">{dailySales.total_orders}</div>
                        <div className="stat-trend positive">
                            <span className="trend-label">+ 8%</span>
                            <span className="trend-value">₩{dailySales.total_revenue.toLocaleString()} ↑</span>
                        </div>
                    </div>
                </div>

                {/* TOP 10 테이블 */}
                <div className="dashboard-section">
                    <div className="section-tabs">
                        <button className="tab-btn active">판매량</button>
                        <button className="tab-btn">판매액</button>
                    </div>

                    <div className="top-products-table">
                        <table>
                            <thead>
                                <tr>
                                    <th>순위</th>
                                    <th>상품명</th>
                                    <th>판매량</th>
                                    <th>등락</th>
                                </tr>
                            </thead>
                            <tbody>
                                {topProducts.map((product, index) => (
                                    <tr key={product.product_id}>
                                        <td className="rank-cell">
                                            {index === 0 && <span className="rank-badge gold">{index + 1}</span>}
                                            {index === 1 && <span className="rank-badge silver">{index + 1}</span>}
                                            {index === 2 && <span className="rank-badge bronze">{index + 1}</span>}
                                            {index > 2 && <span className="rank-number">{index + 1}</span>}
                                        </td>
                                        <td className="product-cell">
                                            <div className="product-info">
                                                <img src={`/api/placeholder/40/40`} alt="" className="product-thumb" />
                                                <span>{product.product_name}</span>
                                            </div>
                                        </td>
                                        <td className="sales-cell">{product.purchase_count}</td>
                                        <td className="change-cell">
                                            <span className="change-positive">+12</span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
}
