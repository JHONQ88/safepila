import { useState } from 'react';
import type { ValidationResult } from '../types';
import { FlagsModal } from './FlagsModal';

interface ResultCardProps {
  result: ValidationResult;
  onReset: () => void;
  onDownloadReport: () => void;
}

const SEMAPHORE_CONFIG = {
  GREEN: {
    bg: 'bg-safe-green/10',
    border: 'border-safe-green',
    text: 'text-safe-green',
    label: 'APROBADO',
    icon: (
      <svg className="w-16 h-16" fill="currentColor" viewBox="0 0 24 24">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
      </svg>
    ),
  },
  YELLOW: {
    bg: 'bg-safe-yellow/10',
    border: 'border-safe-yellow',
    text: 'text-safe-yellow',
    label: 'SOSPECHOSO',
    icon: (
      <svg className="w-16 h-16" fill="currentColor" viewBox="0 0 24 24">
        <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z" />
      </svg>
    ),
  },
  RED: {
    bg: 'bg-safe-red/10',
    border: 'border-safe-red',
    text: 'text-safe-red',
    label: 'RECHAZADO',
    icon: (
      <svg className="w-16 h-16" fill="currentColor" viewBox="0 0 24 24">
        <path d="M12 2C6.47 2 2 6.47 2 12s4.47 10 10 10 10-4.47 10-10S17.53 2 12 2zm5 13.59L15.59 17 12 13.41 8.41 17 7 15.59 10.59 12 7 8.41 8.41 7 12 10.59 15.59 7 17 8.41 13.41 12 17 15.59z" />
      </svg>
    ),
  },
};

export function ResultCard({ result, onReset, onDownloadReport }: ResultCardProps) {
  const [showFlags, setShowFlags] = useState(false);
  const config = SEMAPHORE_CONFIG[result.semaphore];

  return (
    <>
      <div className="w-full max-w-2xl mx-auto space-y-6">
        <div className={`card ${config.bg} ${config.border} border-2`}>
          <div className="flex flex-col items-center text-center p-8">
            <div className={`${config.text} mb-4`}>{config.icon}</div>

            <h2 className={`text-3xl font-bold ${config.text} mb-2`}>{config.label}</h2>

            <div className="flex items-center gap-3 mb-4">
              <span className="text-sm text-safe-muted">Score:</span>
              <span className={`text-2xl font-bold ${config.text}`}>{result.score}</span>
              <span className="text-sm text-safe-muted">/ 100</span>
            </div>

            <p className="text-safe-text text-base leading-relaxed max-w-lg">
              {result.verdict}
            </p>
          </div>
        </div>

        <div className="card space-y-4">
          <h3 className="font-semibold text-safe-text">Detalles del documento</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-safe-muted">Archivo:</span>
              <span className="ml-2 text-safe-text">{result.filename}</span>
            </div>
            <div>
              <span className="text-safe-muted">Páginas:</span>
              <span className="ml-2 text-safe-text">{result.details.pages ?? 'N/A'}</span>
            </div>
            <div>
              <span className="text-safe-muted">Producer:</span>
              <span className="ml-2 text-safe-text">{result.details.producer ?? 'N/A'}</span>
            </div>
            <div>
              <span className="text-safe-muted">Fuentes:</span>
              <span className="ml-2 text-safe-text">{result.details.fonts.length}</span>
            </div>
          </div>

          {result.flags.length > 0 && (
            <button
              onClick={() => setShowFlags(true)}
              className="btn-secondary w-full flex items-center justify-center gap-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              Ver Huellas ({result.flags.length} hallazgos)
            </button>
          )}
        </div>

        <div className="flex gap-3">
          <button onClick={onReset} className="btn-secondary flex-1">
            Validar otro PDF
          </button>
          <button onClick={onDownloadReport} className="btn-primary flex-1">
            Descargar Reporte
          </button>
        </div>
      </div>

      <FlagsModal
        isOpen={showFlags}
        onClose={() => setShowFlags(false)}
        flags={result.flags}
        filename={result.filename}
      />
    </>
  );
}