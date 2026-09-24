from collections import deque
from usuario import Usuario

class Tienda:

    def __init__(self, nombre):
        self.nombre = nombre
        self.cola_usuarios = deque()

    def agregar_usuario_a_cola(self, usuario: Usuario):
        self.cola_usuarios.append(usuario)

    # Esta operación, elimina el usuario de la cola y lo hace automáticamente.
    def atender_siguiente_usuario(self):
        if self.cola_usuarios:
            usuario_atendido = self.cola_usuarios.popleft()
            print(f"Atendiendo al usuario: {usuario_atendido.nombre}")
        else:
            print("No hay usuarios en la cola para atender.")

    # Esta operación, permite consultar el siguiente usuario en la cola sin eliminarlo.
    def consultar_siguiente_usuario_en_la_cola(self):
        if self.cola_usuarios:
            siguiente_usuario = self.cola_usuarios[0]
            print(f"El siguiente usuario en la cola es: {siguiente_usuario.nombre}")
        else:
            print("No hay usuarios en la cola.")

    
    def consultar_toda_la_cola_de_usuarios(self):
        total_usuarios_pendientes = 0
        total_monto_transacciones_pendientes = 0.0

        for usuario in self.cola_usuarios:
            total_usuarios_pendientes += 1
            total_monto_transacciones_pendientes = total_monto_transacciones_pendientes + usuario.monto_transaccion
            print(f"Usuario por atender: {usuario.nombre}, Monto de transacción: {usuario.monto_transaccion}")

        print(f"Total de usuarios pendientes: {total_usuarios_pendientes}")
        print(f"Total de monto de transacciones pendientes: {total_monto_transacciones_pendientes}")