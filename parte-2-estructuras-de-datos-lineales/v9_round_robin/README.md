# Ejecutar el proyecto

API de las colas de la tienda con rotación **Round Robin**.

Referencia técnica (endpoints, arquitectura, decisiones de diseño) en
[REFERENCIA.md](REFERENCIA.md).

## Requisitos

- **Python 3.10 o superior.**

SQLite viene incluido en Python, no se instala nada más.

> En macOS el `python3` del sistema suele ser 3.9. Si es tu caso, instala
> Python 3.13 con `brew install python@3.13` y sustituye `python3.13` por tu
> versión en los comandos de abajo.

## Pasos

Ejecuta esto desde la carpeta `v9_round_robin`:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python main.py
```

Para detener el servidor: `Ctrl + C`.

El entorno virtual hay que activarlo **cada vez que abras una terminal nueva**:

```bash
cd parte-2-estructuras-de-datos-lineales/v9_round_robin
source .venv/bin/activate
```

## Abrir la documentación

En el navegador: <http://127.0.0.1:8000/docs>

Desde ahí puedes probar todos los endpoints con el botón *Try it out*.

## Comprobar que funciona

En otra terminal, con el servidor corriendo:

```bash
curl localhost:8000/api/v1/health
```

Respuesta esperada:

```json
{"estado":"ok","politica":"round-robin-ponderado","longitud_ciclo":6}
```

## Correr los tests

```bash
pytest
```

Debe terminar con `99 passed`. No necesitan el servidor corriendo.

## Empezar de cero

Para borrar la base de datos y arrancar limpio:

```bash
rm -rf var/
```

Se recrea sola al levantar el servidor.
