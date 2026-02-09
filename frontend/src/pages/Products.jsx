import { useState, useEffect } from 'react'
import './Products.css'

function Products() {
    const [products, setProducts] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetchProducts()
    }, [])

    const fetchProducts = async () => {
        try {
            const response = await fetch('/api/products')
            const data = await response.json()
            setProducts(data.products || [])
        } catch (error) {
            console.error('Failed to fetch products:', error)
        } finally {
            setLoading(false)
        }
    }

    const getStatusBadge = (status) => {
        if (status?.includes('Published')) return 'success'
        if (status?.includes('Failed')) return 'error'
        return 'info'
    }

    if (loading) {
        return (
            <div className="loading-container">
                <div className="spinner"></div>
                <p>Loading products...</p>
            </div>
        )
    }

    return (
        <div className="products-page animate-fadeIn">
            <div className="page-header">
                <h1 className="page-title">Products</h1>
                <p className="page-subtitle">Your created digital products</p>
            </div>

            {products.length === 0 ? (
                <div className="empty-state">
                    <span style={{ fontSize: '48px' }}>📦</span>
                    <h3>No Products Yet</h3>
                    <p>Go to Research and create your first product</p>
                </div>
            ) : (
                <div className="products-table-wrapper">
                    <table className="products-table">
                        <thead>
                            <tr>
                                <th>Product Name</th>
                                <th>Type</th>
                                <th>Status</th>
                                <th>Created</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {products.map((product, i) => (
                                <tr key={i}>
                                    <td className="product-name">{product['Product Name']}</td>
                                    <td>{product['Type']}</td>
                                    <td>
                                        <span className={`badge badge-${getStatusBadge(product['Status'])}`}>
                                            {product['Status']}
                                        </span>
                                    </td>
                                    <td className="product-date">
                                        {new Date(product['Timestamp']).toLocaleDateString()}
                                    </td>
                                    <td>
                                        {product['Link'] && (
                                            <a href={product['Link']} target="_blank" rel="noopener noreferrer" className="btn btn-secondary btn-sm">
                                                View →
                                            </a>
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    )
}

export default Products
