import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Puerto 5173: es el que el backend tiene permitido en CORS por defecto.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
  },
})
