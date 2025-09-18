import React, { useCallback, useMemo, useRef, useState } from 'react'

const API_BASE = import.meta.env.VITE_ML_API_BASE || 'http://localhost:8000'

export default function LeafDiseaseDetector() {
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [progressText, setProgressText] = useState('')
  const dropRef = useRef(null)

  const isValid = useMemo(() => !!file && /^image\//.test(file?.type || ''), [file])

  const onFile = useCallback((f) => {
    if (!f) return
    if (!/^image\//.test(f.type)) {
      setError('Invalid file. Please select an image.')
      setFile(null)
      setPreview('')
      return
    }
    if (f.size > 5 * 1024 * 1024) {
      setError('Image too large (max 5 MB).')
      setFile(null)
      setPreview('')
      return
    }
    setError('')
    setFile(f)
    setPreview(URL.createObjectURL(f))
  }, [])

  const onInputChange = (e) => onFile(e.target.files?.[0])

  const onDrop = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    const f = e.dataTransfer.files?.[0]
    onFile(f)
  }, [onFile])

  const onDragOver = (e) => {
    e.preventDefault()
    e.stopPropagation()
  }

  async function upload() {
    if (!isValid) return
    setLoading(true)
    setResult(null)
    setError('')
    setProgressText('Uploading...')
    try {
      const form = new FormData()
      form.append('image', file)
      const res = await fetch(`${API_BASE}/api/detect`, { method: 'POST', body: form })
      const data = await res.json()
      if (!res.ok) throw new Error(data?.detail || 'Server error')
      setProgressText('Processing complete')
      setResult(data)
    } catch (err) {
      setError(err.message || 'Upload failed. Try again later.')
    } finally {
      setLoading(false)
    }
  }

  function reset() {
    setFile(null)
    setPreview('')
    setResult(null)
    setError('')
    setProgressText('')
  }

  return (
    <div className="bg-white rounded-xl shadow p-6">
      <h2 className="text-2xl font-bold mb-2">Leaf Image Upload (AI Disease Detection)</h2>
      <p className="text-gray-600 mb-4">Upload a clear photo of a single leaf for analysis.</p>

      <div
        ref={dropRef}
        onDrop={onDrop}
        onDragOver={onDragOver}
        className="border-2 border-dashed rounded-lg p-6 text-center mb-4"
        aria-label="Drag and drop image area"
        tabIndex={0}
      >
        <p className="mb-2">Drag & drop an image here, or</p>
        <label className="inline-block bg-green-600 text-white px-4 py-2 rounded cursor-pointer">
          Choose Image
          <input type="file" accept="image/*" onChange={onInputChange} className="hidden" />
        </label>
        <div className="text-sm text-gray-500 mt-2">Max 5 MB. JPG/PNG/WebP.</div>
      </div>

      {preview && (
        <div className="mb-4">
          <img src={preview} alt="Selected leaf preview" className="max-h-64 rounded" />
        </div>
      )}

      <div className="flex items-center gap-3 mb-4">
        <button
          disabled={!isValid || loading}
          onClick={upload}
          className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-6 py-2 rounded"
        >
          {loading ? 'Analyzing...' : 'Analyze Image'}
        </button>
        <button onClick={reset} className="px-4 py-2 rounded border">Upload another</button>
        {progressText && <span className="text-gray-600 text-sm">{progressText}</span>}
      </div>

      {error && (
        <div className="bg-red-50 text-red-700 p-3 rounded mb-4">
          {error}
          <div className="text-sm text-red-600 mt-1">
            Ensure the file is an image under 5 MB and try again.
          </div>
        </div>
      )}

      {result && (
        <div className="bg-gray-50 rounded p-4">
          <div className="mb-3">
            <div className="text-lg font-semibold">Top prediction: {result.top_prediction.label}</div>
            <Progress value={Math.round(result.top_prediction.probability * 100)} />
          </div>
          <div>
            <div className="font-semibold mb-1">All predictions</div>
            <ul className="space-y-1">
              {result.predictions.map((p) => (
                <li key={p.label} className="flex items-center gap-2">
                  <span className="w-40">{p.label}</span>
                  <Progress value={Math.round(p.probability * 100)} />
                </li>
              ))}
            </ul>
          </div>
          <div className="mt-4">
            <div className="font-semibold mb-1">Suggestions</div>
            <ul className="list-disc ml-6">
              {(result.confidence < 0.5 ? result.suggestions.low_confidence : result.suggestions[result.top_prediction.label] || []).map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  )
}

function Progress({ value }) {
  return (
    <div className="w-full bg-white border rounded h-3 overflow-hidden" aria-valuemin={0} aria-valuemax={100} aria-valuenow={value} role="progressbar">
      <div className="h-full bg-green-600" style={{ width: `${value}%` }} />
    </div>
  )
}


