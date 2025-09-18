import React from 'react'
import { NavLink } from 'react-router-dom'

const linkBase = 'px-3 py-2 rounded-lg font-medium hover:bg-green-100'

export default function Navbar() {
  return (
    <nav className="sticky top-0 z-50 bg-white/90 backdrop-blur border-b">
      <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
        <div className="text-xl font-extrabold text-green-700">Your Farming Friend</div>
        <div className="flex gap-2">
          <NavLink to="/" end className={({ isActive }) => `${linkBase} ${isActive ? 'bg-green-200 text-green-900' : 'text-gray-700'}`}>Home</NavLink>
          <NavLink to="/detector" className={({ isActive }) => `${linkBase} ${isActive ? 'bg-green-200 text-green-900' : 'text-gray-700'}`}>Disease Detector</NavLink>
          <NavLink to="/advisory" className={({ isActive }) => `${linkBase} ${isActive ? 'bg-green-200 text-green-900' : 'text-gray-700'}`}>Advisory</NavLink>
          <NavLink to="/analytics" className={({ isActive }) => `${linkBase} ${isActive ? 'bg-green-200 text-green-900' : 'text-gray-700'}`}>Analytics</NavLink>
          <NavLink to="/about" className={({ isActive }) => `${linkBase} ${isActive ? 'bg-green-200 text-green-900' : 'text-gray-700'}`}>About</NavLink>
        </div>
      </div>
    </nav>
  )
}


