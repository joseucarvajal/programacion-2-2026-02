class Producto:
    def __init__(self, codigo, nombre, precio, stock):
        self.codigo = codigo
        self.nombre = nombre
        self.precio = precio
        self.stock = stock

    def __repr__(self):
        return (
            f"Producto(codigo={self.codigo}, nombre={self.nombre}, "
            f"precio={self.precio}, stock={self.stock})"
        )
