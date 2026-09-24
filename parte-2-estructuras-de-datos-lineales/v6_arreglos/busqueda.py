from tienda import generar_catalogo

def buscar_producto_lineal(arreglo_productos, codigo):
    comparaciones = 0
    for producto in arreglo_productos:
        comparaciones += 1
        if producto.codigo == codigo:
            return producto, comparaciones

    return None, comparaciones

def buscar_producto_por_indice(arreglo_productos, indice):
    if 0 <= indice < len(arreglo_productos):
        return arreglo_productos[indice], 1
    return None, 1

if __name__ == "__main__":
    arreglo_productos = generar_catalogo(100)

    codigo_a_buscar = 99
    producto_encontrado, comparaciones = buscar_producto_lineal(arreglo_productos, codigo_a_buscar)
    producto_encontrado_por_indice, comparaciones_por_indice = buscar_producto_por_indice(arreglo_productos, 99)

    if producto_encontrado != None:
        print(f"Búsqueda lineal - Producto encontrado: {producto_encontrado.nombre}, Comparaciones realizadas: {comparaciones}")
    else:
        print(f"Búsqueda lineal - Producto con código {codigo_a_buscar} no encontrado, Comparaciones realizadas: {comparaciones}")

    if producto_encontrado_por_indice != None:
        print(f"Búsqueda por índice - Producto encontrado: {producto_encontrado_por_indice.nombre}, Comparaciones realizadas: {comparaciones_por_indice}")
    else:
        print(f"Búsqueda por índice - Producto en el índice {10} no encontrado, Comparaciones realizadas: {comparaciones_por_indice}")