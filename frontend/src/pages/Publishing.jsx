import { useState } from 'react'
import './Publishing.css'

function Publishing() {
    const [publishing, setPublishing] = useState(false)
    const [results, setResults] = useState(null)

    const handlePublish = async () => {
        setPublishing(true)
        setResults(null)

        try {
            const response = await fetch('/api/publish', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ platform: 'pinterest' })
            })
            const data = await response.json()
            setResults(data)
        } catch (error) {
            setResults({ success: false, message: error.message })
        } finally {
            setPublishing(false)
        }
    }

    return (
        <div className="publishing-page animate-fadeIn">
            <div className="page-header">
                <h1 className="page-title">Publishing</h1>
                <p className="page-subtitle">Publish products to Pinterest for marketing automation</p>
            </div>

            <div className="publishing-grid">
                <div className="card platform-card">
                    <div className="platform-header">
                        <span className="platform-icon">📌</span>
                        <div>
                            <h3>Pinterest</h3>
                            <p>Create pins with links to your products</p>
                        </div>
                    </div>
                    <p className="platform-note">
                        💡 Products are manually uploaded to your shop. This app creates marketing pins on Pinterest to drive traffic.
                    </p>
                </div>
            </div>

            <div className="publish-action">
                <button
                    className="btn btn-primary btn-lg"
                    onClick={handlePublish}
                    disabled={publishing}
                >
                    {publishing ? (
                        <>
                            <div className="spinner"></div>
                            Publishing...
                        </>
                    ) : (
                        <>🚀 Publish to Pinterest</>
                    )}
                </button>
            </div>

            {results && (
                <div className="results-card card">
                    <h3>Publishing Results</h3>

                    {results.success === false ? (
                        <div className="result-item error">
                            <span>❌</span>
                            <span>{results.message || 'Publishing failed'}</span>
                        </div>
                    ) : (
                        <>
                            <p className="result-product">Product: {results.product_name}</p>

                            {results.pinterest && (
                                <div className={`result-item ${results.pinterest.success ? 'success' : 'error'}`}>
                                    <span>{results.pinterest.success ? '✅' : '❌'}</span>
                                    <span>Pinterest: {results.pinterest.success ? results.pinterest.url || 'Created' : results.pinterest.error}</span>
                                </div>
                            )}
                        </>
                    )}
                </div>
            )}
        </div>
    )
}

export default Publishing
