import { useState, useEffect } from 'react'
import './Activity.css'

function Activity() {
    const [activities, setActivities] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetchActivities()
        // Auto-refresh every 30 seconds
        const interval = setInterval(fetchActivities, 30000)
        return () => clearInterval(interval)
    }, [])

    const fetchActivities = async () => {
        try {
            const response = await fetch('/api/activity?limit=100')
            const data = await response.json()
            setActivities(data.activities || [])
        } catch (error) {
            console.error('Failed to fetch activities:', error)
        } finally {
            setLoading(false)
        }
    }

    const getAgentColor = (agent) => {
        if (agent?.includes('Research')) return 'research'
        if (agent?.includes('Creation')) return 'creation'
        if (agent?.includes('Publishing')) return 'publishing'
        return 'default'
    }

    const formatTime = (timestamp) => {
        try {
            const date = new Date(timestamp)
            return date.toLocaleString()
        } catch {
            return timestamp
        }
    }

    if (loading) {
        return (
            <div className="loading-container">
                <div className="spinner"></div>
                <p>Loading activity log...</p>
            </div>
        )
    }

    return (
        <div className="activity-page animate-fadeIn">
            <div className="page-header">
                <div className="header-content">
                    <h1 className="page-title">Activity Log</h1>
                    <p className="page-subtitle">Real-time system activity</p>
                </div>
                <button className="btn btn-secondary" onClick={fetchActivities}>
                    🔄 Refresh
                </button>
            </div>

            {activities.length === 0 ? (
                <div className="empty-state">
                    <span style={{ fontSize: '48px' }}>📋</span>
                    <h3>No Activity Yet</h3>
                    <p>Run some agents to see activity here</p>
                </div>
            ) : (
                <div className="activity-timeline">
                    {activities.map((activity, i) => (
                        <div key={i} className={`timeline-item ${getAgentColor(activity.agent)}`}>
                            <div className="timeline-dot"></div>
                            <div className="timeline-content">
                                <div className="timeline-header">
                                    <span className="timeline-agent">{activity.agent}</span>
                                    <span className="timeline-time">{formatTime(activity.timestamp)}</span>
                                </div>
                                <div className="timeline-action">{activity.action}</div>
                                {activity.result && (
                                    <div className="timeline-result">{activity.result}</div>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}

export default Activity
