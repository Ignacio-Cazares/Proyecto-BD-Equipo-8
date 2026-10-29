# Proyecto-BD-Equipo-8

## Integrantes
1. José Ignacio Cázares Bocanegra
2. Brandon Adrián Becerra Gómez
3. Agustin Gradilla

## Descripción del proyecto
Este proyecto consiste en desarrollar un Sistema de Gestión de Restaurantes y Pedidos que permita consultar información sobre restaurantes, menús, clientes y pedidos, así como consultar historiales de actividad y generar recomendaciones basadas en las preferencias de los clientes.

Para su desarrollo se utilizarán tres bases de datos NoSQL: MongoDB, para almacenar y consultar la información de restaurantes, clientes y pedidos; Cassandra, para gestionar los historiales de pedidos y actividades; y Dgraph, para representar las relaciones entre clientes, restaurantes y platillos.

## Flujo de trabajo
1. Preparación: iniciar los servicios de MongoDB, Cassandra y Dgraph y establecer las conexiones mediante connect.py.
2. Carga de datos: ejecutar populate.py, que leerá los archivos de la carpeta data/ y cargará la información en las tres bases de datos.
3. Ejecución del sistema: iniciar main.py para acceder al menú principal.
4. Selección de consultas: elegir alguna consulta del menú principal.
5. Visualización de resultados: se devolverá la información de manera limpia y ordenada. 
