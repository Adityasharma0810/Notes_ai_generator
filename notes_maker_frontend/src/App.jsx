import { useState } from 'react'
import './App.css'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'

const SHANTANU_QUOTES = [
  "I love beer! 🍺",
  "Bhai padh le, exam aane wala hai 📚",
  "Notes banao, nahi toh rona padega 😭",
  "Ek aur chai ho jaaye? ☕",
  "TSP solve karna hai? Brute force maar do 💪",
  "Sleep is overrated, notes are not 🌙",
  "I didn't choose the study life, the study life chose me 😤",
  "Knapsack problem? My life is a knapsack problem 🎒",
]

const MODES = [
  {
    value: 'detailed',
    label: 'Detailed Notes',
    desc: 'Full explanations, examples & definitions',
    emoji: '📖',
  },
  {
    value: 'important',
    label: 'MCQ Pointer Notes',
    desc: 'Bullet points for quick revision & MCQs',
    emoji: '🎯',
  },
  {
    value: 'mixed',
    label: 'Mixed',
    desc: 'Best of both — explanations + key points',
    emoji: '⚡',
  },
]

export default function App() {
  const [files, setFiles] = useState([])
  const [mode, setMode] = useState('detailed')
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)
  const [quote] = useState(
    () => SHANTANU_QUOTES[Math.floor(Math.random() * SHANTANU_QUOTES.length)]
  )
  const [dragOver, setDragOver] = useState(false)

  function handleFileChange(e) {
    setFiles(Array.from(e.target.files))
    setResults(null)
    setError(null)
  }

  function handleDrop(e) {
    e.preventDefault()
    setDragOver(false)
    const dropped = Array.from(e.dataTransfer.files)
    setFiles(dropped)
    setResults(null)
    setError(null)
  }

  function removeFile(index) {
    setFiles(files.filter((_, i) => i !== index))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    if (!files.length) return

    setLoading(true)
    setError(null)
    setResults(null)

    const formData = new FormData()
    files.forEach((f) => formData.append('files', f))
    formData.append('mode', mode)

    try {
      const res = await fetch(`${API_BASE}/generate-notes`, {
        method: 'POST',
        body: formData,
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Something went wrong')
      setResults(data.results)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  function downloadPdf(pdfUrl, filename) {
    const url = `${API_BASE}${pdfUrl}`
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
  }

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-inner">
          <div className="bot-avatar">🤖</div>
          <div className="bot-info">
            <h1 className="bot-name">Shantanu</h1>
            <span className="bot-status">● Online</span>
          </div>
        </div>
        <div className="bot-quote">"{quote}"</div>
      </header>

      <main className="main">
        <form onSubmit={handleSubmit} className="upload-form">

          {/* Drop zone */}
          <div
            className={`dropzone ${dragOver ? 'drag-over' : ''} ${files.length ? 'has-files' : ''}`}
            onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            onClick={() => document.getElementById('file-input').click()}
          >
            <input
              id="file-input"
              type="file"
              multiple
              accept=".pdf,.pptx,.png,.jpg,.jpeg"
              onChange={handleFileChange}
              style={{ display: 'none' }}
            />
            {files.length === 0 ? (
              <>
                <div className="drop-icon">📂</div>
                <p className="drop-text">Drop your files here or <span className="drop-link">browse</span></p>
                <p className="drop-hint">Supports PDF, PPTX, PNG, JPG</p>
              </>
            ) : (
              <div className="file-list" onClick={(e) => e.stopPropagation()}>
                {files.map((f, i) => (
                  <div key={i} className="file-chip">
                    <span className="file-icon">{fileIcon(f.name)}</span>
                    <span className="file-name">{f.name}</span>
                    <button
                      type="button"
                      className="file-remove"
                      onClick={() => removeFile(i)}
                      aria-label={`Remove ${f.name}`}
                    >×</button>
                  </div>
                ))}
                <button
                  type="button"
                  className="add-more"
                  onClick={() => document.getElementById('file-input').click()}
                >+ Add more</button>
              </div>
            )}
          </div>

          {/* Mode selector */}
          <div className="mode-section">
            <p className="mode-label">What type of notes do you want?</p>
            <div className="mode-cards">
              {MODES.map((m) => (
                <label
                  key={m.value}
                  className={`mode-card ${mode === m.value ? 'selected' : ''}`}
                >
                  <input
                    type="radio"
                    name="mode"
                    value={m.value}
                    checked={mode === m.value}
                    onChange={() => setMode(m.value)}
                  />
                  <span className="mode-emoji">{m.emoji}</span>
                  <span className="mode-title">{m.label}</span>
                  <span className="mode-desc">{m.desc}</span>
                </label>
              ))}
            </div>
          </div>

          <button
            type="submit"
            className="submit-btn"
            disabled={loading || files.length === 0}
          >
            {loading ? (
              <><span className="spinner" /> Generating notes...</>
            ) : (
              '✨ Generate Notes'
            )}
          </button>
        </form>

        {/* Error */}
        {error && (
          <div className="error-box">
            <span>⚠️</span> {error}
          </div>
        )}

        {/* Results */}
        {results && (
          <div className="results">
            <h2 className="results-title">Your Notes are Ready! 🎉</h2>
            {results.map((r, i) => (
              <div key={i} className="result-card">
                <div className="result-header">
                  <span className="result-filename">{fileIcon(r.file)} {r.file}</span>
                  {r.pdf_url && (
                    <button
                      className="download-btn"
                      onClick={() => downloadPdf(r.pdf_url, r.file.replace(/\.[^.]+$/, '') + '_notes.pdf')}
                    >
                      ⬇ Download PDF
                    </button>
                  )}
                </div>
                {r.warning && <p className="result-warning">⚠️ {r.warning}</p>}
                {r.notes && (
                  <pre className="result-notes">{r.notes}</pre>
                )}
              </div>
            ))}
          </div>
        )}
      </main>

      <footer className="footer">
        Made with ❤️ by Aditya V &nbsp;·&nbsp; Powered by Sarvam AI
      </footer>
    </div>
  )
}

function fileIcon(name) {
  if (name.endsWith('.pdf')) return '📄'
  if (name.endsWith('.pptx') || name.endsWith('.ppt')) return '📊'
  if (name.match(/\.(png|jpg|jpeg)$/i)) return '🖼️'
  return '📁'
}
