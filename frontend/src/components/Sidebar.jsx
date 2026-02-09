import { NavLink } from 'react-router-dom'
import './Sidebar.css'

function Sidebar() {
    const navItems = [
        { path: '/', icon: '📊', label: 'Dashboard' },
        { path: '/research', icon: '🔍', label: 'Research' },
        { path: '/products', icon: '📦', label: 'Products' },
        { path: '/publishing', icon: '🚀', label: 'Publishing' },
        { path: '/activity', icon: '📋', label: 'Activity Log' },
        { path: '/settings', icon: '⚙️', label: 'Settings' },
    ]

    return (
        <aside className="sidebar">
            <div className="sidebar-header">
                <div className="logo">
                    <span className="logo-icon">🤖</span>
                    <div className="logo-text">
                        <span className="logo-title">AI Business</span>
                        <span className="logo-subtitle">Partner</span>
                    </div>
                </div>
            </div>

            <nav className="sidebar-nav">
                {navItems.map((item) => (
                    <NavLink
                        key={item.path}
                        to={item.path}
                        className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
                    >
                        <span className="nav-icon">{item.icon}</span>
                        <span className="nav-label">{item.label}</span>
                    </NavLink>
                ))}
            </nav>

            <div className="sidebar-footer">
                <div className="status-indicator">
                    <span className="status-dot"></span>
                    <span className="status-text">System Online</span>
                </div>
            </div>
        </aside>
    )
}

export default Sidebar
