import React, { useMemo, useState } from 'react'

const SOILS = ['clay', 'sandy', 'loam', 'silt']
const CROPS = ['rice', 'wheat', 'maize', 'pulses', 'vegetables']
const apiBase = import.meta.env.VITE_API_BASE || 'http://localhost:5000'

export default function Advisory() {
  const [soilType, setSoilType] = useState('')
  const [crop, setCrop] = useState('')
  const [region, setRegion] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  const canSubmit = useMemo(() => soilType && crop, [soilType, crop])

  async function onSubmit(e) {
    e.preventDefault()
    if (!canSubmit) return
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const res = await fetch(`${apiBase}/api/recommend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ soilType, crop, region }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data?.error || 'Request failed')
      setResult(data)
    } catch (err) {
      setError(err.message || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div className="bg-white rounded-xl shadow p-6">
        <h2 className="text-2xl font-bold text-green-700 mb-4">Advisory</h2>
        <form onSubmit={onSubmit} className="grid md:grid-cols-3 gap-4">
          <div>
            <label className="block text-lg font-semibold mb-2">Soil type</label>
            <select value={soilType} onChange={e => setSoilType(e.target.value)} className="w-full border rounded-lg px-3 py-3 text-lg focus:outline-none focus:ring-2 focus:ring-green-500">
              <option value="">Select soil</option>
              {SOILS.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-lg font-semibold mb-2">Crop</label>
            <select value={crop} onChange={e => setCrop(e.target.value)} className="w-full border rounded-lg px-3 py-3 text-lg focus:outline-none focus:ring-2 focus:ring-green-500">
              <option value="">Select crop</option>
              {CROPS.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-lg font-semibold mb-2">Region</label>
            <input type="text" value={region} onChange={e => setRegion(e.target.value)} placeholder="e.g., Punjab, India" className="w-full border rounded-lg px-3 py-3 text-lg focus:outline-none focus:ring-2 focus:ring-green-500" />
          </div>
          <div className="md:col-span-3">
            <button disabled={!canSubmit || loading} className="bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white text-xl font-semibold px-6 py-3 rounded-lg">
              {loading ? 'Fetching...' : 'Get Recommendations'}
            </button>
            {error && <span className="text-red-600 text-lg ml-3">{error}</span>}
          </div>
        </form>
      </div>

      {result && (
        <div className="bg-green-50 p-5 rounded-lg mt-6">
          <h3 className="text-xl font-bold text-green-700 mb-3">Recommendations</h3>
          <ul className="space-y-2 text-lg">
            <li><span className="font-semibold">Soil:</span> {result.soilType}</li>
            <li><span className="font-semibold">Crop:</span> {result.crop}</li>
            {result.region ? <li><span className="font-semibold">Region:</span> {result.region}</li> : null}
            <li><span className="font-semibold">Sowing time:</span> {result.recommendation.sowingTime}</li>
            <li><span className="font-semibold">Irrigation:</span> {result.recommendation.irrigation}</li>
            <li><span className="font-semibold">Fertilizer:</span> {result.recommendation.fertilizer}</li>
            {result.recommendation.notes ? <li className="text-gray-600">Note: {result.recommendation.notes}</li> : null}
          </ul>
        </div>
      )}
    </div>
  )
}


