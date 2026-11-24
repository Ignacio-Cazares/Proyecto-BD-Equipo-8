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

# 13. Consultar los platillos mas caros de un restaurante
def consultar_platillos_mas_caros(db):
    restaurante_id = input("Ingresa el ID del restaurante: ")
    resultados = db.restaurantes.aggregate([
        {"$match": {"_id": ObjectId(restaurante_id)}},
        {"$unwind": "$menu"},
        {"$match": {"menu.disponible": True}},
        {"$sort": {"menu.precio": -1}},
        {"$limit": 5},
        {
            "$project": {
                "_id": 0,
                "nombre": "$menu.nombre",
                "categoria": "$menu.categoria",
                "precio": "$menu.precio"
            }
        }
    ])
    for doc in resultados:
        print(doc)
# 14. Consultar el total de ventas por restaurante
def consultar_total_ventas_restaurante(db):
    fecha_inicio = input("Ingresa fecha de inicio (AAAA-MM-DD): ")
    fecha_fin = input("Ingresa fecha de fin (AAAA-MM-DD): ")
    f_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    f_fin = datetime.strptime(fecha_fin + " 23:59:59", "%Y-%m-%d %H:%M:%S")
    resultados = db.pedidos.aggregate([
        {
            "$match": {
                "estado": "entregado",
                "fecha": {"$gte": f_inicio, "$lte": f_fin}
            }
        },
        {
            "$group": {
                "_id": "$restaurante_id",
                "nombre_restaurante": {"$first": "$nombre_restaurante"},
                "cantidad_pedidos": {"$sum": 1},
                "monto_total": {"$sum": "$total"}
            }
        },
        {"$sort": {"monto_total": -1}},
        {
            "$project": {
                "_id": 0,
                "restaurante_id": "$_id",
                "nombre": "$nombre_restaurante",
                "cantidad_pedidos": 1,
                "monto_total": 1
            }
        }
    ])
    for doc in resultados:
        print(doc)
# 15. Consultar detalle de un pedido
def consultar_detalle_pedido(db):
    pedido_id = input("Ingresa el ID del pedido: ")
    pedido = db.pedidos.find_one({"_id": ObjectId(pedido_id)})
    if pedido:
        print(pedido)
    else:
        print("Pedido no encontrado")
# 16. Consultar los platillos mas vendidos
def consultar_platillos_mas_vendidos(db):
    restaurante_id = input("Ingresa el ID del restaurante: ")
    fecha_inicio = input("Ingresa fecha de inicio (AAAA-MM-DD): ")
    fecha_fin = input("Ingresa fecha de fin (AAAA-MM-DD): ")
    f_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    f_fin = datetime.strptime(fecha_fin + " 23:59:59", "%Y-%m-%d %H:%M:%S")
    resultados = db.pedidos.aggregate([
        {
            "$match": {
                "restaurante_id": ObjectId(restaurante_id),
                "estado": "entregado",
                "fecha": {"$gte": f_inicio, "$lte": f_fin}
            }
        },
        {"$unwind": "$items"},
        {
            "$group": {
                "_id": "$items.platillo_id",
                "nombre": {"$first": "$items.nombre"},
                "unidades_vendidas": {"$sum": "$items.cantidad"},
                "monto_generado": {"$sum": "$items.subtotal"}
            }
        },
        {"$sort": {"unidades_vendidas": -1}},
        {"$limit": 5},
        {
            "$project": {
                "_id": 0,
                "platillo_id": "$_id",
                "nombre": 1,
                "unidades_vendidas": 1,
                "monto_generado": 1
            }
        }
    ])
    for doc in resultados:
        print(doc)