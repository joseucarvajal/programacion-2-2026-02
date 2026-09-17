from collections import deque

from producto import Producto

lista_productos = deque()

def agregar_producto_al_final(producto):
    lista_productos.append(producto)

def buscar_producto_por_indice(indice):
    if 0 <= indice < len(lista_productos):
        return lista_productos[indice]
    return None

def buscar_producto_por_codigo(codigo):
    for producto in lista_productos:
        if producto.codigo == codigo:
            return producto
    return None


def total_carrito():
    total = 0
    for producto in lista_productos:
        total += producto.precio
    return total


if __name__ == "__main__":
    # Agregar productos al carrito

    agregar_producto_al_final(Producto(1, "Producto A", 10.0, 5))
    agregar_producto_al_final(Producto(2, "Producto B", 20.0, 3))
    agregar_producto_al_final(Producto(3, "Producto C", 15.0, 2))

    # Buscar producto por índice
    indice_a_buscar = 1
    producto_encontrado_por_indice = buscar_producto_por_indice(indice_a_buscar)
    if producto_encontrado_por_indice is not None:
        print(f"Producto encontrado en el índice {indice_a_buscar}: {producto_encontrado_por_indice.nombre}")
    else:
        print(f"No se encontró ningún producto en el índice {indice_a_buscar}")

    # Buscar producto por código
    codigo_a_buscar = 2
    producto_encontrado_por_codigo = buscar_producto_por_codigo(codigo_a_buscar)
    if producto_encontrado_por_codigo is not None:
        print(f"Producto encontrado con código {codigo_a_buscar}: {producto_encontrado_por_codigo.nombre}")
    else:
        print(f"No se encontró ningún producto con código {codigo_a_buscar}")

    # Calcular total del carrito
    total = total_carrito()
    print(f"Total del carrito: ${total:.2f}")