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

            if (data.success) {
                setMessage(`✅ Found ${data.count} trends!`)
                // Refresh the list
                fetchResearch()
            } else {
                setMessage('❌ Research failed. Check logs.')
            }
        } catch (error) {
            setMessage(`❌ Error: ${error.message}`)
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

            if (data.success) {
                setMessage(`✅ Product created! Link: ${data.link}`)
            } else {
                setMessage('❌ Failed to create product.')
            }
        } catch (error) {
            setMessage(`❌ Error: ${error.message}`)
        }
    }

    return (
        <div className="research-page animate-fadeIn">
            <div className="page-header">
                <div className="header-content">
                    <h1 className="page-title">Research</h1>
                    <p className="page-subtitle">Discover trending digital product opportunities</p>
                </div>
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
                            key={i}
                            keyword={trend.Keyword || trend.keyword}
                            score={parseFloat(trend.Signal || trend.signal || 0)}
                            sources={[trend.Platform || trend.platform || 'Unknown']}
                            onSelect={() => createProduct(trend.Keyword || trend.keyword)}
                        />
                    ))}
                </div>
            )}
        </div>
    )
}

export default Research
