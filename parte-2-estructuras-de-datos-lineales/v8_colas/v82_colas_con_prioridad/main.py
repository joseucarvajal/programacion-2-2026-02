from tienda import Tienda
from usuario import Usuario


def main():
    
    tienda = Tienda("Tienda Número 1 con prioridades")

    print(tienda.nombre)

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
            tipo_tramite = int(input("Ingrese el tipo de trámite (0: pago de deudas, 1: compra al contado, 2: solicitud de crédito): "))
            usuario = Usuario(nombre, tipo_tramite, monto_transaccion)
            tienda.encolar_usuario_por_prioridad_segun_tramite(usuario)

        elif opcion == 2:
            print("Vamos a atender el siguiente usuario en la cola")
            tienda.atender_siguiente_usuario()

        elif opcion == 3:
            print("Vamos a consultar el siguiente usuario en la cola")
            tienda.consultar_siguiente_usuario_en_la_cola()

        elif opcion == 4:
            print("Vamos a consultar TODOS los usuarios en la cola")
            tienda.consultar_todas_las_colas_de_usuarios()

        else:
            break
            
if __name__ == "__main__":
    main()