import type { Flag, Severity } from '../types';

interface FlagsModalProps {
  isOpen: boolean;
  onClose: () => void;
  flags: Flag[];
  filename: string;
}

const SEVERITY_CONFIG: Record<Severity, { label: string; color: string; bg: string }> = {
  HIGH: { label: 'ALTO', color: 'text-safe-red', bg: 'bg-safe-red/10' },
  MEDIUM: { label: 'MEDIO', color: 'text-safe-yellow', bg: 'bg-safe-yellow/10' },
  LOW: { label: 'BAJO', color: 'text-safe-muted', bg: 'bg-safe-muted/10' },
};

const LAYER_LABELS: Record<string, string> = {
  metadata: 'Metadatos',
  dates: 'Fechas',
  structure: 'Estructura',
  ai: 'Inteligencia Artificial',
};

export function FlagsModal({ isOpen, onClose, flags, filename }: FlagsModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="fixed inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />

      <div className="relative bg-safe-card border border-safe-border rounded-2xl w-full max-w-2xl max-h-[80vh] mx-4 overflow-hidden">
        <div className="flex items-center justify-between p-6 border-b border-safe-border">
          <div>
            <h2 className="text-xl font-bold text-safe-text">Evidencia de Alteración</h2>
            <p className="text-sm text-safe-muted mt-1">{filename}</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-safe-border rounded-lg transition-colors"
          >
            <svg className="w-5 h-5 text-safe-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="p-6 overflow-y-auto max-h-[60vh] space-y-4">
          {flags.length === 0 ? (
            <p className="text-center text-safe-muted py-8">No se encontraron hallazgos.</p>
          ) : (
            flags.map((flag, i) => {
              const sev = SEVERITY_CONFIG[flag.severity];
              return (
                <div
                  key={i}
                  className={`${sev.bg} border border-safe-border rounded-xl p-4`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-xs font-semibold text-safe-muted uppercase">
                          {LAYER_LABELS[flag.layer] ?? flag.layer}
                        </span>
                        <span className={`text-xs font-bold ${sev.color} px-2 py-0.5 rounded-full ${sev.bg}`}>
                          {sev.label}
                        </span>
                        <span className="text-xs text-safe-muted">Peso: {flag.weight}</span>
                      </div>
                      <p className="text-safe-text">{flag.finding}</p>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>

        <div className="p-6 border-t border-safe-border">
          <button onClick={onClose} className="btn-primary w-full">
            Cerrar
          </button>
        </div>
      </div>
    </div>
  );
}