import ConnectionStatus from './ConnectionStatus';
import KPICard from './KPICard';
import TopProductsTable from './TopProductsTable';
import './RealtimeDashboard.css';

export default function RealtimeDashboard({
    isConnected,
    lastUpdate,
    activeUsers,
    dailySales,
    topProducts
}) {
    return (
        <section className="realtime-dashboard">
            <div className="dashboard-header">
                <h2>실시간 대시보드</h2>
                <ConnectionStatus isConnected={isConnected} lastUpdate={lastUpdate} />
            </div>

            {/* KPI 카드 */}
            <div className="kpi-grid">
                <KPICard
                    icon="👥"
                    title="실시간 접속자"
                    value={`${activeUsers}명`}
                />

                <KPICard
                    icon="📦"
                    title="총 주문"
                    value={`${dailySales.total_orders}건`}
                />

                <KPICard
                    icon="💰"
                    title="총 매출"
                    value={`₩${dailySales.total_revenue.toLocaleString()}`}
                />
            </div>

            {/* TOP 10 테이블 */}
            <div className="top-products-section">
                <TopProductsTable products={topProducts} />
            </div>
        </section>
    );
}
