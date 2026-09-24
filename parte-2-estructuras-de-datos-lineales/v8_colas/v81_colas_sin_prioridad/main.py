from tienda import Tienda
from usuario import Usuario


def main():
    
    tienda = Tienda("Tienda Número 1")

    while True:
        print("1. Registrar un usuario en la cola")
        print("2. Atender el siguiente usuario de la cola")
        print("3. Consultar el siguiente usuario en la cola")
        print("4. Consultar todos los usuarios de la cola")
        print("5. Salir")

        opcion = int(input("Ingrese una opción (1...5): "))

        if opcion == 1:
            print("Vamos a registrar un usuario en la cola")
            nombre = input("Ingrese el nombre del usuario: ")
            monto_transaccion = float(input("Ingrese el monto de la transacción: "))
            usuario = Usuario(nombre, monto_transaccion)
            tienda.agregar_usuario_a_cola(usuario)

        elif opcion == 2:
            print("Vamos a atender el siguiente usuario en la cola")
            tienda.atender_siguiente_usuario()

        elif opcion == 3:
            print("Vamos a consultar el siguiente usuario en la cola")
            tienda.consultar_siguiente_usuario_en_la_cola()

        elif opcion == 4:
            print("Vamos a consultar TODOS los usuarios en la cola")
            tienda.consultar_toda_la_cola_de_usuarios()

        else:
            break
            
if __name__ == "__main__":
    main()