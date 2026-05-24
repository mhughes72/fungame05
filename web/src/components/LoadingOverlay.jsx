export default function LoadingOverlay({ message = 'PROCESSING...' }) {
  return (
    <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="text-center">
        <div className="text-amber-400 text-lg font-bold tracking-widest animate-pulse mb-2">
          {message}
        </div>
        <div className="text-slate-500 text-sm">Consulting the advisors...</div>
      </div>
    </div>
  )
}
