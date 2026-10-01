-- Esquema de las colas de la tienda.
--
-- Se ejecuta con CREATE ... IF NOT EXISTS, asi que es idempotente y se puede
-- correr en cada arranque.

CREATE TABLE IF NOT EXISTS usuarios (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre            TEXT    NOT NULL,
    tipo_tramite      INTEGER NOT NULL CHECK (tipo_tramite IN (0, 1, 2)),
    monto_transaccion REAL    NOT NULL CHECK (monto_transaccion >= 0),
    creado_en         TEXT    NOT NULL
);

-- Este indice ES la definicion de la cola: agrupa por tipo de tramite y, dentro
-- de cada tipo, ordena por id. Como el id es autoincremental, ese orden es
-- exactamente el orden de llegada.
CREATE INDEX IF NOT EXISTS ix_usuarios_cola ON usuarios (tipo_tramite, id);

-- Estado interno del algoritmo de rotacion. La posicion del ciclo es una fila
-- mas de la base de datos: por eso sobrevive a un reinicio del servidor, algo
-- que nooba una variable en memoria.
CREATE TABLE IF NOT EXISTS estado (
    clave TEXT    PRIMARY KEY,
    valor INTEGER NOT NULL
);

INSERT OR IGNORE INTO estado (clave, valor) VALUES ('posicion_ciclo', 0);