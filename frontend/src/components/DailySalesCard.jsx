export default function DailySalesCard({ data }) {
    return (
        <div className="stats-card">
            <h2>💰 오늘의 매출 현황</h2>
            <p className="stats-date">{data.date || '날짜 없음'}</p>

            <div className="stats-grid stats-grid-2">
                <div className="stat-item">
                    <div className="stat-icon">📦</div>
                    <span className="stat-label">주문 건수</span>
                    <span className="stat-value">{data.total_orders.toLocaleString()}건</span>
                </div>

                <div className="stat-item">
                    <div className="stat-icon">💵</div>
                    <span className="stat-label">총 매출</span>
                    <span className="stat-value">{data.total_revenue.toLocaleString()}원</span>
                </div>
            </div>
        </div>
    );
}
