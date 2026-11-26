import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from uuid import UUID

from connect import connect_mongodb, connect_dgraph
from populate import convertir_uuid

from Cassandra import queries as cassandra
from MongoDB import querys_mongo as mongo
from Dgraph import querys_dragph as dgraph


CONSULTAS_CASSANDRA = {
    1: (
        "Consultar historial de pedidos de un cliente",
        cassandra.consultar_historial_pedidos_cliente,
        ("ID del cliente",)
    ),
    2: (
        "Consultar pedidos de un cliente por rango de fechas",
        cassandra.consultar_pedidos_cliente_rango_fechas,
        (
            "ID del cliente",
            "Fecha inicial (AAAA-MM-DD)",
            "Fecha final (AAAA-MM-DD)"
        )
    ),
    3: (
        "Consultar historial de pedidos de un restaurante",
        cassandra.consultar_historial_pedidos_restaurante,
        ("ID del restaurante", "Fecha (AAAA-MM-DD)")
    ),
    4: (
        "Consultar pedidos de un restaurante por estado",
        cassandra.consultar_pedidos_restaurante_por_estado,
        (
            "ID del restaurante",
            "Fecha (AAAA-MM-DD)",
            "Estado del pedido"
        )
    ),
    5: (
        "Consultar historial de cambios de estado de un pedido",
        cassandra.consultar_historial_estados_pedido,
        ("ID del pedido",)
    ),
    6: (
        "Consultar pedidos de un cliente en un restaurante específico",
        cassandra.consultar_pedidos_cliente_restaurante,
        ("ID del cliente", "ID del restaurante")
    ),
    7: (
        "Consultar historial de actividad de un cliente",
        cassandra.consultar_historial_actividad_cliente,
        ("ID del cliente",)
    ),
    8: (
        "Consultar actividad de clientes por tipo de evento y fecha",
        cassandra.consultar_actividad_por_fecha_tipo,
        ("Fecha (AAAA-MM-DD)", "Tipo de evento")
    )
}


CONSULTAS_MONGODB = {
    9: (
        "Consultar restaurantes disponibles",
        mongo.consultar_restaurantes_disponibles
    ),
    10: (
        "Consultar menú de un restaurante",
        mongo.consultar_menu_restaurante
    ),
    11: (
        "Buscar platillos por categoría y precio",
        mongo.buscar_platillos_categoria_precio
    ),
    12: (
        "Consultar clientes por nombre o correo electrónico",
        mongo.consultar_clientes
    ),
    13: (
        "Consultar los platillos más caros de un restaurante",
        mongo.consultar_platillos_mas_caros
    ),
    14: (
        "Consultar el total de ventas por restaurante",
        mongo.consultar_total_ventas_restaurante
    ),
    15: (
        "Consultar detalle de un pedido",
        mongo.consultar_detalle_pedido
    ),
    16: (
        "Consultar los platillos más vendidos",
        mongo.consultar_platillos_mas_vendidos
    )
}

CONSULTAS_DGRAPH = {
    17: (
        "Consultar platillos ofrecidos por un restaurante",
        dgraph.consultar_platillos_restaurante
    ),
    18: (
        "Consultar restaurantes que ofrecen un platillo",
        dgraph.consultar_restaurantes_platillo
    ),
    19: (
        "Consultar platillos favoritos de un cliente",
        dgraph.consultar_platillos_favoritos
    ),
    20: (
        "Consultar restaurantes favoritos de un cliente",
        dgraph.consultar_restaurantes_favoritos
    ),
    21: (
        "Consultar restaurantes por tipo de comida preferida",
        dgraph.consultar_restaurantes_tipo_preferido
    ),
    22: (
        "Encontrar clientes con platillos favoritos en común",
        dgraph.consultar_clientes_platillos_comunes
    ),
    23: (
        "Recomendar platillos según preferencias similares",
        dgraph.recomendar_platillos
    ),
    24: (
        "Recomendar restaurantes a partir de platillos favoritos",
        dgraph.recomendar_restaurantes
    )
}


def mostrar_menu():
    print("\n========== RestoDB ==========")
    print("Sistema de Gestión de Restaurantes y Pedidos")

    for titulo, consultas in (
        ("CASSANDRA", CONSULTAS_CASSANDRA),
        ("MONGODB", CONSULTAS_MONGODB),
        ("DGRAPH", CONSULTAS_DGRAPH)
    ):
        print(f"\n--- {titulo} ---")

        for numero, datos in consultas.items():
            print(f"{numero}. {datos[0]}")

    print("\n0. Salir")


def cargar_identificadores():
    """
    Relaciona los UUID internos de Cassandra
    con los identificadores de nuestros archivos JSON.
    """
    ruta = Path(__file__).resolve().parent / "data"
    mapa = {}

    for archivo in (
        "clientes.json",
        "restaurantes.json",
        "pedidos.json"
    ):
        with open(ruta / archivo, "r", encoding="utf-8") as f:
            registros = json.load(f)

        for registro in registros:
            id_original = registro["_id"]
            uuid_cassandra = convertir_uuid(id_original)

            mapa[str(uuid_cassandra)] = id_original

    return mapa


def pedir_parametros(etiquetas):
    valores = []

    for etiqueta in etiquetas:
        valor = input(f"{etiqueta}: ").strip()

        if not valor:
            raise ValueError(
                f"Debes proporcionar: {etiqueta}."
            )

        if "fecha" in etiqueta.lower():
            try:
                datetime.strptime(valor, "%Y-%m-%d")
            except ValueError as error:
                raise ValueError(
                    "La fecha debe ser válida y "
                    "tener formato AAAA-MM-DD."
                ) from error

        valores.append(valor)

    return valores


def mostrar_resultados_cassandra(resultados, mapa_ids):
    if not resultados:
        print("\nNo se encontraron registros con esos criterios.")
        return

    print(f"\nSe encontraron {len(resultados)} registros:")

    for numero, fila in enumerate(resultados, start=1):
        print(f"\n--- Registro {numero} ---")

        for campo, valor in fila._asdict().items():

            if isinstance(valor, UUID):
                valor = mapa_ids.get(
                    str(valor),
                    str(valor)
                )

            elif isinstance(valor, datetime):
                valor = (
                    valor.strftime("%Y-%m-%d %H:%M:%S")
                    + " UTC"
                )

            elif campo == "total" and valor is not None:
                valor = f"${Decimal(valor):.2f}"

            nombre_campo = campo.replace("_", " ").capitalize()

            print(f"{nombre_campo}: {valor}")


def ejecutar_cassandra(opcion, mapa_ids):
    _, funcion, etiquetas = CONSULTAS_CASSANDRA[opcion]

    valores = pedir_parametros(etiquetas)

    resultados = funcion(*valores)

    mostrar_resultados_cassandra(
        resultados,
        mapa_ids
    )


def ejecutar_mongodb(opcion):
    _, funcion = CONSULTAS_MONGODB[opcion]

    cliente = None

    try:
        cliente, db = connect_mongodb()

        funcion(db)

    finally:
        if cliente is not None:
            cliente.close()


def ejecutar_dgraph(opcion):
    _, funcion = CONSULTAS_DGRAPH[opcion]

    stub = None

    try:
        stub, cliente = connect_dgraph()

        funcion(cliente)

    finally:
        if stub is not None:
            stub.close()


def main():
    mapa_ids = cargar_identificadores()

    while True:
        mostrar_menu()

        try:
            seleccion = input(
                "\nSelecciona una opción (0-24): "
            ).strip()

            if seleccion == "0":
                print("Saliendo de RestoDB...")
                break

            if not seleccion.isdigit():
                print("Ingresa un número de opción válido.")
                continue

            opcion = int(seleccion)

            if opcion in CONSULTAS_CASSANDRA:
                ejecutar_cassandra(opcion, mapa_ids)

            elif opcion in CONSULTAS_MONGODB:
                ejecutar_mongodb(opcion)

            elif opcion in CONSULTAS_DGRAPH:
                ejecutar_dgraph(opcion)

            else:
                print("La opción seleccionada no existe.")

        except (KeyboardInterrupt, EOFError):
            print("\nSaliendo de RestoDB...")
            break

        except Exception as error:
            print(f"\nError al ejecutar la consulta: {error}")


if __name__ == "__main__":
    main()
