import { useState, useCallback } from 'react';
import { DropZone } from './components/DropZone';
import { ProgressBar } from './components/ProgressBar';
import { ResultCard } from './components/ResultCard';
import type { ValidationResult, ValidateResponse, ValidationError } from './types';

const API_URL = import.meta.env.VITE_API_URL || '/api/validate';
const API_REPORT_URL = import.meta.env.VITE_API_REPORT_URL || '/api/validate/report';

export default function App() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ValidationResult | null>(null);
  const [error, setError] = useState<ValidationError | null>(null);

  const handleFileSelect = useCallback(async (selectedFile: File) => {
    setFile(selectedFile);
    setResult(null);
    setError(null);
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await fetch(API_URL, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({
          error: 'Error al conectar con el servidor',
          timestamp: new Date().toISOString(),
        }));
        setError(errData);
        return;
      }

      const data: ValidateResponse = await response.json();
      setResult(data.result);
    } catch (err) {
      setError({
        error: 'Error de conexion',
        detail: err instanceof Error ? err.message : 'No se pudo conectar con el servidor',
        timestamp: new Date().toISOString(),
      });
    } finally {
      setLoading(false);
    }
  }, []);

  const handleReset = useCallback(() => {
    setFile(null);
    setResult(null);
    setError(null);
  }, []);

  const handleDownloadReport = useCallback(async () => {
    if (!result || !file) return;

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(API_REPORT_URL, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        console.error('Error al generar reporte');
        return;
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `reporte_${result.filename.replace('.pdf', '')}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Error al descargar reporte:', err);
    }
  }, [result, file]);

  return (
    <div className="min-h-screen bg-safe-bg">
      <header className="border-b border-safe-border bg-safe-card/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <div>
              <h1 className="text-xl font-bold text-safe-text">SafePILA</h1>
              <p className="text-xs text-safe-muted">Validador de Seguridad Social</p>
            </div>
          </div>
          <span className="text-xs text-safe-muted bg-safe-border px-3 py-1 rounded-full">v0.1.0</span>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-12">
        {!loading && !result && !error && (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold text-safe-text mb-2">Validar Planilla</h2>
              <p className="text-safe-muted">
                Sube un PDF de seguridad social para verificar si ha sido alterado o editado.
              </p>
            </div>
            <DropZone onFileSelect={handleFileSelect} />
          </div>
        )}

        {loading && (
          <div className="space-y-6">
            {file && (
              <div className="card">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-safe-red/10 rounded-lg flex items-center justify-center">
                    <svg className="w-6 h-6 text-safe-red" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6zM6 20V4h7v5h5v11H6z" />
                    </svg>
                  </div>
                  <div>
                    <p className="font-medium text-safe-text">{file.name}</p>
                    <p className="text-sm text-safe-muted">
                      {(file.size / (1024 * 1024)).toFixed(2)} MB
                    </p>
                  </div>
                </div>
              </div>
            )}
            <ProgressBar />
          </div>
        )}

        {error && (
          <div className="space-y-6">
            <div className="card border-safe-red/30 bg-safe-red/5">
              <div className="flex flex-col items-center text-center p-6">
                <div className="w-16 h-16 bg-safe-red/10 rounded-full flex items-center justify-center mb-4">
                  <svg className="w-8 h-8 text-safe-red" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
                  </svg>
                </div>
                <h3 className="text-lg font-bold text-safe-red mb-2">{error.error}</h3>
                {error.detail && <p className="text-safe-muted">{error.detail}</p>}
              </div>
            </div>
            <button onClick={handleReset} className="btn-secondary w-full">
              Intentar de nuevo
            </button>
          </div>
        )}

        {result && !loading && (
          <ResultCard
            result={result}
            onReset={handleReset}
            onDownloadReport={handleDownloadReport}
          />
        )}
      </main>
    </div>
  );
}