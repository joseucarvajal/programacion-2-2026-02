// Talking to the backend. All the endpoints live under /api/v1.
const BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1'

async function pedir(ruta, opciones = {}) {
  const respuesta = await fetch(`${BASE}${ruta}`, {
    headers: { 'Content-Type': 'application/json' },
    ...opciones,
  })

  if (!respuesta.ok) {
    // The backend answers with { detail, codigo }; show what it says.
    const cuerpo = await respuesta.json().catch(() => ({}))
    throw new Error(cuerpo.detail ?? `Error ${respuesta.status}`)
  }

  return respuesta.status === 204 ? null : respuesta.json()
}

export const api = {
  registrar: (nombre, tipoTramite, monto) =>
    pedir('/colas/usuarios', {
      method: 'POST',
      body: JSON.stringify({ nombre, tipo_tramite: tipoTramite, monto_transaccion: monto }),
    }),

  estado: () => pedir('/colas'),
  siguiente: () => pedir('/colas/siguiente'),
  atender: () => pedir('/colas/atender', { method: 'POST' }),
  reiniciar: () => pedir('/colas/reiniciar', { method: 'POST' }),
  configuracion: () => pedir('/colas/configuracion'),
}
