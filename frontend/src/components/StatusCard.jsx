import './StatusCard.css'

function StatusCard({ icon, title, value, subtitle, trend, type = 'default' }) {
    return (
        <div className={`status-card ${type}`}>
            <div className="status-card-icon">{icon}</div>
            <div className="status-card-content">
                <span className="status-card-title">{title}</span>
                <span className="status-card-value">{value}</span>
                {subtitle && <span className="status-card-subtitle">{subtitle}</span>}
                {trend && (
                    <span className={`status-card-trend ${trend > 0 ? 'positive' : 'negative'}`}>
                        {trend > 0 ? '↑' : '↓'} {Math.abs(trend)}%
                    </span>
                )}
            </div>
        </div>
    )
}

export default StatusCard
