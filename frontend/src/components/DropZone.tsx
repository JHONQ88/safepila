import { useCallback, useState, useRef } from 'react';

interface DropZoneProps {
  onFileSelect: (file: File) => void;
  disabled?: boolean;
  isLoading?: boolean;
}

const MAX_SIZE_MB = 25;
const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024;

export function DropZone({ onFileSelect, disabled, isLoading }: DropZoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const validateFile = useCallback((file: File): boolean => {
    setError(null);

    if (file.type !== 'application/pdf') {
      setError('Solo se permiten archivos PDF.');
      return false;
    }

    if (file.size > MAX_SIZE_BYTES) {
      setError(`El archivo supera ${MAX_SIZE_MB}MB. Tamaño actual: ${(file.size / (1024 * 1024)).toFixed(1)}MB.`);
      return false;
    }

    if (file.size === 0) {
      setError('El archivo está vacío.');
      return false;
    }

    return true;
  }, []);

  const handleFile = useCallback((file: File) => {
    if (validateFile(file)) {
      onFileSelect(file);
    }
  }, [validateFile, onFileSelect]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    if (disabled || isLoading) return;

    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  }, [disabled, isLoading, handleFile]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    if (!disabled && !isLoading) setIsDragging(true);
  }, [disabled, isLoading]);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleClick = useCallback(() => {
    if (!disabled && !isLoading) {
      inputRef.current?.click();
    }
  }, [disabled, isLoading]);

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
    e.target.value = '';
  }, [handleFile]);

  return (
    <div className="w-full">
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={handleClick}
        className={`
          relative border-2 border-dashed rounded-xl p-12 text-center cursor-pointer
          transition-all duration-200
          ${isDragging
            ? 'border-blue-500 bg-blue-500/10'
            : 'border-safe-border hover:border-safe-muted'
          }
          ${disabled || isLoading ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,application/pdf"
          onChange={handleChange}
          className="hidden"
          disabled={disabled || isLoading}
        />

        <div className="flex flex-col items-center gap-4">
          <div className={`
            w-16 h-16 rounded-full flex items-center justify-center
            ${isDragging ? 'bg-blue-500/20' : 'bg-safe-card'}
          `}>
            <svg
              className={`w-8 h-8 ${isDragging ? 'text-blue-400' : 'text-safe-muted'}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>
          </div>

          <div>
            <p className="text-lg font-semibold text-safe-text">
              Arrastra tu planilla de seguridad social
            </p>
            <p className="text-sm text-safe-muted mt-1">
              o haz clic para seleccionar un archivo PDF (max {MAX_SIZE_MB}MB)
            </p>
          </div>
        </div>
      </div>

      {error && (
        <div className="mt-3 p-3 bg-safe-red/10 border border-safe-red/30 rounded-lg">
          <p className="text-sm text-safe-red">{error}</p>
        </div>
      )}
    </div>
  );
}