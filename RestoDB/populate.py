import argparse
import json
from pathlib import Path
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid5, NAMESPACE_URL

from bson import ObjectId
from connect import connect_mongodb, connect_cassandra


# Carpeta donde están almacenados nuestros JSON
DATA_DIR = Path(__file__).resolve().parent / "data"


def leer_datos():
    archivos = {
        "restaurantes": "restaurantes.json",
        "clientes": "clientes.json",
        "pedidos": "pedidos.json",
        "historial_estados": "historial_estados.json",
        "actividades": "actividades.json",
        "preferencias": "preferencias.json"
    }

    datos = {}

    for nombre, archivo in archivos.items():
        ruta = DATA_DIR / archivo

        with open(ruta, "r", encoding="utf-8") as f:
            datos[nombre] = json.load(f)

        print(
            f"{archivo}: {len(datos[nombre])} registros leídos"
        )

    return datos


def convertir_fecha(valor):
    fecha = datetime.fromisoformat(
        valor.replace("Z", "+00:00")
    )

    if fecha.tzinfo is None:
        raise ValueError("La fecha debe incluir zona horaria")

    return fecha.astimezone(timezone.utc)


def convertir_uuid(identificador):
    return uuid5(
        NAMESPACE_URL,
        f"restodb:{identificador}"
    )



def poblar_mongodb(datos):
    cliente = None

    try:
        cliente, db = connect_mongodb()

        # Insertar restaurantes y menús
        for restaurante in datos["restaurantes"]:
            documento = restaurante.copy()

            documento["_id"] = ObjectId(
                restaurante["_id"]
            )

            documento["menu"] = [
                {
                    **platillo,
                    "platillo_id": ObjectId(
                        platillo["platillo_id"]
                    )
                }
                for platillo in restaurante["menu"]
            ]

            db.restaurantes.replace_one(
                {"_id": documento["_id"]},
                documento,
                upsert=True
            )

        # Insertar clientes
        for cliente_json in datos["clientes"]:
            documento = cliente_json.copy()

            documento["_id"] = ObjectId(
                cliente_json["_id"]
            )

            documento["fecha_registro"] = convertir_fecha(
                cliente_json["fecha_registro"]
            )

            db.clientes.replace_one(
                {"_id": documento["_id"]},
                documento,
                upsert=True
            )

        # Insertar pedidos
        for pedido in datos["pedidos"]:
            documento = pedido.copy()

            documento["_id"] = ObjectId(
                pedido["_id"]
            )

            documento["cliente_id"] = ObjectId(
                pedido["cliente_id"]
            )

            documento["restaurante_id"] = ObjectId(
                pedido["restaurante_id"]
            )

            documento["fecha"] = convertir_fecha(
                pedido["fecha"]
            )

            documento["items"] = [
                {
                    **item,
                    "platillo_id": ObjectId(
                        item["platillo_id"]
                    )
                }
                for item in pedido["items"]
            ]

            db.pedidos.replace_one(
                {"_id": documento["_id"]},
                documento,
                upsert=True
            )

        # Índices del modelo de MongoDB
        db.restaurantes.create_index("activo")
        db.restaurantes.create_index("menu.categoria")
        db.clientes.create_index("email")

        db.pedidos.create_index([
            ("restaurante_id", 1),
            ("fecha", 1)
        ])

        print("MongoDB poblado correctamente.")

    finally:
        if cliente is not None:
            cliente.close()


def preparar_cassandra(session):

    # Crear keyspace
    session.execute("""
        CREATE KEYSPACE IF NOT EXISTS restodb
        WITH replication = {
            'class': 'SimpleStrategy',
            'replication_factor': 1
        }
    """)

    session.set_keyspace("restodb")

    # Tabla 1: Pedidos por cliente
    session.execute("""
        CREATE TABLE IF NOT EXISTS pedidos_por_cliente (
            cliente_id uuid,
            fecha_pedido timestamp,
            pedido_id uuid,
            restaurante_id uuid,
            nombre_restaurante text,
            total decimal,
            estado text,
            PRIMARY KEY (
                cliente_id,
                fecha_pedido,
                pedido_id
            )
        ) WITH CLUSTERING ORDER BY (
            fecha_pedido DESC,
            pedido_id ASC
        )
    """)

    # Tabla 2: Pedidos por restaurante y fecha
    session.execute("""
        CREATE TABLE IF NOT EXISTS
        pedidos_por_restaurante_fecha (
            restaurante_id uuid,
            fecha_dia date,
            fecha_pedido timestamp,
            pedido_id uuid,
            cliente_id uuid,
            total decimal,
            estado text,
            PRIMARY KEY (
                (restaurante_id, fecha_dia),
                fecha_pedido,
                pedido_id
            )
        ) WITH CLUSTERING ORDER BY (
            fecha_pedido ASC,
            pedido_id ASC
        )
    """)

    # Tabla 3: Pedidos por restaurante y estado
    session.execute("""
        CREATE TABLE IF NOT EXISTS
        pedidos_por_restaurante_estado (
            restaurante_id uuid,
            fecha_dia date,
            estado text,
            fecha_pedido timestamp,
            pedido_id uuid,
            cliente_id uuid,
            total decimal,
            PRIMARY KEY (
                (restaurante_id, fecha_dia, estado),
                fecha_pedido,
                pedido_id
            )
        ) WITH CLUSTERING ORDER BY (
            fecha_pedido ASC,
            pedido_id ASC
        )
    """)

    # Tabla 4: Historial de cambios de estado
    session.execute("""
        CREATE TABLE IF NOT EXISTS historial_estados_pedido (
            pedido_id uuid,
            fecha_cambio timestamp,
            evento_id uuid,
            estado text,
            PRIMARY KEY (
                pedido_id,
                fecha_cambio,
                evento_id
            )
        ) WITH CLUSTERING ORDER BY (
            fecha_cambio ASC,
            evento_id ASC
        )
    """)

    # Tabla 5: Pedidos de cliente en restaurante
    session.execute("""
        CREATE TABLE IF NOT EXISTS
        pedidos_por_cliente_restaurante (
            cliente_id uuid,
            restaurante_id uuid,
            fecha_pedido timestamp,
            pedido_id uuid,
            total decimal,
            estado text,
            PRIMARY KEY (
                (cliente_id, restaurante_id),
                fecha_pedido,
                pedido_id
            )
        ) WITH CLUSTERING ORDER BY (
            fecha_pedido DESC,
            pedido_id ASC
        )
    """)

    # Tabla 6: Actividad por cliente
    session.execute("""
        CREATE TABLE IF NOT EXISTS actividad_por_cliente (
            cliente_id uuid,
            fecha_evento timestamp,
            evento_id uuid,
            tipo_evento text,
            descripcion text,
            PRIMARY KEY (
                cliente_id,
                fecha_evento,
                evento_id
            )
        ) WITH CLUSTERING ORDER BY (
            fecha_evento DESC,
            evento_id ASC
        )
    """)

    # Tabla 7: Actividad por fecha y tipo
    session.execute("""
        CREATE TABLE IF NOT EXISTS actividad_por_fecha_tipo (
            fecha_dia date,
            tipo_evento text,
            fecha_evento timestamp,
            evento_id uuid,
            cliente_id uuid,
            descripcion text,
            PRIMARY KEY (
                (fecha_dia, tipo_evento),
                fecha_evento,
                evento_id
            )
        ) WITH CLUSTERING ORDER BY (
            fecha_evento ASC,
            evento_id ASC
        )
    """)

    print("Las 7 tablas Cassandra están preparadas.")



def poblar_cassandra(datos):
    cluster = None

    try:
        cluster, session = connect_cassandra()
        preparar_cassandra(session)

        # Preparar las siete instrucciones INSERT
        consultas = {
            "cliente": session.prepare("""
                INSERT INTO pedidos_por_cliente (
                    cliente_id, fecha_pedido, pedido_id,
                    restaurante_id, nombre_restaurante,
                    total, estado
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """),

            "restaurante_fecha": session.prepare("""
                INSERT INTO pedidos_por_restaurante_fecha (
                    restaurante_id, fecha_dia, fecha_pedido,
                    pedido_id, cliente_id, total, estado
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """),

            "restaurante_estado": session.prepare("""
                INSERT INTO pedidos_por_restaurante_estado (
                    restaurante_id, fecha_dia, estado,
                    fecha_pedido, pedido_id, cliente_id, total
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """),

            "historial": session.prepare("""
                INSERT INTO historial_estados_pedido (
                    pedido_id, fecha_cambio, evento_id, estado
                ) VALUES (?, ?, ?, ?)
            """),

            "cliente_restaurante": session.prepare("""
                INSERT INTO pedidos_por_cliente_restaurante (
                    cliente_id, restaurante_id, fecha_pedido,
                    pedido_id, total, estado
                ) VALUES (?, ?, ?, ?, ?, ?)
            """),

            "actividad_cliente": session.prepare("""
                INSERT INTO actividad_por_cliente (
                    cliente_id, fecha_evento, evento_id,
                    tipo_evento, descripcion
                ) VALUES (?, ?, ?, ?, ?)
            """),

            "actividad_fecha": session.prepare("""
                INSERT INTO actividad_por_fecha_tipo (
                    fecha_dia, tipo_evento, fecha_evento,
                    evento_id, cliente_id, descripcion
                ) VALUES (?, ?, ?, ?, ?, ?)
            """)
        }

        for pedido in datos["pedidos"]:
            pedido_id = convertir_uuid(pedido["_id"])
            cliente_id = convertir_uuid(pedido["cliente_id"])
            restaurante_id = convertir_uuid(
                pedido["restaurante_id"]
            )

            fecha = convertir_fecha(pedido["fecha"])
            fecha_dia = fecha.date()

            total = Decimal(str(pedido["total"]))
            estado = pedido["estado"]

            # Tabla 1
            session.execute(consultas["cliente"], (
                cliente_id,
                fecha,
                pedido_id,
                restaurante_id,
                pedido["nombre_restaurante"],
                total,
                estado
            ))

            # Tabla 2
            session.execute(consultas["restaurante_fecha"], (
                restaurante_id,
                fecha_dia,
                fecha,
                pedido_id,
                cliente_id,
                total,
                estado
            ))

            # Tabla 3
            session.execute(consultas["restaurante_estado"], (
                restaurante_id,
                fecha_dia,
                estado,
                fecha,
                pedido_id,
                cliente_id,
                total
            ))

            # Tabla 5
            session.execute(consultas["cliente_restaurante"], (
                cliente_id,
                restaurante_id,
                fecha,
                pedido_id,
                total,
                estado
            ))

        print(
            f"Pedidos cargados en Cassandra: "
            f"{len(datos['pedidos'])}"
        )


        # CARGAR HISTORIAL DE ESTADOS

        for evento in datos["historial_estados"]:
            session.execute(consultas["historial"], (
                convertir_uuid(evento["pedido_id"]),
                convertir_fecha(evento["fecha_cambio"]),
                UUID(evento["evento_id"]),
                evento["estado"]
            ))

        print(
            f"Cambios de estado cargados: "
            f"{len(datos['historial_estados'])}"
        )


        # CARGAR ACTIVIDADES
 
        for actividad in datos["actividades"]:
            cliente_id = convertir_uuid(
                actividad["cliente_id"]
            )

            fecha = convertir_fecha(
                actividad["fecha_evento"]
            )

            evento_id = UUID(
                actividad["evento_id"]
            )

            tipo = actividad["tipo_evento"]
            descripcion = actividad["descripcion"]

            # Tabla 6
            session.execute(consultas["actividad_cliente"], (
                cliente_id,
                fecha,
                evento_id,
                tipo,
                descripcion
            ))

            # Tabla 7
            session.execute(consultas["actividad_fecha"], (
                fecha.date(),
                tipo,
                fecha,
                evento_id,
                cliente_id,
                descripcion
            ))

        print(
            f"Actividades cargadas en Cassandra: "
            f"{len(datos['actividades'])}"
        )

        print("Cassandra poblada correctamente.")

    finally:
        if cluster is not None:
            cluster.shutdown()



def poblar_dgraph(datos):
    # Pendiente de implementar junto con la conexión
    # y la carga de nodos y relaciones de Dgraph.
    print("Dgraph: carga pendiente de implementar.")


def main():
    parser = argparse.ArgumentParser(
        description="Carga de datos de RestoDB"
    )

    parser.add_argument(
        "--solo",
        choices=["mongodb", "cassandra"],
        help="Cargar únicamente la base de datos indicada"
    )

    args = parser.parse_args()

    print("=== INICIANDO CARGA DE DATOS ===")

    datos = leer_datos()

    if args.solo is None or args.solo == "mongodb":
        poblar_mongodb(datos)

    if args.solo is None or args.solo == "cassandra":
        poblar_cassandra(datos)

    if args.solo is None:
        poblar_dgraph(datos)

    print("=== PROCESO FINALIZADO ===")


if __name__ == "__main__":
    main()

