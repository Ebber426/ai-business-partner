import { useState, useEffect } from 'react'
import StatusCard from '../components/StatusCard'
import './Dashboard.css'

function Dashboard() {
    const [status, setStatus] = useState(null)
    const [revenue, setRevenue] = useState(0)
    const [products, setProducts] = useState([])
    const [activities, setActivities] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetchDashboardData()
    }, [])

    const fetchDashboardData = async () => {
        try {
            const [statusRes, revenueRes, productsRes, activityRes] = await Promise.all([
                fetch('/api/status'),
                fetch('/api/revenue'),
                fetch('/api/products'),
                fetch('/api/activity?limit=5')
            ])

            const statusData = await statusRes.json()
            const revenueData = await revenueRes.json()
            const productsData = await productsRes.json()
            const activityData = await activityRes.json()

            setStatus(statusData)
            setRevenue(revenueData.total)
            setProducts(productsData.products || [])
            setActivities(activityData.activities || [])
        } catch (error) {
            console.error('Failed to fetch dashboard data:', error)
        } finally {
            setLoading(false)
        }
    }

    if (loading) {
        return (
            <div className="loading-container">
                <div className="spinner"></div>
                <p>Loading dashboard...</p>
            </div>
        )
    }

    return (
        <div className="dashboard animate-fadeIn">
            <div className="page-header">
                <h1 className="page-title">Dashboard</h1>
                <p className="page-subtitle">Welcome to your AI Business Partner</p>
            </div>

            <div className="stats-grid">
                <StatusCard
                    icon="🚀"
                    title="System Status"
                    value={status?.status === 'online' ? 'Online' : 'Offline'}
                    subtitle={`Version ${status?.version || '2.0'}`}
                    type="success"
                />
                <StatusCard
                    icon="💰"
                    title="Total Revenue"
                    value={`$${revenue.toFixed(2)}`}
                    subtitle="All time earnings"
                />
                <StatusCard
                    icon="📦"
                    title="Products"
                    value={products.length}
                    subtitle="Created products"
                />
                <StatusCard
                    icon="📊"
                    title="Today's Actions"
                    value={activities.length}
                    subtitle="Recent activities"
                />
            </div>

            <div className="dashboard-grid">
                <div className="card">
                    <div className="card-header">
                        <h2 className="card-title">Recent Activity</h2>
                    </div>
                    <div className="activity-list">
                        {activities.length === 0 ? (
                            <div className="empty-state">
                                <p>No recent activity</p>
                            </div>
                        ) : (
                            activities.map((activity, i) => (
                                <div key={i} className="activity-item">
                                    <div className="activity-agent">{activity.agent}</div>
                                    <div className="activity-action">{activity.action}</div>
                                    <div className="activity-result">{activity.result}</div>
                                </div>
                            ))
                        )}
                    </div>
                </div>

                <div className="card">
                    <div className="card-header">
                        <h2 className="card-title">Quick Actions</h2>
                    </div>
                    <div className="quick-actions">
                        <a href="/research" className="quick-action-btn">
                            <span className="quick-action-icon">🔍</span>
                            <span>Run Research</span>
                        </a>
                        <a href="/products" className="quick-action-btn">
                            <span className="quick-action-icon">📦</span>
                            <span>View Products</span>
                        </a>
                        <a href="/publishing" className="quick-action-btn">
                            <span className="quick-action-icon">🚀</span>
                            <span>Publish</span>
                        </a>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Dashboard
