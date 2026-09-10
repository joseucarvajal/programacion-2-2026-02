from producto import Producto #molde, clase

# objeto - galleta 1
producto_1 = Producto()
producto_1.solicitar_nombre()
producto_1.precio = float(input("Ingrese el precio del producto 1: "))
producto_1.descuento = 1

# objeto - galleta 2
producto_2 = Producto()
producto_2.solicitar_nombre()
producto_2.precio = 135
producto_2.descuento = 0

# objeto - galleta 3
producto_3 = Producto()
producto_3.solicitar_nombre()
producto_3.precio = 78
producto_3.descuento = 8


total_compra = producto_1.precio + producto_2.precio + producto_3.precio

print(f"El total de la compra es: {total_compra}")