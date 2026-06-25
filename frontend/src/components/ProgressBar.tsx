export function ProgressBar() {
  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-safe-text">Validando documento...</span>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
          <span className="text-sm text-safe-muted">Analizando</span>
        </div>
      </div>
      <div className="w-full h-2 bg-safe-border rounded-full overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-blue-500 to-blue-400 rounded-full animate-progress"
          style={{ width: '60%' }}
        />
      </div>
      <div className="flex justify-between mt-2">
        <span className="text-xs text-safe-muted">Capa 1: Metadatos</span>
        <span className="text-xs text-safe-muted">Capa 2: Fechas</span>
        <span className="text-xs text-safe-muted">Capa 3: Estructura</span>
        <span className="text-xs text-safe-muted">Capa 4: IA</span>
      </div>
    </div>
  );
}