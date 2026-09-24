# Colas (FIFO : First In First Out)

Sirven para muchos procesos en la vida real, ejemplos:
- La cola de un banco (la primera persona en llegar es la primera persona en ser atendida, la segunda persona en llegar será la segunda persona en ser atendida... etc.)
- Colas de trabajo: A nivel computacional (debido a que en computación los recursos son limitados -RAM, HD, ancho de banda, CPU-), no se puede atender a todos los usuarios al mismo tiempo, se deben ir atendiendo de a poco
- Colas de impresión

## Operaciones

### Encolar (enqueue):
Agrega un nuevo elemento a la cola
- append en Python

### Des-encolar (dequeue)
Tomar un trabajo de la cola.
- popleft

### Preguntar quien sigue (peek)
Simplemente preguntar, pero SIN atender.