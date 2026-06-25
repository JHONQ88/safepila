# Guia de Deploy - SafePILA

## Paso 1: Subir codigo a GitHub

1. Crear un repositorio en GitHub llamado `safepila`
2. Subir toda la carpeta del proyecto

## Paso 2: Deploy Backend en Render (GRATIS)

1. Ir a [render.com](https://render.com) y crear cuenta
2. Click **"New +"** → **"Web Service"**
3. Conectar el repositorio de GitHub
4. Configurar:
   - **Name**: `safepila-backend`
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -e .`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Click **"Create Web Service"**
6. Esperar a que termine el deploy (2-3 minutos)
7. **Copiar la URL** que genera (ej: `https://safepila-backend.onrender.com`)

## Paso 3: Deploy Frontend en Vercel (GRATIS)

1. Ir a [vercel.com](https://vercel.com) y crear cuenta
2. Click **"Add New..."** → **"Project"**
3. Conectar el repositorio de GitHub
4. Configurar:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Agregar Variable de Entorno:
   - **Name**: `VITE_API_URL`
   - **Value**: `https://safepila-backend.onrender.com` (la URL del paso 2)
6. Click **"Deploy"**
7. Esperar 1-2 minutos

## Paso 4: Probar

1. Abrir la URL de Vercel (ej: `https://safepila.vercel.app`)
2. Subir un PDF de prueba
3. Verificar que funciona

## Paso 5: Compartir

Copiar la URL de Vercel y compartirla con quien quiera probar.

---

## Solucion de problemas

### Si el frontend no conecta al backend:
1. Verificar que la variable `VITE_API_URL` esta configurada en Vercel
2. Verificar que el backend esta corriendo en Render (puede tardar 30s en despertar)

### Si el backend tarda en responder:
Render gratuita duerme el servicio despues de 15 min de inactividad. La primera request puede tomar 30-60 segundos.