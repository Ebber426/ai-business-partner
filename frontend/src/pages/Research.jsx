import { useState, useEffect } from 'react'
import TrendCard from '../components/TrendCard'
import './Research.css'

function Research() {
    const [trends, setTrends] = useState([])
    const [loading, setLoading] = useState(false)
    const [researching, setResearching] = useState(false)
    const [message, setMessage] = useState('')

    useEffect(() => {
        fetchResearch()
    }, [])

    const fetchResearch = async () => {
        setLoading(true)
        try {
            const response = await fetch('/api/research')
            const data = await response.json()
            setTrends(data.results || [])
        } catch (error) {
            console.error('Failed to fetch research:', error)
        } finally {
            setLoading(false)
        }
    }

    const runResearch = async () => {
        setResearching(true)
        setMessage('🔍 Running research... This may take a minute.')

        try {
            const response = await fetch('/api/research/run', { method: 'POST' })
            const data = await response.json()

            if (response.ok && data.success) {
                setMessage(`✅ Found ${data.count} trends!`)
                // Refresh the list
                fetchResearch()
            } else {
                const errorDetail = data.detail || 'Research failed'
                setMessage(`❌ ${errorDetail}`)
                console.error('Research failed:', errorDetail)
            }
        } catch (error) {
            setMessage(`❌ Network error: ${error.message}`)
            console.error('Research error:', error)
        } finally {
            setResearching(false)
        }
    }

    const createProduct = async (keyword) => {
        setMessage(`📦 Creating product: ${keyword}...`)

        try {
            const response = await fetch('/api/products/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ keyword })
            })
            const data = await response.json()

            if (response.ok && data.success) {
                setMessage(`✅ Product created! Link: ${data.link}`)
            } else {
                // Show detailed error from API
                const errorDetail = data.detail || 'Unknown error occurred'
                setMessage(`❌ Failed: ${errorDetail}`)
                console.error('Product creation failed:', errorDetail)
            }
        } catch (error) {
            setMessage(`❌ Network error: ${error.message}`)
            console.error('Product creation error:', error)
        }
    }

    const deleteItem = async (keyword) => {
        setMessage(`🗑️ Deleting: ${keyword}...`)

        try {
            const response = await fetch(`/api/research/${encodeURIComponent(keyword)}`, {
                method: 'DELETE'
            })
            const data = await response.json()

            if (response.ok && data.success) {
                // Remove from UI immediately
                setTrends(trends.filter(t => t.keyword !== keyword))
                setMessage(`✅ Deleted: ${keyword}`)
            } else {
                const errorDetail = data.detail || 'Failed to delete'
                setMessage(`❌ ${errorDetail}`)
                console.error('Delete failed:', errorDetail)
            }
        } catch (error) {
            setMessage(`❌ Network error: ${error.message}`)
            console.error('Delete error:', error)
        }
    }

    const clearAllResearch = async () => {
        if (!window.confirm('Clear all research items from the latest run?')) return

        setMessage('🧹 Clearing all research...')

        try {
            const response = await fetch('/api/research/latest', {
                method: 'DELETE'
            })
            const data = await response.json()

            if (response.ok && data.success) {
                setTrends([])
                setMessage(`✅ Cleared ${data.deleted_count} items`)
            } else {
                const errorDetail = data.detail || 'Failed to clear research'
                setMessage(`❌ ${errorDetail}`)
                console.error('Clear failed:', errorDetail)
            }
        } catch (error) {
            setMessage(`❌ Network error: ${error.message}`)
            console.error('Clear error:', error)
        }
    }

    return (
        <div className="research-page animate-fadeIn">
            <div className="page-header">
                <div className="header-content">
                    <h1 className="page-title">Research</h1>
                    <p className="page-subtitle">Discover trending digital product opportunities</p>
                </div>
                <div className="header-actions">
                    <button
                        className="btn btn-primary"
                        onClick={runResearch}
                        disabled={researching}
                    >
                        {researching ? (
                            <>
                                <div className="spinner"></div>
                                Researching...
                            </>
                        ) : (
                            <>🔍 Run Research</>
                        )}
                    </button>
                    {trends.length > 0 && (
                        <button
                            className="btn btn-secondary"
                            onClick={clearAllResearch}
                            title="Clear all items from latest research run"
                        >
                            🧹 Clear Research
                        </button>
                    )}
                </div>
            </div>

            {message && (
                <div className="message-bar">
                    {message}
                </div>
            )}

            {loading ? (
                <div className="loading-container">
                    <div className="spinner"></div>
                    <p>Loading research data...</p>
                </div>
            ) : trends.length === 0 ? (
                <div className="empty-state">
                    <span style={{ fontSize: '48px' }}>🔍</span>
                    <h3>No Research Data Yet</h3>
                    <p>Click "Run Research" to discover trending products</p>
                </div>
            ) : (
                <div className="trends-grid">
                    {trends.map((trend, i) => (
                        <TrendCard
                            key={`${trend.keyword}-${i}`}
                            keyword={trend.keyword || trend.Keyword}
                            score={parseFloat(trend.signal || trend.Signal || 0)}
                            velocity={parseFloat(trend.velocity || 0)}
                            category={trend.category || 'stable'}
                            confidence={trend.confidence || 'medium'}
                            confidence_score={parseFloat(trend.confidence_score || 0.5)}
                            explanation={trend.explanation || ''}
                            sources={[trend.platform || trend.Platform || 'Google Trends']}
                            onSelect={() => createProduct(trend.keyword || trend.Keyword)}
                            onDelete={deleteItem}
                        />
                    ))}
                </div>
            )}
        </div>
    )
}

export default Research
