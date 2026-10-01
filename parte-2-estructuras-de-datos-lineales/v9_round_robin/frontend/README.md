# Ejecutar el frontend

## 1. Instalar dependencias

Una sola vez, desde la carpeta `frontend`:

```bash
cd parte-2-estructuras-de-datos-lineales/v9_round_robin/frontend
npm install
```

## 2. Levantar el backend

El frontend necesita la API. En **otra terminal**, desde `v9_round_robin`:

```bash
cd parte-2-estructuras-de-datos-lineales/v9_round_robin
source .venv/bin/activate
python main.py
```

## 3. Levantar el frontend

Desde la carpeta `frontend`:

```bash
npm run dev
```

## 4. Abrir la aplicación

En el navegador: **<http://localhost:5173>**

---

## Notas

- El frontend corre en el puerto **5173** y el backend en el **8000**. Esos dos
  puertos ya están permitidos en la configuración de CORS del backend.
- Cada terminal nueva necesita volver a activarse:
  `source .venv/bin/activate` (backend) o `cd frontend` (frontend).

## Si no abre

**`Address already in use`** → el puerto ya está ocupado. Para ver qué lo ocupa y
liberarlo:

```bash
lsof -nP -iTCP:8000 -sTCP:LISTEN
kill <PID>
```

O cambia el puerto del backend: `python main.py 8001`. Si haces eso, avisa al
frontend editando la primera línea de `src/api.js`:

```js
const BASE = 'http://localhost:8001/api/v1'
```

## Detener

`Ctrl + C` en cada terminal.
