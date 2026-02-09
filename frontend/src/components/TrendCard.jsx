import './TrendCard.css'

function TrendCard({ keyword, score, velocity, category, confidence, confidence_score, explanation, sources, onSelect, onDelete }) {
    const getScoreColor = (score) => {
        if (score >= 70) return 'high'
        if (score >= 40) return 'medium'
        return 'low'
    }

    const getCategoryIcon = (category) => {
        switch (category) {
            case 'emerging':
                return '📈'
            case 'spiking':
                return '🔥'
            case 'stable':
                return '💤'
            default:
                return '📊'
        }
    }

    const getCategoryLabel = (category) => {
        return category ? category.charAt(0).toUpperCase() + category.slice(1) : 'Stable'
    }

    const handleDelete = (e) => {
        e.stopPropagation()
        if (onDelete) {
            onDelete(keyword)
        }
    }

    return (
        <div className="trend-card">
            <div className="trend-header">
                <div className="trend-title-row">
                    <span className="category-badge" title={getCategoryLabel(category)}>
                        {getCategoryIcon(category)}
                    </span>
                    <h3 className="trend-keyword">{keyword}</h3>
                </div>
                <div className={`trend-score ${getScoreColor(score)}`}>
                    {typeof score === 'number' && !isNaN(score) ? score.toFixed(1) : '—'}
                </div>
            </div>

            {explanation && (
                <div className="trend-explanation">
                    💡 {explanation}
                </div>
            )}

            <div className="trend-metrics">
                <div className="metric">
                    <span className="metric-label">Velocity:</span>
                    <span className={`metric-value ${velocity > 30 ? 'positive' : velocity < -30 ? 'negative' : ''}`}>
                        {velocity > 0 ? '+' : ''}{velocity}%
                    </span>
                </div>
                <div className="metric">
                    <span className="metric-label">Confidence:</span>
                    <span className={`metric-value confidence-${confidence || 'medium'}`} title={`Score: ${(confidence_score || 0.5).toFixed(2)}`}>
                        {(confidence || 'medium').toUpperCase()}
                    </span>
                </div>
            </div>

            <div className="trend-sources">
                {sources?.map((source, i) => (
                    <span key={i} className="trend-source">{source}</span>
                ))}
            </div>

            <div className="trend-actions">
                <button className="trend-action" onClick={onSelect}>
                    Create Product →
                </button>
                <button className="trend-delete" onClick={handleDelete} title="Delete this trend">
                    🗑️
                </button>
            </div>
        </div>
    )
}

export default TrendCard
