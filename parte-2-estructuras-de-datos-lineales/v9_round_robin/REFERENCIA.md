# Referencia técnica

Documentación de la API y del diseño. Para **cómo ejecutarlo**, empieza por
[README.md](README.md).

## Qué resuelve

Resuelve el problema de **inanición (starvation)** que quedó anotado en la
versión de consola `v8_colas/v82_colas_con_prioridad/`, y lo expone como API
HTTP documentada en Swagger, lista para que se le conecte un frontend.

`v82` atendía por **prioridad estricta**: primero quien venga a pagar deudas,
luego las compras de contado, y los créditos al final. Si nunca paran de llegar
pagos de deudas, **los que piden crédito esperan para siempre**.

Esta versión rota los turnos con **Round Robin ponderado**, usando los mismos
parámetros del comentario de `v82`:

| `tipo_tramite` | Trámite                  | Peso |
|----------------|--------------------------|------|
| `0`            | Pago de deudas           | 3    |
| `1`            | Compra de contado        | 2    |
| `2`            | Solicitud de crédito     | 1    |

Los pesos producen el ciclo de turnos:

```
(deudas, deudas, deudas, contado, contado, crédito)
```

**Consecuencia: ningún usuario espera más de 6 turnos.** Ese es el invariante,
y hay un test que lo verifica exhaustivamente
(`tests/unit/test_politica_round_robin.py::test_no_hay_inanicion_en_ninguna_combinacion_posible`).

### Las dos variantes son el mismo código

| Variante | Pesos | Ciclo | Espera máxima |
|----------|-------|-------|---------------|
| Round Robin puro      | `1,1,1` | `(deudas, contado, crédito)`        | 3 turnos |
| Round Robin ponderado | `3,2,1` | `(deudas,deudas,deudas,contado,contado,crédito)` | 6 turnos |

La ponderación no es un caso especial: es el algoritmo general, y el Round
Robin puro sale cambiando una constante (`ROUND_ROBIN_PESOS=1,1,1`).

Detalle importante: los turnos se **intercalan** dentro del ciclo. Agruparlos
(`3 deudas` seguidas, luego `2 de contado`, luego `1 de crédito`) reintroduciría
la inanición en las colas del final.

## Endpoints

Todos bajo `/api/v1`.

| Método | Ruta | Qué hace |
|--------|------|----------|
| `GET`  | `/health` | Estado del servidor y de la política |
| `POST` | `/colas/usuarios` | Registra un usuario en la cola de su trámite |
| `POST` | `/colas/atender` | **Ejecuta** el siguiente turno. Saca al usuario de la cola |
| `GET`  | `/colas/siguiente` | Consulta quién sigue, **sin** sacarlo (peek) |
| `GET`  | `/colas` | Estado completo: las tres colas, totales y ciclo |
| `GET`  | `/colas/configuracion` | Política, pesos, ciclo y posición actual |
| `DELETE` | `/colas/usuarios/{id}` | Retira a un usuario de su cola |
| `POST` | `/colas/reiniciar` | Vacía las colas y reinicia el ciclo |

La separación entre `POST /atender` y `GET /siguiente` es deliberada: es la
versión web de la operación "Consultar" del `definiciones.md` de las colas. El
frontend puede mostrar "tú sigues" sin sacar a nadie de la cola.

Códigos de error relevantes:

| Situación | Código | `codigo` en el cuerpo |
|-----------|--------|----------------------|
| Cola vacía al atender o consultar | `409` | `ColaVaciaError` |
| Id de usuario inexistente | `404` | `UsuarioNoEncontradoError` |
| Datos inválidos | `422` | (validación de Pydantic) |

## Arquitectura (Clean Architecture)

Las dependencias apuntan hacia adentro. `domain` no importa nada de las demás
capas; eso se puede comprobar con `import-linter` si se quiere.

```
src/round_robin/
├── domain/            ← puro: sin FastAPI, sin Pydantic, sin SQL
│   ├── enums.py             TipoTramite (IntEnum 0,1,2)
│   ├── entities.py          Usuario, UsuarioRegistrado
│   ├── exceptions.py        Errores de negocio
│   ├── plan/
│   │   ├── planificador.py  ABC de las políticas + Turno
│   │   └── round_robin.py   PoliticaRoundRobin (pura, sin estado)
│   └── ports/
│       └── cola_turnos.py   ColaTurnosPort (la interfaz del almacén)
│
├── application/       ← casos de uso: orquestan, no calculan
│   ├── dtos.py
│   └── use_cases/          RegistrarUsuarioEnCola, AtenderSiguienteUsuario, ...
│
├── infrastructure/    ← adaptadores externos
│   ├── config.py            Configuración desde variables de entorno
│   └── persistence/
│       ├── en_memoria.py        deque + threading.Lock (para tests)
│       └── sqlite/              ← la implementación real
│           ├── esquema.sql
│           ├── conexion.py
│           └── cola_turnos_sqlite.py
│
└── presentation/      ← HTTP
    ├── app.py                App factory, CORS, lifespan
    ├── dependencies.py       Punto de composición (qué implementación se usa)
    ├── errors.py             Excepción de dominio → código HTTP
    ├── schemas.py            Modelos Pydantic (el único lugar con Pydantic)
    └── routers/colas.py
```

### La política no tiene estado

`PoliticaRoundRobin.planear(tipos_ocupados, posicion_actual)` es una **función
pura**: le das qué colas tienen gente y dónde está el ciclo, te devuelve el
turno. No guarda nada. La posición del ciclo vive en el almacén, detrás del
puerto.

Por eso se puede probar de forma exhaustiva sin montar nada, y por eso el
mismo código sirve para el Round Robin puro y el ponderado.

### Por qué el turno se decide dentro del repositorio

`ColaTurnosPort.avanzar_turno(planificador)` recibe la política en vez de que
el caso de uso componga los pasos. La razón es la **atomicidad**:

```
leer posición → calcular turno → borrar usuario → guardar posición nueva
```

Si el caso de uso hiciera `planear()` y después `sacar()`, dos peticiones
simultáneas podrían calcular el mismo turno y atender dos veces al mismo
usuario. Solo quien tiene el estado puede garantizar que eso no pase, así que
la transacción vive en el adaptador. La política sigue siendo pura: no sabe
que existe una base de datos.

## Persistencia: SQLite

Archivo local, sin servidor. Elegido por tres razones:

**1. Atomicidad entre procesos.** `BEGIN IMMEDIATE` toma el cerrojo de escritura
al inicio de la transacción. Es el equivalente multi-proceso del
`threading.Lock` del repositorio en memoria, y funciona aunque corran varios
workers de uvicorn. Un `threading.Lock` ya no alcanza en ese escenario, porque
cada proceso tiene el suyo.

**2. La posición del ciclo sobrevive.** Es una fila en la tabla `estado`, no
una variable en memoria. Si se reinicia el servidor, el ciclo se reanuda donde
iba.

**3. Retirar por id es barato.** Con un `deque` había que recorrerlo entero
(O(n)); con clave primaria es un `DELETE`. Ese fue el compromiso que se evitó
al elegir un almacén relacional.

Detalles de configuración:

- **Conexión por operación**, no una global: FastAPI ejecuta los endpoints
  síncronos en un grupo de hilos y un objeto `sqlite3.Connection` no se puede
  compartir entre ellos.
- **`PRAGMA journal_mode=WAL`** para que las lecturas no bloqueen a la
  escritura, y **`busy_timeout=5000`** para que un worker espere su turno en
  vez de fallar.
- El índice `(tipo_tramite, id)` **es** la definición de la cola: agrupa por
  tipo y ordena por orden de llegada.
- Los `CHECK` del esquema son la segunda línea de defensa: la base rechaza un
  `tipo_tramite = 9` o un monto negativo, el bug que `v82` ignoraba en silencio.

### El repositorio en memoria sigue en el repo

`infrastructure/persistence/en_memoria.py` se conserva por dos razones: los
tests de los casos de uso corren al instante sin tocar disco, y demuestra que
el puerto es realmente intercambiable (misma interfaz, dos almacenes).

Sus limitaciones son las que justifican SQLite: el lock solo protege dentro de
un proceso, nada sobrevive a un reinicio, y `retirar` es O(n).

## Pruebas

```
tests/
├── unit/          política pura (exhaustiva) y casos de uso
├── persistence/   SQLite y en memoria con los MISMOS tests
└── api/           TestClient: contrato HTTP, errores, Swagger
```

El fixture `colas` corre cada prueba de persistencia contra **los dos
adaptadores**. Es la comprobación práctica de que el puerto funciona.

## Migrar a PostgreSQL

Cuando el backend se despliegue en un servidor y la base necesite estar en otra
máquina, o simplemente si quieres más concurrentes:

1. Escribir `infrastructure/persistence/postgres/cola_turnos_postgres.py`
   implementando `ColaTurnosPort`.
2. Cambiar `BEGIN IMMEDIATE` por `SELECT ... FOR UPDATE`, y el
   `DELETE ... LIMIT 1` por su equivalente con `ORDER BY id`.
3. Cambiar la línea que lo instancia en `presentation/dependencies.py`.

**No se toca el dominio, ni los casos de uso, ni los routers, ni el contrato
OpenAPI.** Ese es el resultado concreto de haber dibujado el puerto bien.

## Notas de implementación

- **Por qué no `heapq`.** La cola de prioridad estándar saca por clave, no por
  llegada, y eso rompe el FIFO dentro de cada nivel: se atendería primero al
  de deuda más antigua, pero entre dos del mismo tipo se perdería el orden de
  llegada. La rotación sobre `deque` conserva ambas cosas.
- **Dos clases para `avanzar` y `inspeccionar`.** Si compartieran el avance del
  ciclo, cada consulta HTTP le robaría un turno al usuario.
- **Pesos configurables solo por entorno.** El `PUT` de pesos quedó fuera; hoy se
  cambia con `ROUND_ROBIN_PESOS`. La posición del ciclo ya se normaliza contra
  el largo del ciclo, así que cambiarla a posteriori es seguro.
- **Sin autenticación.** Los endpoints son de administración interna. Si se
  exponen fuera de la red local, hace falta añadir auth antes.