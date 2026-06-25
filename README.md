# SafePILA - Validador de Seguridad Social

Validador inteligente de planillas de seguridad social en formato PDF.

## Stack

- **Backend**: FastAPI + Python 3.11
- **PDF Engine**: pdfplumber + pikepdf
- **Frontend**: React + Vite + Tailwind CSS

## Deploy Online (Railway + Vercel)

### Paso 1: Subir Backend a Railway

1. Crear cuenta en [railway.app](https://railway.app)
2. Click en **"New Project"** > **"Deploy from GitHub repo"**
3. Subir la carpeta `backend/` a un repositorio de GitHub
4. En Railway, configurar:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -e .`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Variables de entorno en Railway:
   ```
   DEBUG=false
   PYTHON_VERSION=3.11.8
   ```
6. Copiar la URL generada (ej: `https://safepila-backend.up.railway.app`)

### Paso 2: Subir Frontend a Vercel

1. Crear cuenta en [vercel.com](https://vercel.com)
2. Subir la carpeta `frontend/` a un repositorio de GitHub
3. En Vercel, click **"New Project"** > importar el repo
4. Configurar:
   - **Framework**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Variable de entorno en Vercel:
   ```
   VITE_API_URL=https://safepila-backend.up.railway.app
   VITE_API_REPORT_URL=https://safepila-backend.up.railway.app
   ```
6. Deploy

### Paso 3: Compartir

La URL de Vercel es pública. Compártela para que cualquiera pueda probar:
```
https://tu-proyecto.vercel.app
```

## Desarrollo Local

**Backend:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

## Uso

1. Arrastra un PDF de planilla de seguridad social
2. El sistema valida automáticamente (4 capas)
3. Recibe resultado con semáforo (🟢/🟡/🔴)
4. Descarga el reporte en PDF profesional

## Tests

```bash
cd backend
pytest
```