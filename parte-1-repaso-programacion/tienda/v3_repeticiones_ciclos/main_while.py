'''
- Aplicación para una tienda
- Versión: v3.0
- Qué incluye:
    - Repeticiones: While
    Soluciona: B-10. Usualmente, el cliente comprador de productos en el supermercado no sabe cuántos productos lleva en su canasto/carrito de compras 
- Qué problemas/errores (BUGS) tiene:
    B-3. El precio acepta caracteres no numéricos
    B-6. El descuento acepta caracteres no numéricos
    B-10. Cuando hay un error, el programa se cierra intempestivamente. Debería volver a preguntar el valor que se ingresó mal y dejar continuar al usuario ingresando datos
    
'''

quiere_seguir_llevando_productos = True
total_compra = 0
i = 0

while quiere_seguir_llevando_productos == True: # B-10. Usualmente, el cliente comprador de productos en el supermercado no sabe cuántos productos lleva en su canasto/carrito de compras 
    nombre_del_producto = input(f"Ingrese el nombre del producto {i + 1}: ") # variable e input
    if nombre_del_producto == "": # Solución al BUG B-1: El nombre puede ser vacío
        print("ERROR: El nombre del producto no puede estar vacío")
    else:
        precio_del_producto = input(f"Ingrese el precio del producto {i + 1}: ") # variable e input
        if precio_del_producto == "":
            print("ERROR: El precio del producto no puede estar vacío") # Solución al BUG B-2: El precio puede ser vacío
        else:
            precio_del_producto = float(precio_del_producto) # Tipos de variables: decimal, es decir: float
            if precio_del_producto < 0:
                print("ERROR: El precio del producto no puede ser un valor negativo") # Solución al BUG B-4: El precio puede ser negativo
            else:
                descuento_del_producto = input("Ingrese el descuento del producto: ") # variable e input
                if descuento_del_producto == "":
                    print("ERROR: El descuento del producto no puede ser vacío") # Solución al BUG B-5: El descuento puede ser vacío
                else:
                    descuento_del_producto = float(descuento_del_producto) # Tipos de variables: decimal, es decir: float
                    if descuento_del_producto < 0:
                        print("ERROR: El descuento del producto no puede ser un valor negativo") # Solución al BUG B-7. El descuento puede ser negativo
                    else:
                        if descuento_del_producto > precio_del_producto:
                            print("ERROR: El descuento del producto no puede ser mayor a su precio")# Solución al BUG B-8. El descuento puede ser mayor al precio
                        else:
                            total_producto = precio_del_producto - descuento_del_producto # Variables y operadores (+,-,*,/)
                            print(f"El precio final del producto {i + 1} es: {nombre_del_producto} es: {total_producto}") # Output o salida de datos
                            total_compra = total_compra + total_producto
                            i = i + 1
                            quiere_llevar_mas_respuesta = input("Desea llevar más productos? s/n: ")
                            if quiere_llevar_mas_respuesta != 's':
                                quiere_seguir_llevando_productos = False

print(f"El total a pagar es: {total_compra}")