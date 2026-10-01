"""Punto de entrada para desarrollo: ``python main.py``.

El puerto se puede cambiar sin tocar el código::

    python main.py 8001
    PORT=8001 python main.py

En produccion se arranca con uvicorn directamente::

    uvicorn round_robin.presentation.app:app --reload

Este archivo existe para poder ejecutar el servidor sin instalar el paquete.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Solo para correr sin `pip install -e .`: agrega src/ al path de busqueda.
sys.path.insert(0, str(Path(__file__).parent / "src"))

import uvicorn  # noqa: E402

from round_robin.presentation.app import app  # noqa: E402,F401


def puerto_por_defecto() -> int:
    """El puerto puede venir como argumento o en la variable PORT."""
    if len(sys.argv) > 1:
        return int(sys.argv[1])
    return int(os.getenv("PORT", "8000"))


if __name__ == "__main__":
    uvicorn.run(
        "round_robin.presentation.app:app",
        host="127.0.0.1",
        port=puerto_por_defecto(),
        reload=True,
    )