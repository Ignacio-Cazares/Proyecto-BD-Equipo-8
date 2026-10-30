# Este archivo se encargará de poblar las bases de datos
# MongoDB, Cassandra y Dgraph.
#
# Flujo planeado:
#
# 1. Establecer las conexiones utilizando connect.py.
#
# 2. Leer los archivos de prueba almacenados en data.
#
# 3. Cargar los restaurantes, clientes, menús y pedidos
#    en MongoDB.
#
# 4. Cargar los historiales de pedidos, cambios de estado
#    y actividades de clientes en Cassandra.
#
# 5. Cargar los nodos y relaciones entre clientes,
#    restaurantes, platillos y preferencias en Dgraph.
#
# 6. Verificar que los registros se hayan almacenado
#    correctamente en cada base de datos.
#
# 7. Mostrar un resumen de la carga realizada.
