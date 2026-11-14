from datetime import datetime
from bson import ObjectId

#indices
def crear_indices(db):
    db.restaurantes.create_index([("activo", 1)])
    db.restaurantes.create_index([("menu.categoria", 1)])
    db.clientes.create_index([("email", 1)])
    db.pedidos.create_index([("restaurante_id", 1), ("fecha", 1)])

# 9. Consultar restaurantes disponibles 
def consultar_restaurantes_disponibles(db):
    resultados = db.restaurantes.find(
        {"activo": True},
        {"nombre": 1, "tipo_comida": 1, "descripcion": 1}
    )
    for doc in resultados:
        print(doc)

# 10. Consultar menu de un restaurante 
def consultar_menu_restaurante(db):
    restaurante_id = input("Ingresa el ID del restaurante: ")
    resultados = db.restaurantes.aggregate([
        {"$match": {"_id": ObjectId(restaurante_id)}},
        {"$unwind": "$menu"},
        {"$match": {"menu.disponible": True}},
        {
            "$project": {
                "_id": 0,
                "menu.nombre": 1,
                "menu.descripcion": 1,
                "menu.precio": 1,
                "menu.categoria": 1
            }
        }
    ])
    for doc in resultados:
        print(doc)

# 11. Buscar platillos por categoria y precio 
def buscar_platillos_categoria_precio(db):
    restaurante_id = input("Ingresa el ID del restaurante: ")
    categoria = input("Ingresa la categoria a buscar: ")
    precio_max = float(input("Ingresa el precio maximo: "))
    resultados = db.restaurantes.aggregate([
        {"$match": {"_id": ObjectId(restaurante_id)}},
        {"$unwind": "$menu"},
        {
            "$match": {
                "menu.disponible": True,
                "menu.categoria": categoria,
                "menu.precio": {"$lte": precio_max}
            }
        },
        {
            "$project": {
                "_id": 0,
                "menu.nombre": 1,
                "menu.descripcion": 1,
                "menu.categoria": 1,
                "menu.precio": 1
            }
        }
    ])
    for doc in resultados:
        print(doc)
        
# 12. Consultar clientes por nombre o correo electronico 
def consultar_clientes(db):
    criterio = input("Ingresa el nombre o correo electronico del cliente: ")
    resultados = db.clientes.find(
        {"$or": [{"nombre": criterio}, {"email": criterio}]},
        {"nombre": 1, "email": 1}
    )
    for doc in resultados:
        print(doc)