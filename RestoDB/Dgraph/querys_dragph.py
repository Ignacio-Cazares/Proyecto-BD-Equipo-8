import json
import pydgraph


# schema e indices
def crear_schema(client):
    schema = """
    cliente_id: string @index(exact) .
    restaurante_id: string @index(exact) .
    platillo_id: string @index(exact) .
    tipo_id: string @index(exact) .
    nombre: string @index(exact, term) .
    email: string .
    numero_telefono: string .
    fecha_registro: datetime .
    descripcion: string .
    activo: bool .
    categoria: string .
    precio: float .

    ofrece: [uid] @reverse .
    tipo_comida: [uid] @reverse .
    platillo_favorito: [uid] @reverse .
    restaurante_favorito: [uid] .
    prefiere_tipo: [uid] .

    type Cliente {
        cliente_id
        nombre
        email
        numero_telefono
        fecha_registro
        platillo_favorito
        restaurante_favorito
        prefiere_tipo
    }

    type Restaurante {
        restaurante_id
        nombre
        descripcion
        activo
        ofrece
        tipo_comida
    }

    type Platillo {
        platillo_id
        nombre
        descripcion
        categoria
        precio
    }

    type TipoComida {
        tipo_id
        nombre
    }
    """
    client.alter(pydgraph.Operation(schema=schema))
    print("Schema creado exitosamente.")


def ejecutar_query(client, query, variables=None):
    res = client.txn(read_only=True).query(query, variables=variables)
    print(json.dumps(json.loads(res.json), indent=2, ensure_ascii=False))


# 17. Consultar platillos ofrecidos por un restaurante
def consultar_platillos_restaurante(client):
    restaurante_id = input("Ingresa el ID del restaurante: ")
    query = """
    query q($id: string) {
        restaurante(func: eq(restaurante_id, $id)) {
            nombre
            ofrece {
                nombre
                categoria
            }
        }
    }
    """
    ejecutar_query(client, query, {"$id": restaurante_id})


# 18. Consultar restaurantes que ofrecen un platillo
def consultar_restaurantes_platillo(client):
    platillo = input("Ingresa el nombre del platillo: ")
    query = """
    query q($nombre: string) {
        platillo(func: eq(nombre, $nombre)) @filter(type(Platillo)) {
            nombre
            categoria
            precio
            ofrecido_por: ~ofrece {
                nombre
                descripcion
            }
        }
    }
    """
    ejecutar_query(client, query, {"$nombre": platillo})


# 19. Consultar platillos favoritos de un cliente
def consultar_platillos_favoritos(client):
    cliente_id = input("Ingresa el ID del cliente: ")
    query = """
    query q($id: string) {
        cliente(func: eq(cliente_id, $id)) {
            nombre
            platillo_favorito {
                nombre
                restaurante: ~ofrece {
                    nombre
                }
            }
        }
    }
    """
    ejecutar_query(client, query, {"$id": cliente_id})


# 20. Consultar restaurantes favoritos de un cliente
def consultar_restaurantes_favoritos(client):
    cliente_id = input("Ingresa el ID del cliente: ")
    query = """
    query q($id: string) {
        cliente(func: eq(cliente_id, $id)) {
            nombre
            restaurante_favorito {
                nombre
                tipo_comida {
                    nombre
                }
            }
        }
    }
    """
    ejecutar_query(client, query, {"$id": cliente_id})


# 21. Consultar restaurantes por tipo de comida preferida
def consultar_restaurantes_tipo_preferido(client):
    cliente_id = input("Ingresa el ID del cliente: ")
    query = """
    query q($id: string) {
        var(func: eq(cliente_id, $id)) {
            prefiere_tipo {
                ~tipo_comida {
                    restaurantes as uid
                }
            }
        }

        cliente(func: eq(cliente_id, $id)) {
            nombre
            prefiere_tipo {
                nombre
            }
        }

        restaurantes(func: uid(restaurantes)) {
            nombre
            descripcion
            tipo_comida {
                nombre
            }
        }
    }
    """
    ejecutar_query(client, query, {"$id": cliente_id})


# 22. Encontrar clientes con platillos favoritos en comun
def consultar_clientes_platillos_comunes(client):
    cliente_id = input("Ingresa el ID del cliente: ")
    query = """
    query q($id: string) {
        var(func: eq(cliente_id, $id)) {
            mis_platillos as platillo_favorito
        }

        var(func: uid(mis_platillos)) {
            coincidentes as ~platillo_favorito @filter(NOT eq(cliente_id, $id))
        }

        clientes(func: uid(coincidentes)) {
            cliente_id
            nombre
            platillos_en_comun: platillo_favorito @filter(uid(mis_platillos)) {
                nombre
            }
        }
    }
    """
    ejecutar_query(client, query, {"$id": cliente_id})


# 23. Recomendar platillos segun preferencias similares
def recomendar_platillos(client):
    cliente_id = input("Ingresa el ID del cliente: ")
    query = """
    query q($id: string) {
        var(func: eq(cliente_id, $id)) {
            mis_platillos as platillo_favorito
        }

        var(func: uid(mis_platillos)) {
            similares as ~platillo_favorito @filter(NOT eq(cliente_id, $id))
        }

        var(func: uid(similares)) {
            recomendados as platillo_favorito @filter(NOT uid(mis_platillos))
        }

        recomendaciones(func: uid(recomendados)) {
            nombre
            categoria
            precio
            restaurante: ~ofrece {
                nombre
            }
        }
    }
    """
    ejecutar_query(client, query, {"$id": cliente_id})


# 24. Recomendar restaurantes a partir de platillos favoritos
def recomendar_restaurantes(client):
    cliente_id = input("Ingresa el ID del cliente: ")
    query = """
    query q($id: string) {
        var(func: eq(cliente_id, $id)) {
            restaurante_favorito {
                favoritos as uid
            }
            mis_platillos as platillo_favorito {
                ~ofrece {
                    candidatos as uid
                }
            }
        }

        recomendaciones(func: uid(candidatos)) @filter(NOT uid(favoritos)) {
            nombre
            descripcion
            tipo_comida {
                nombre
            }
            platillos_favoritos_que_ofrece: ofrece @filter(uid(mis_platillos)) {
                nombre
            }
        }
    }
    """
    ejecutar_query(client, query, {"$id": cliente_id})