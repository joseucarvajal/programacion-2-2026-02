'''
- Aplicación para una tienda
- Versión: v2.0
- Qué incluye:
    - Decisiones: Condicionales (if, elif, else)
- Qué problemas/errores (BUGS) tiene:
    B-1. El nombre puede ser vacío
    B-2. El precio puede ser vacío
    B-4. El precio puede ser negativo
    B-5. El descuento puede ser vacío
    B-7. El descuento puede ser negativo
    B-8. El descuento puede ser mayor al precio
'''

nombre_del_producto = input("Ingrese el nombre del producto: ") # variable e input
if nombre_del_producto == "": # Solución al BUG B-1: El nombre puede ser vacío
    print("ERROR: El nombre del producto no puede estar vacío")
else:
    precio_del_producto = input("Ingrese el precio del producto: ") # variable e input
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
                        total_a_pagar = precio_del_producto - descuento_del_producto # Variables y operadores (+,-,*,/)
                        print(f"El precio final de {nombre_del_producto} es: {total_a_pagar}") # Output o salida de datos