import { Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import Research from './pages/Research'
import Products from './pages/Products'
import Publishing from './pages/Publishing'
import Activity from './pages/Activity'
import Settings from './pages/Settings'
import './App.css'

function App() {
    return (
        <div className="app-layout">
            <Sidebar />
            <main className="main-content">
                <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/research" element={<Research />} />
                    <Route path="/products" element={<Products />} />
                    <Route path="/publishing" element={<Publishing />} />
                    <Route path="/activity" element={<Activity />} />
                    <Route path="/settings" element={<Settings />} />
                </Routes>
            </main>
        </div>
    )
}

export default App
