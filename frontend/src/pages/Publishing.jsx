import { useState } from 'react'
import './Publishing.css'

function Publishing() {
    const [publishing, setPublishing] = useState(false)
    const [results, setResults] = useState(null)
    const [selectedPlatform, setSelectedPlatform] = useState('both')

    const handlePublish = async () => {
        setPublishing(true)
        setResults(null)

        try {
            const response = await fetch('/api/publish', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ platform: selectedPlatform })
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
                <p className="page-subtitle">Publish products to Etsy and Pinterest</p>
            </div>

            <div className="publishing-grid">
                <div className="card platform-card">
                    <div className="platform-header">
                        <span className="platform-icon">🛍️</span>
                        <div>
                            <h3>Etsy</h3>
                            <p>Create draft listings</p>
                        </div>
                    </div>
                    <label className="platform-checkbox">
                        <input
                            type="checkbox"
                            checked={selectedPlatform === 'etsy' || selectedPlatform === 'both'}
                            onChange={(e) => {
                                if (e.target.checked) {
                                    setSelectedPlatform(selectedPlatform === 'pinterest' ? 'both' : 'etsy')
                                } else {
                                    setSelectedPlatform(selectedPlatform === 'both' ? 'pinterest' : '')
                                }
                            }}
                        />
                        <span>Include Etsy</span>
                    </label>
                </div>

                <div className="card platform-card">
                    <div className="platform-header">
                        <span className="platform-icon">📌</span>
                        <div>
                            <h3>Pinterest</h3>
                            <p>Create pins with links</p>
                        </div>
                    </div>
                    <label className="platform-checkbox">
                        <input
                            type="checkbox"
                            checked={selectedPlatform === 'pinterest' || selectedPlatform === 'both'}
                            onChange={(e) => {
                                if (e.target.checked) {
                                    setSelectedPlatform(selectedPlatform === 'etsy' ? 'both' : 'pinterest')
                                } else {
                                    setSelectedPlatform(selectedPlatform === 'both' ? 'etsy' : '')
                                }
                            }}
                        />
                        <span>Include Pinterest</span>
                    </label>
                </div>
            </div>

            <div className="publish-action">
                <button
                    className="btn btn-primary btn-lg"
                    onClick={handlePublish}
                    disabled={publishing || !selectedPlatform}
                >
                    {publishing ? (
                        <>
                            <div className="spinner"></div>
                            Publishing...
                        </>
                    ) : (
                        <>🚀 Publish Latest Product</>
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

                            {results.etsy && (
                                <div className={`result-item ${results.etsy.success ? 'success' : 'error'}`}>
                                    <span>{results.etsy.success ? '✅' : '❌'}</span>
                                    <span>Etsy: {results.etsy.success ? results.etsy.url || 'Created' : results.etsy.error}</span>
                                </div>
                            )}

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
