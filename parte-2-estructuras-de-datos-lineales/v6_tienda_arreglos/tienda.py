import random
from producto import Producto

def generar_catalogo(n):
    arreglo_productos = [
        Producto(
            codigo=i,
            nombre= f"Producto {i}",
            precio=round(random.uniform(5, 500), 2),
            stock=random.randint(0, 100),
        )
        for i in range(n)
    ]

    return arreglo_productos
