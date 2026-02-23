import './KPICard.css';

export default function KPICard({ icon, title, value }) {
    return (
        <div className="kpi-card card">
            <div className="kpi-header">
                <span className="kpi-icon">{icon}</span>
                <span className="kpi-title">{title}</span>
            </div>

            <div className="kpi-value">{value}</div>
        </div>
    );
}
