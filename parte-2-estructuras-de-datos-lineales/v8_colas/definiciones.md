# Colas (FIFO : First In First Out)

Sirven para muchos procesos en la vida real, ejemplos:
- La cola de un banco (la primera persona en llegar es la primera persona en ser atendida, la segunda persona en llegar será la segunda persona en ser atendida... etc.)
- Colas de trabajo: A nivel computacional (debido a que en computación los recursos son limitados -RAM, HD, ancho de banda, CPU-), no se puede atender a todos los usuarios al mismo tiempo, se deben ir atendiendo de a poco
- Colas de impresión

## Prioridad estricta y el problema de la inanición (starvation)

En `v82_colas_con_prioridad` las colas se atienden por **prioridad estricta**:
primero quien va a pagar deudas, después las compras de contado, y los créditos
al final.

El problema es que ese mecanismo **puede desatender para siempre a las colas de
menor prioridad**. Si no paran de llegar pagos de deudas, los que piden crédito
nunca se atienden. A ese fenómeno se le llama **inanición** (starvation).

## Round Robin

La solución es **rotar los turnos** entre las colas.

### Variación 1: Round Robin simple

Un turno por cola, en ciclo:

```
pago de deudas -> compra de contado -> solicitud de crédito -> (repite)
```

- Atiende 1 persona de pago de deudas
- Atiende 1 persona de compra de contado
- Atiende 1 persona de solicitud de crédito

**Ningún usuario espera más de 3 turnos.**

### Variación 2: Round Robin ponderado (Weighted Round Robin)

Cada tipo de trámite recibe un **peso** proporcional a cuántas personas deben
atenderse por vuelta. En el enunciado:

| Tipo de trámite    | Peso |
|--------------------|------|
| Pago de deudas     | 3    |
| Compra de contado  | 2    |
| Solicitud de crédito | 1  |

Los pesos generan el ciclo:

```
pago de deudas, pago de deudas, pago de deudas,
compra de contado, compra de contado,
solicitud de crédito -> (repite)
```

**Ningún usuario espera más de 6 turnos.**

Nota importante: los turnos se **intercalan** dentro del ciclo. Agruparlos
("3 de deudas, luego 2 de contado, luego 1 de crédito") volvería a introducir
inanición en las colas del final. El ciclo se repite completo.

En el fondo las dos variaciones son **el mismo algoritmo**: Round Robin simple
es Round Robin ponderado con todos los pesos iguales a 1.

### Implementación

La solución completa (API HTTP con FastAPI, persistencia en SQLite y arquitectura
por capas) está en `../v9_round_robin/`.

## Operaciones

### Encolar (enqueue):
Agrega un nuevo elemento a la cola
- append en Python

### Des-encolar (dequeue)
Tomar un trabajo de la cola.
- popleft

### Preguntar quien sigue (peek)
Simplemente preguntar, pero SIN atender.