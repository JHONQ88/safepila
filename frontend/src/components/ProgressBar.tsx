import { useState, useEffect } from 'react';

interface ProgressBarProps {
  elapsedMs?: number;
}

export function ProgressBar({ elapsedMs = 0 }: ProgressBarProps) {
  const [elapsed, setElapsed] = useState(elapsedMs);

  useEffect(() => {
    const interval = setInterval(() => {
      setElapsed((prev) => prev + 1000);
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const seconds = Math.floor(elapsed / 1000);
  const isWakingUp = seconds < 30;
  const isLongWait = seconds >= 30;

  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-safe-text">
          {isWakingUp ? 'Activando servidor...' : 'Validando documento...'}
        </span>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
          <span className="text-sm text-safe-muted">{seconds}s</span>
        </div>
      </div>
      <div className="w-full h-2 bg-safe-border rounded-full overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-blue-500 to-blue-400 rounded-full transition-all duration-1000"
          style={{ width: isWakingUp ? '30%' : isLongWait ? '70%' : '50%' }}
        />
      </div>
      {isWakingUp && (
        <p className="text-xs text-safe-yellow mt-2">
          El servidor se activa tras inactividad (~30s). Solo la primera vez.
        </p>
      )}
      {isLongWait && (
        <p className="text-xs text-safe-muted mt-2">
          Servidor activo, procesando documento...
        </p>
      )}
      {!isWakingUp && !isLongWait && (
        <div className="flex justify-between mt-2">
          <span className="text-xs text-safe-muted">Capa 1: Metadatos</span>
          <span className="text-xs text-safe-muted">Capa 2: Fechas</span>
          <span className="text-xs text-safe-muted">Capa 3: Estructura</span>
          <span className="text-xs text-safe-muted">Capa 4: IA</span>
        </div>
      )}
    </div>
  );
}