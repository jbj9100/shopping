import { useState } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import DailySalesCard from '../components/DailySalesCard';
import TopProductsTable from '../components/TopProductsTable';
import '../styles/AdminDashboard.css';

export default function AdminDashboard() {
    const [dailySales, setDailySales] = useState({
        date: new Date().toISOString().split('T')[0],
        total_orders: 0,
        total_revenue: 0
    });
    const [topProducts, setTopProducts] = useState([]);

    // WebSocket analytics 채널 구독
    const { isConnected } = useWebSocket(
        'ws://localhost:8001/websocket/ws/analytics',
        {
            onMessage: (data) => {
                console.log('📊 Analytics 데이터 수신:', data);

                if (data.type === 'STATS_UPDATED') {
                    setDailySales(data.data.daily_sales);
                    setTopProducts(data.data.top_products || []);
                }
            },
            onOpen: () => {
                console.log('✅ Analytics WebSocket 연결됨');
            },
            onError: (error) => {
                console.error('❌ Analytics WebSocket 에러:', error);
            }
        }
    );

    return (
        <div className="admin-dashboard">
            <div className="dashboard-header">
                <h1>📊 관리자 대시보드</h1>
                <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
                    <span className="status-dot"></span>
                    {isConnected ? '실시간 연결됨' : '연결 중...'}
                </div>
            </div>

            <DailySalesCard data={dailySales} />
            <TopProductsTable products={topProducts} />
        </div>
    );
}
