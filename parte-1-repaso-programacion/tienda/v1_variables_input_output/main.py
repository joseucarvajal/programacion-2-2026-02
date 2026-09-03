'''
- Aplicación para una tienda
- Versión: v1.0
- Qué incluye:
    - Variables (Y tipos de datos: str, int, float)
    - Input
    - Output
    - Operadores aritméticos (+,-,*,/)
- Qué problemas/errores (BUGS) tiene:
    B-1. El nombre puede ser vacío
    B-2. El precio puede ser vacío
    B-3. El precio acepta caracteres no numéricos
    B-4. El precio puede ser negativo
    B-5. El descuento puede ser vacío
    B-6. El descuento acepta caracteres no numéricos
    B-7. El descuento puede ser negativo
    B-8. El descuento puede ser mayor al precio
    B-9. El programa solamente sirve para un solo producto, no para varios productos
'''

nombre_del_producto = input("Ingrese el nombre del producto: ") # variable e input

precio_del_producto = input("Ingrese el precio del producto: ") # variable e input
precio_del_producto = float(precio_del_producto) # Tipos de variables: decimal, es decir: float

descuento_del_producto = input("Ingrese el descuento del producto: ") # variable e input
descuento_del_producto = float(descuento_del_producto) # Tipos de variables: decimal, es decir: float

total_a_pagar = precio_del_producto - descuento_del_producto # Variables y operadores (+,-,*,/)

print(f"El precio final de {nombre_del_producto} es: {total_a_pagar}") # Output o salida de datos