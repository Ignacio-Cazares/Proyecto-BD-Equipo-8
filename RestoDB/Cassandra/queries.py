from datetime import date, datetime, time, timedelta, timezone
from connect import connect_cassandra
from populate import convertir_uuid


def convertir_fecha(fecha):
    """
    Convierte una fecha en formato YYYY-MM-DD
    a un objeto date de Python.
    """
    if isinstance(fecha, datetime):
        return fecha.date()

    if isinstance(fecha, date):
        return fecha

    return date.fromisoformat(fecha)


def ejecutar_consulta(consulta_cql, parametros):
    """
    Conecta con Cassandra, ejecuta una consulta
    preparada y devuelve los resultados.
    """
    cluster = None

    try:
        cluster, session = connect_cassandra()
        session.set_keyspace("restodb")

        session.default_fetch_size = 100

        consulta = session.prepare(consulta_cql)

        resultados = session.execute(
            consulta,
            parametros
        )

        return list(resultados)

    finally:
        if cluster is not None:
            cluster.shutdown()


def consultar_historial_pedidos_cliente(cliente_id):
    consulta = """
        SELECT pedido_id,
               restaurante_id,
               nombre_restaurante,
               fecha_pedido,
               total,
               estado
        FROM pedidos_por_cliente
        WHERE cliente_id = ?
    """

    return ejecutar_consulta(
        consulta,
        (convertir_uuid(cliente_id),)
    )



def consultar_pedidos_cliente_rango_fechas(
    cliente_id, fecha_inicio, fecha_fin
):
    inicio = convertir_fecha(fecha_inicio)
    fin = convertir_fecha(fecha_fin)

    if inicio > fin:
        raise ValueError(
            "La fecha inicial no puede ser mayor "
            "que la fecha final."
        )

    # Inicio del primer día en UTC
    fecha_inicial = datetime.combine(
        inicio,
        time.min,
        tzinfo=timezone.utc
    )

    # Inicio del día posterior al último día
    fecha_final = datetime.combine(
        fin + timedelta(days=1),
        time.min,
        tzinfo=timezone.utc
    )

    consulta = """
        SELECT pedido_id,
               restaurante_id,
               nombre_restaurante,
               fecha_pedido,
               total,
               estado
        FROM pedidos_por_cliente
        WHERE cliente_id = ?
          AND fecha_pedido >= ?
          AND fecha_pedido < ?
    """

    resultados = ejecutar_consulta(
        consulta,
        (
            convertir_uuid(cliente_id),
            fecha_inicial,
            fecha_final
        )
    )

    # Orden cronológico ascendente
    return sorted(
        resultados,
        key=lambda pedido: (
            pedido.fecha_pedido,
            pedido.pedido_id
        )
    )


def consultar_historial_pedidos_restaurante(
    restaurante_id, fecha_dia
):
    consulta = """
        SELECT pedido_id,
               cliente_id,
               fecha_pedido,
               total,
               estado
        FROM pedidos_por_restaurante_fecha
        WHERE restaurante_id = ?
          AND fecha_dia = ?
    """

    return ejecutar_consulta(
        consulta,
        (
            convertir_uuid(restaurante_id),
            convertir_fecha(fecha_dia)
        )
    )


def consultar_pedidos_restaurante_por_estado(
    restaurante_id, fecha_dia, estado
):
    consulta = """
        SELECT pedido_id,
               cliente_id,
               fecha_pedido,
               total,
               estado
        FROM pedidos_por_restaurante_estado
        WHERE restaurante_id = ?
          AND fecha_dia = ?
          AND estado = ?
    """

    return ejecutar_consulta(
        consulta,
        (
            convertir_uuid(restaurante_id),
            convertir_fecha(fecha_dia),
            estado.strip().lower()
        )
    )


def consultar_historial_estados_pedido(pedido_id):
    consulta = """
        SELECT pedido_id,
               fecha_cambio,
               evento_id,
               estado
        FROM historial_estados_pedido
        WHERE pedido_id = ?
    """

    return ejecutar_consulta(
        consulta,
        (convertir_uuid(pedido_id),)
    )


def consultar_pedidos_cliente_restaurante(
    cliente_id, restaurante_id
):
    consulta = """
        SELECT pedido_id,
               fecha_pedido,
               total,
               estado
        FROM pedidos_por_cliente_restaurante
        WHERE cliente_id = ?
          AND restaurante_id = ?
    """

    return ejecutar_consulta(
        consulta,
        (
            convertir_uuid(cliente_id),
            convertir_uuid(restaurante_id)
        )
    )


def consultar_historial_actividad_cliente(cliente_id):
    consulta = """
        SELECT evento_id,
               fecha_evento,
               tipo_evento,
               descripcion
        FROM actividad_por_cliente
        WHERE cliente_id = ?
    """

    return ejecutar_consulta(
        consulta,
        (convertir_uuid(cliente_id),)
    )


def consultar_actividad_por_fecha_tipo(
    fecha_dia, tipo_evento
):
    consulta = """
        SELECT evento_id,
               cliente_id,
               fecha_evento,
               tipo_evento,
               descripcion
        FROM actividad_por_fecha_tipo
        WHERE fecha_dia = ?
          AND tipo_evento = ?
    """

    return ejecutar_consulta(
        consulta,
        (
            convertir_fecha(fecha_dia),
            tipo_evento.strip().lower()
        )
    )
