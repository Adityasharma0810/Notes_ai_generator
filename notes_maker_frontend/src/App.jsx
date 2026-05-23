import { useState, useRef } from 'react'
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

const LANGUAGES = [
  { code: 'en', name: 'English', flag: '🇬🇧' },
  { code: 'hi', name: 'हिंदी', flag: '🇮🇳' },
  { code: 'bn', name: 'বাংলা', flag: '🇧🇩' },
  { code: 'gu', name: 'ગુજરાતી', flag: '🇮🇳' },
  { code: 'kn', name: 'ಕನ್ನಡ', flag: '🇮🇳' },
  { code: 'ml', name: 'മലയാളം', flag: '🇮🇳' },
  { code: 'mr', name: 'मराठी', flag: '🇮🇳' },
  { code: 'od', name: 'ଓଡ଼ିଆ', flag: '🇮🇳' },
  { code: 'pa', name: 'ਪੰਜਾਬੀ', flag: '🇮🇳' },
  { code: 'ta', name: 'தமிழ்', flag: '🇮🇳' },
  { code: 'te', name: 'తెలుగు', flag: '🇮🇳' },
]

// UI translations for each language
const UI_TEXT = {
  en: {
    title: 'Shantanu', online: 'Online',
    dropText: 'Drop your files here or', browse: 'browse',
    dropHint: 'Supports PDF, PPTX, PNG, JPG',
    addMore: '+ Add more',
    modeLabel: 'What type of notes do you want?',
    modes: [
      { value: 'detailed', label: 'Detailed Notes', desc: 'Full explanations, examples & definitions', emoji: '📖' },
      { value: 'important', label: 'MCQ Pointer Notes', desc: 'Bullet points for quick revision & MCQs', emoji: '🎯' },
      { value: 'mixed', label: 'Mixed', desc: 'Best of both — explanations + key points', emoji: '⚡' },
    ],
    langLabel: 'Notes Language',
    generateBtn: '✨ Generate Notes',
    generating: 'Generating notes...',
    readyTitle: 'Your Notes are Ready! 🎉',
    downloadPdf: '⬇ Download PDF',
    listenAudio: '🔊 Listen',
    noText: 'No text could be extracted from this file.',
    footer: 'Made with ❤️ by Aditya V · Powered by Groq & Sarvam AI',
  },
  hi: {
    title: 'शंतनु', online: 'ऑनलाइन',
    dropText: 'फ़ाइलें यहाँ छोड़ें या', browse: 'ब्राउज़ करें',
    dropHint: 'PDF, PPTX, PNG, JPG समर्थित',
    addMore: '+ और जोड़ें',
    modeLabel: 'आप किस प्रकार के नोट्स चाहते हैं?',
    modes: [
      { value: 'detailed', label: 'विस्तृत नोट्स', desc: 'पूर्ण व्याख्या, उदाहरण और परिभाषाएं', emoji: '📖' },
      { value: 'important', label: 'MCQ पॉइंटर नोट्स', desc: 'त्वरित पुनरीक्षण के लिए बुलेट पॉइंट', emoji: '🎯' },
      { value: 'mixed', label: 'मिश्रित', desc: 'दोनों का सर्वश्रेष्ठ', emoji: '⚡' },
    ],
    langLabel: 'नोट्स की भाषा',
    generateBtn: '✨ नोट्स बनाएं',
    generating: 'नोट्स बन रहे हैं...',
    readyTitle: 'आपके नोट्स तैयार हैं! 🎉',
    downloadPdf: '⬇ PDF डाउनलोड करें',
    listenAudio: '🔊 सुनें',
    noText: 'इस फ़ाइल से कोई टेक्स्ट नहीं निकाला जा सका।',
    footer: 'Aditya V द्वारा ❤️ के साथ बनाया गया · Groq & Sarvam AI द्वारा संचालित',
  },
  ta: {
    title: 'சாந்தனு', online: 'ஆன்லைன்',
    dropText: 'கோப்புகளை இங்கே இடுங்கள் அல்லது', browse: 'உலாவுங்கள்',
    dropHint: 'PDF, PPTX, PNG, JPG ஆதரிக்கப்படுகிறது',
    addMore: '+ மேலும் சேர்க்கவும்',
    modeLabel: 'எந்த வகை குறிப்புகள் வேண்டும்?',
    modes: [
      { value: 'detailed', label: 'விரிவான குறிப்புகள்', desc: 'முழு விளக்கங்கள், எடுத்துக்காட்டுகள்', emoji: '📖' },
      { value: 'important', label: 'MCQ குறிப்புகள்', desc: 'விரைவு திருத்தத்திற்கான புள்ளிகள்', emoji: '🎯' },
      { value: 'mixed', label: 'கலவை', desc: 'இரண்டின் சிறந்தது', emoji: '⚡' },
    ],
    langLabel: 'குறிப்புகளின் மொழி',
    generateBtn: '✨ குறிப்புகள் உருவாக்கு',
    generating: 'குறிப்புகள் உருவாகின்றன...',
    readyTitle: 'உங்கள் குறிப்புகள் தயார்! 🎉',
    downloadPdf: '⬇ PDF பதிவிறக்கம்',
    listenAudio: '🔊 கேளுங்கள்',
    noText: 'இந்த கோப்பிலிருந்து உரை பிரிக்க முடியவில்லை.',
    footer: 'Aditya V ❤️ · Groq & Sarvam AI',
  },
}

// Fallback to English for languages without full UI translation
function getUI(lang) {
  return UI_TEXT[lang] || UI_TEXT['en']
}

export default function App() {
  const [files, setFiles] = useState([])
  const [mode, setMode] = useState('detailed')
  const [language, setLanguage] = useState('en')
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)
  const [dragOver, setDragOver] = useState(false)
  const [quote] = useState(
    () => SHANTANU_QUOTES[Math.floor(Math.random() * SHANTANU_QUOTES.length)]
  )
  const audioRefs = useRef({})

  const ui = getUI(language)

  function handleFileChange(e) {
    setFiles(Array.from(e.target.files))
    setResults(null)
    setError(null)
  }

  function handleDrop(e) {
    e.preventDefault()
    setDragOver(false)
    setFiles(Array.from(e.dataTransfer.files))
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
    formData.append('language', language)

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
    const a = document.createElement('a')
    a.href = `${API_BASE}${pdfUrl}`
    a.download = filename
    a.click()
  }

  function playAudio(audioUrl, key) {
    const audio = audioRefs.current[key]
    if (audio) {
      audio.paused ? audio.play() : audio.pause()
    }
  }

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-inner">
          <div className="bot-avatar">🤖</div>
          <div className="bot-info">
            <h1 className="bot-name">{ui.title}</h1>
            <span className="bot-status">● {ui.online}</span>
          </div>
          {/* Language selector in header */}
          <div className="lang-selector-header">
            <select
              value={language}
              onChange={(e) => { setLanguage(e.target.value); setResults(null) }}
              className="lang-select"
              aria-label="Select language"
            >
              {LANGUAGES.map(l => (
                <option key={l.code} value={l.code}>{l.flag} {l.name}</option>
              ))}
            </select>
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
                <p className="drop-text">{ui.dropText} <span className="drop-link">{ui.browse}</span></p>
                <p className="drop-hint">{ui.dropHint}</p>
              </>
            ) : (
              <div className="file-list" onClick={(e) => e.stopPropagation()}>
                {files.map((f, i) => (
                  <div key={i} className="file-chip">
                    <span className="file-icon">{fileIcon(f.name)}</span>
                    <span className="file-name">{f.name}</span>
                    <button type="button" className="file-remove" onClick={() => removeFile(i)}>×</button>
                  </div>
                ))}
                <button type="button" className="add-more"
                  onClick={() => document.getElementById('file-input').click()}>
                  {ui.addMore}
                </button>
              </div>
            )}
          </div>

          {/* Mode selector */}
          <div className="mode-section">
            <p className="mode-label">{ui.modeLabel}</p>
            <div className="mode-cards">
              {ui.modes.map((m) => (
                <label key={m.value} className={`mode-card ${mode === m.value ? 'selected' : ''}`}>
                  <input type="radio" name="mode" value={m.value}
                    checked={mode === m.value} onChange={() => setMode(m.value)} />
                  <span className="mode-emoji">{m.emoji}</span>
                  <span className="mode-title">{m.label}</span>
                  <span className="mode-desc">{m.desc}</span>
                </label>
              ))}
            </div>
          </div>

          <button type="submit" className="submit-btn" disabled={loading || files.length === 0}>
            {loading ? <><span className="spinner" /> {ui.generating}</> : ui.generateBtn}
          </button>
        </form>

        {error && <div className="error-box"><span>⚠️</span> {error}</div>}

        {results && (
          <div className="results">
            <h2 className="results-title">{ui.readyTitle}</h2>
            {results.map((r, i) => (
              <div key={i} className="result-card">
                <div className="result-header">
                  <span className="result-filename">{fileIcon(r.file)} {r.file}</span>
                  <div className="result-actions">
                    {r.pdf_url && (
                      <button className="download-btn"
                        onClick={() => downloadPdf(r.pdf_url, r.file.replace(/\.[^.]+$/, '') + '_notes.pdf')}>
                        {ui.downloadPdf}
                      </button>
                    )}
                    {r.audio_url && (
                      <>
                        <button className="audio-btn" onClick={() => playAudio(r.audio_url, i)}>
                          {ui.listenAudio}
                        </button>
                        <audio
                          ref={(el) => { audioRefs.current[i] = el }}
                          src={`${API_BASE}${r.audio_url}`}
                          style={{ display: 'none' }}
                        />
                      </>
                    )}
                  </div>
                </div>
                {r.warning && <p className="result-warning">⚠️ {r.warning}</p>}
                {r.notes && <pre className="result-notes">{r.notes}</pre>}
              </div>
            ))}
          </div>
        )}
      </main>

      <footer className="footer">{ui.footer}</footer>
    </div>
  )
}

function fileIcon(name) {
  if (name.endsWith('.pdf')) return '📄'
  if (name.endsWith('.pptx') || name.endsWith('.ppt')) return '📊'
  if (name.match(/\.(png|jpg|jpeg)$/i)) return '🖼️'
  return '📁'
}
