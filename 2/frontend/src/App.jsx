import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar.jsx'
import Home from './pages/Home.jsx'
import DiseaseDetector from './pages/DiseaseDetector.jsx'
import Advisory from './pages/Advisory.jsx'
import Analytics from './pages/Analytics.jsx'
import About from './pages/About.jsx'

const SOILS = ['clay', 'sandy', 'loam', 'silt']
const CROPS = ['rice', 'wheat', 'maize', 'pulses', 'vegetables']

const apiBase = import.meta.env.VITE_API_BASE || 'http://localhost:5000'

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <main className="max-w-6xl mx-auto px-4 py-6">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/detector" element={<DiseaseDetector />} />
          <Route path="/advisory" element={<Advisory />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/about" element={<About />} />
        </Routes>
        <footer className="mt-10 text-center text-gray-500 text-sm">© 2025 Smart Farming AI | Built with love and thankfulness</footer>
      </main>
    </BrowserRouter>
  )
}

// SDG UI removed


