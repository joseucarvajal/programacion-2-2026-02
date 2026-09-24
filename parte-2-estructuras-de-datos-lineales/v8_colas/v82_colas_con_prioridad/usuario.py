class Usuario:
    
    def __init__(self, nombre, tipo_tramite, monto_transaccion):
        self.nombre = nombre
        self.tipo_tramite = tipo_tramite #0: Viene a pagar una deuda, 1: Viene a comprar de contado, #2: Viene a fiar
        self.monto_transaccion = monto_transaccion
