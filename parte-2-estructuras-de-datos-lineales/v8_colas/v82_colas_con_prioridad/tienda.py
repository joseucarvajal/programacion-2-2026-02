from collections import deque
from usuario import Usuario

class Tienda:

    def __init__(self, nombre):
        self.nombre = nombre
        self.cola_usuarios_que_viene_a_pagar_deudas = deque()
        self.cola_usuarios_que_viene_a_comprar_de_contado = deque()
        self.cola_usuarios_que_viene_a_fiar = deque()

    def encolar_usuario_por_prioridad_segun_tramite(self, usuario:Usuario):
        if usuario.tipo_tramite == 0: # Pago de deudas
            self.cola_usuarios_que_viene_a_pagar_deudas.append(usuario)
        elif usuario.tipo_tramite == 1: # Compra de contado
            self.cola_usuarios_que_viene_a_comprar_de_contado.append(usuario)
        elif usuario.tipo_tramite == 2: # Viene a fiar
            self.cola_usuarios_que_viene_a_fiar.append(usuario)

    '''
    PROBLEMA: Este mecanismos es un mecanismo de "Prioridad Estricta". El problema que tiene es que las colas de menor prioridad pueden quedar desatendidas
    inanición (starvation)
    SOLUCIÓN: Implementar un algoritmo de Round Robin. Dos variaciones:
        - Variación número 1:
            Se atiende 1 persona de pago de deudas
            Se atiende 1 persona de compra de contado
            Se atiende 1 persona de solicitud de crédito
        - Variación número 2 (Round Robin ponderado - Weighted Round Robin):
            Se atiende 3 persona de pago de deudas
            Se atiende 2 persona de compra de contado
            Se atiende 1 persona de solicitud de crédito
    '''
    def atender_siguiente_usuario(self):
        if self.cola_usuarios_que_viene_a_pagar_deudas:
            usuario = self.cola_usuarios_que_viene_a_pagar_deudas.popleft()
            print(f"Atendiendo al usuario de la cola de pago de deudas: {usuario.nombre}")
            return
        
        if self.cola_usuarios_que_viene_a_comprar_de_contado:
            usuario = self.cola_usuarios_que_viene_a_comprar_de_contado.popleft()
            print(f"Atendiendo al usuario de la cola de compras de contado: {usuario.nombre}")
            return
        
        if self.cola_usuarios_que_viene_a_fiar:
            usuario = self.cola_usuarios_que_viene_a_fiar.popleft()
            print(f"Atendiendo al usuario de la cola de solicitudes de crédito: {usuario.nombre}")
            return
        
    def consultar_siguiente_usuario_en_la_cola(self):
        if self.cola_usuarios_que_viene_a_pagar_deudas:
            usuario = self.cola_usuarios_que_viene_a_pagar_deudas[0]
            print(f"El siguiente usuario es de la cola de pago de deudas: {usuario.nombre}")
            return
        
        if self.cola_usuarios_que_viene_a_comprar_de_contado:
            usuario = self.cola_usuarios_que_viene_a_comprar_de_contado[0]
            print(f"El siguiente usuario es de la cola de compras de contado: {usuario.nombre}")
            return
        
        if self.cola_usuarios_que_viene_a_fiar:
            usuario = self.cola_usuarios_que_viene_a_fiar[0]
            print(f"El siguiente usuario es de la cola de solicitudes de crédito: {usuario.nombre}")
            return

    
    def consultar_todas_las_colas_de_usuarios(self):
        total_usuarios_pendientes = 0
        total_monto_transacciones_pendientes = 0.0

        for usuario in self.cola_usuarios_que_viene_a_pagar_deudas:
            total_usuarios_pendientes += 1
            total_monto_transacciones_pendientes = total_monto_transacciones_pendientes + usuario.monto_transaccion
            print(f"Usuario por atender de pago de deudas: {usuario.nombre}, Monto de transacción: {usuario.monto_transaccion}")

        for usuario in self.cola_usuarios_que_viene_a_comprar_de_contado:
            total_usuarios_pendientes += 1
            total_monto_transacciones_pendientes = total_monto_transacciones_pendientes + usuario.monto_transaccion
            print(f"Usuario por atender de compra de contado: {usuario.nombre}, Monto de transacción: {usuario.monto_transaccion}")

        for usuario in self.cola_usuarios_que_viene_a_fiar:
            total_usuarios_pendientes += 1
            total_monto_transacciones_pendientes = total_monto_transacciones_pendientes + usuario.monto_transaccion
            print(f"Usuario por atender de solicitud de crédito: {usuario.nombre}, Monto de transacción: {usuario.monto_transaccion}")

        print(f"Total de usuarios pendientes: {total_usuarios_pendientes}")
        print(f"Total de monto de transacciones pendientes: {total_monto_transacciones_pendientes}")