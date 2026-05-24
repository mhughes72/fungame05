import { useEffect } from 'react'

/**
 * Reusable modal overlay.
 * Closes on Escape or clicking the backdrop.
 */
export default function Modal({ title, onClose, children, wide = false }) {
  useEffect(() => {
    function onKey(e) { if (e.key === 'Escape') onClose() }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [onClose])

  return (
    <div
      className="fixed inset-0 bg-slate-950/90 backdrop-blur-sm flex items-start justify-center z-50 p-4 overflow-y-auto"
      onClick={onClose}
    >
      <div
        className={`bg-slate-900 border border-slate-700 w-full mt-12 mb-12 ${wide ? 'max-w-3xl' : 'max-w-2xl'}`}
        onClick={e => e.stopPropagation()}
      >
        {/* Sticky header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-700 sticky top-0 bg-slate-900 z-10">
          <div className="text-amber-400 text-xs uppercase tracking-widest font-bold">{title}</div>
          <button
            onClick={onClose}
            className="text-slate-500 hover:text-slate-200 text-lg leading-none transition-colors"
            aria-label="Close"
          >
            ✕
          </button>
        </div>
        <div className="px-6 py-6">
          {children}
        </div>
      </div>
    </div>
  )
}
