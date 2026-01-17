import ConnectionStatus from './ConnectionStatus';
import TopProductsTable from './TopProductsTable';
import './MiniDashboard.css';

export default function MiniDashboard({
    isConnected,
    lastUpdate,
    activeUsers,
    dailySales,
    topProducts
}) {
    return (
        <div className="mini-dashboard-card">
            {/* 상단: 연결 상태 */}
            <div className="mini-header">
                <ConnectionStatus isConnected={isConnected} lastUpdate={lastUpdate} />
            </div>

            {/* 중단: KPI (접속자, 주문, 매출) */}
            <div className="mini-kpi-row">
                <div className="mini-kpi-item">
                    <span className="mini-kpi-icon">👥</span>
                    <div className="mini-kpi-content">
                        <span className="mini-kpi-label">실시간 접속자</span>
                        <span className="mini-kpi-value">{activeUsers}명</span>
                    </div>
                </div>
                <div className="mini-kpi-divider"></div>

                <div className="mini-kpi-item">
                    <span className="mini-kpi-icon">📦</span>
                    <div className="mini-kpi-content">
                        <span className="mini-kpi-label">총 주문</span>
                        <span className="mini-kpi-value">{dailySales.total_orders}건</span>
                    </div>
                </div>
                <div className="mini-kpi-divider"></div>

                <div className="mini-kpi-item">
                    <span className="mini-kpi-icon">💰</span>
                    <div className="mini-kpi-content">
                        <span className="mini-kpi-label">총 매출</span>
                        <span className="mini-kpi-value">₩{dailySales.total_revenue.toLocaleString()}</span>
                    </div>
                </div>
            </div>

            {/* 하단: 실시간 TOP 3 */}
            <div className="mini-top-list">
                <div className="mini-list-header">
                    <h3>실시간 TOP 3</h3>
                    <span className="header-sub">순위 🪁</span>
                </div>

                {/* Top 3만 전달 - TopProductsTable이 이미 스타일링 되어 있으므로 slice해서 전달 */}
                <div className="mini-table-wrapper">
                    <TopProductsTable products={topProducts.slice(0, 3)} hideHeader={true} />
                </div>


            </div>
        </div>
    );
}
