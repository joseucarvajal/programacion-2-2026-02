import { useCallback, useEffect, useState } from 'react'
import { api } from './api.js'

const TIPOS = [
  { valor: 0, nombre: 'Pago de deudas', peso: 3 },
  { valor: 1, nombre: 'Compra de contado', peso: 2 },
  { valor: 2, nombre: 'Solicitud de crédito', peso: 1 },
]

export default function App() {
  const [estado, setEstado] = useState(null)
  const [siguiente, setSiguiente] = useState(null)
  const [config, setConfig] = useState(null)
  const [nombre, setNombre] = useState('')
  const [tipo, setTipo] = useState(0)
  const [monto, setMonto] = useState('')
  const [error, setError] = useState('')
  const [ultimo, setUltimo] = useState(null)

  const refrescar = useCallback(async () => {
    try {
      setEstado(await api.estado())
      setConfig(await api.configuracion())
      // The "next" endpoint answers 409 when there is nobody in line.
      setSiguiente(await api.siguiente().catch(() => null))
      setError('')
    } catch (e) {
      setError(`No se pudo conectar con la API: ${e.message}`)
    }
  }, [])

  useEffect(() => {
    refrescar()
    const id = setInterval(refrescar, 2000)
    return () => clearInterval(id)
  }, [refrescar])

  async function registrar(evento) {
    evento.preventDefault()
    try {
      const usuario = await api.registrar(nombre, tipo, Number(monto) || 0)
      setNombre('')
      setMonto('')
      setUltimo({ ok: true, texto: `${usuario.nombre} entró a la cola` })
      refrescar()
    } catch (e) {
      setUltimo({ ok: false, texto: e.message })
    }
  }

  async function atender() {
    try {
      const turno = await api.atender()
      setUltimo({ ok: true, texto: `Atendido: ${turno.usuario.nombre}` })
      refrescar()
    } catch (e) {
      setUltimo({ ok: false, texto: e.message })
    }
  }

  async function reiniciar() {
    await api.reiniciar()
    setUltimo({ ok: true, texto: 'Colas vaciadas' })
    refrescar()
  }

  return (
    <main className="contenedor">
      <header>
        <h1>Colas de la tienda</h1>
        <p className="subtitulo">
          Rotación <strong>Round Robin</strong>
          {config && ` · pesos ${config.pesos.map((p) => p.peso).join(' / ')}`}
          {config && ` · espera máxima ${config.espera_maxima_turnos} turnos`}
        </p>
      </header>

      {error && <div className="alerta error">{error}</div>}

      <section className="tarjetas">
        <div className="tarjeta destaque">
          <h2>Le sigue el turno a</h2>
          {siguiente ? (
            <>
              <p className="nombre">{siguiente.usuario.nombre}</p>
              <p className="detalle">{siguiente.tipo_tramite_descripcion}</p>
              <p className="detalle">#{siguiente.usuario.id}</p>
            </>
          ) : (
            <p className="detalle">No hay nadie en cola</p>
          )}
          <button onClick={atender} disabled={!siguiente}>
            Atender
          </button>
        </div>

        <form className="tarjeta" onSubmit={registrar}>
          <h2>Registrar usuario</h2>
          <input
            value={nombre}
            onChange={(e) => setNombre(e.target.value)}
            placeholder="Nombre"
            required
          />
          <select value={tipo} onChange={(e) => setTipo(Number(e.target.value))}>
            {TIPOS.map((t) => (
              <option key={t.valor} value={t.valor}>
                {t.nombre} (peso {t.peso})
              </option>
            ))}
          </select>
          <input
            type="number"
            min="0"
            step="1000"
            value={monto}
            onChange={(e) => setMonto(e.target.value)}
            placeholder="Monto"
          />
          <button type="submit">Encolar</button>
        </form>
      </section>

      {ultimo && (
        <div className={`alerta ${ultimo.ok ? 'ok' : 'error'}`}>{ultimo.texto}</div>
      )}

      {estado && (
        <>
          <p className="resumen">
            <strong>{estado.total_usuarios}</strong> en cola · ciclo en posición{' '}
            <strong>{estado.posicion_ciclo}</strong> de {estado.longitud_ciclo}
          </p>

          <section className="colas">
            {estado.colas.map((cola) => (
              <div className="cola" key={cola.tipo_tramite}>
                <h3>
                  {cola.tipo_tramite_descripcion}{' '}
                  <span className="peso">peso {cola.peso}</span>
                </h3>
                <p className="detalle">
                  {cola.total} personas · ${cola.monto_total.toLocaleString('es-CO')}
                </p>
                <ol>
                  {cola.usuarios.map((u) => (
                    <li key={u.id}>
                      {u.nombre} <span className="id">#{u.id}</span>
                    </li>
                  ))}
                  {cola.total === 0 && <li className="vacia">vacía</li>}
                </ol>
              </div>
            ))}
          </section>

          {config && (
            <p className="ciclo">
              Ciclo: {config.ciclo_legible.join(' → ')} → (repite)
            </p>
          )}

          <button className="peligro" onClick={reiniciar}>
            Reiniciar colas
          </button>
        </>
      )}
    </main>
  )
}
