import { useRef, useState } from 'react'

export default function UploadCard({ onFileSelected, progress, isUploading }) {
  const [isDragging, setIsDragging] = useState(false)
  const inputRef = useRef(null)

  const handleFiles = (files) => {
    const file = files?.[0]
    if (file && file.name.toLowerCase().endsWith('.csv')) {
      onFileSelected(file)
    }
  }

  return (
    <div className="rounded-2xl border border-slate-700 bg-slate-900 p-6 shadow-xl">
      <h2 className="mb-2 text-xl font-semibold">Upload Active Directory Security Log CSV</h2>
      <p className="mb-4 text-sm text-slate-400">Only .csv files, max 20MB.</p>
      <div
        role="button"
        tabIndex={0}
        onClick={() => inputRef.current?.click()}
        onDrop={(e) => {
          e.preventDefault()
          setIsDragging(false)
          handleFiles(e.dataTransfer.files)
        }}
        onDragOver={(e) => {
          e.preventDefault()
          setIsDragging(true)
        }}
        onDragLeave={() => setIsDragging(false)}
        className={`cursor-pointer rounded-xl border-2 border-dashed p-10 text-center transition ${
          isDragging ? 'border-cyan-400 bg-slate-800' : 'border-slate-600 bg-slate-950'
        }`}
      >
        <p className="text-slate-300">Drag & drop CSV here, or click to browse</p>
        <input
          ref={inputRef}
          type="file"
          accept=".csv,text/csv"
          className="hidden"
          onChange={(e) => handleFiles(e.target.files)}
        />
      </div>

      {isUploading && (
        <div className="mt-4">
          <div className="mb-1 text-sm text-slate-300">Uploading: {progress}%</div>
          <div className="h-2 w-full rounded-full bg-slate-700">
            <div className="h-2 rounded-full bg-cyan-400" style={{ width: `${progress}%` }} />
          </div>
        </div>
      )}
    </div>
  )
}
