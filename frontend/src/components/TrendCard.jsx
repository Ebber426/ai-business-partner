import './TrendCard.css'

function TrendCard({ keyword, score, sources, onSelect, onDelete }) {
    const getScoreColor = (score) => {
        if (score >= 70) return 'high'
        if (score >= 40) return 'medium'
        return 'low'
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
                <h3 className="trend-keyword">{keyword}</h3>
                <div className={`trend-score ${getScoreColor(score)}`}>
                    {typeof score === 'number' && !isNaN(score) ? score.toFixed(1) : '—'}
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
