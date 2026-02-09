import './TrendCard.css'

function TrendCard({ keyword, score, sources, onSelect }) {
    const getScoreColor = (score) => {
        if (score >= 70) return 'high'
        if (score >= 40) return 'medium'
        return 'low'
    }

    return (
        <div className="trend-card" onClick={onSelect}>
            <div className="trend-header">
                <h3 className="trend-keyword">{keyword}</h3>
                <div className={`trend-score ${getScoreColor(score)}`}>
                    {score.toFixed(1)}
                </div>
            </div>
            <div className="trend-sources">
                {sources?.map((source, i) => (
                    <span key={i} className="trend-source">{source}</span>
                ))}
            </div>
            <button className="trend-action">
                Create Product →
            </button>
        </div>
    )
}

export default TrendCard
