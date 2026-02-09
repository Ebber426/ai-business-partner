import './Settings.css'

function Settings() {
    return (
        <div className="settings-page animate-fadeIn">
            <div className="page-header">
                <h1 className="page-title">Settings</h1>
                <p className="page-subtitle">Configure your AI Business Partner</p>
            </div>

            <div className="settings-grid">
                <div className="card settings-section">
                    <h3>🔑 API Credentials</h3>
                    <p className="settings-note">
                        API credentials are configured in the <code>.env</code> file on the server.
                    </p>

                    <div className="settings-list">
                        <div className="settings-item">
                            <span className="settings-label">Google Sheets</span>
                            <span className="badge badge-success">Connected</span>
                        </div>
                        <div className="settings-item">
                            <span className="settings-label">Etsy API</span>
                            <span className="badge badge-warning">Not Configured</span>
                        </div>
                        <div className="settings-item">
                            <span className="settings-label">Pinterest API</span>
                            <span className="badge badge-warning">Not Configured</span>
                        </div>
                    </div>
                </div>

                <div className="card settings-section">
                    <h3>📊 Research Keywords</h3>
                    <p className="settings-note">
                        Default keywords used by the Research Agent
                    </p>

                    <div className="keyword-list">
                        {[
                            'daily planner',
                            'budget tracker',
                            'habit tracker',
                            'weekly planner',
                            'study planner'
                        ].map((kw, i) => (
                            <span key={i} className="keyword-tag">{kw}</span>
                        ))}
                    </div>
                </div>

                <div className="card settings-section">
                    <h3>ℹ️ About</h3>
                    <div className="about-info">
                        <div className="about-row">
                            <span>Version</span>
                            <span>2.0.0</span>
                        </div>
                        <div className="about-row">
                            <span>Backend</span>
                            <span>FastAPI + Python</span>
                        </div>
                        <div className="about-row">
                            <span>Frontend</span>
                            <span>React + Vite</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Settings
