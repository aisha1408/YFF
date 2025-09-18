import React from 'react'
import { Link } from 'react-router-dom'

export default function Home() {
  return (
    <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-green-50 via-emerald-50 to-blue-50 p-10">
      <div className="max-w-3xl">
        <h1 className="text-4xl md:text-5xl font-extrabold text-green-700">Your Farming Friend</h1>
        <p className="mt-4 text-lg text-gray-700">
          This is your one-stop digital farming companion. Simply upload a photo of your crop’s leaf and our AI-powered disease detection identifies common plant problems instantly. Alongside diagnosis, we provide practical solutions to crop issues — from fertilizer use and pest management to sustainable farming tips. Stay ahead of risks with real-time weather insights tailored to your region, so you can plan irrigation, sowing, and harvesting with confidence. Farming made simpler, smarter, and sustainable.
        </p>
        <Link to="/detector" className="inline-block mt-6 bg-green-600 hover:bg-green-700 text-white font-semibold px-6 py-3 rounded-lg shadow">
          Try Disease Detector
        </Link>
      </div>
      <div className="absolute -right-10 -bottom-10 w-48 h-48 bg-green-200/50 rounded-full blur-2xl" />
      <div className="absolute -right-24 bottom-16 w-64 h-64 bg-emerald-200/50 rounded-full blur-3xl" />
    </div>
  )
}


