# la clase es el Molde para crear productos (objetos)
class Producto:

    # Atributos / datos
    nombre: str
    precio: float
    descuento: float

    # Métodos
    def solicitar_nombre(self):
        self.nombre = input("Ingrese el nombre del producto: ")
        if self.nombre == "":
            print("ERROR: el nombre del producto no puede ser vacio")
