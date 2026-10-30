def main():
    print("\n===== RestoDB =====")
    print("Sistema de Gestion de Restaurantes y Pedidos")

    print("\n--- CASSANDRA ---")
    print("1. Consultar historial de pedidos de un cliente")
    print("2. Consultar pedidos de un cliente por rango de fechas")
    print("3. Consultar historial de pedidos de un restaurante")
    print("4. Consultar pedidos de un restaurante por estado")
    print("5. Consultar historial de cambios de estado de un pedido")
    print("6. Consultar pedidos de un cliente en un restaurante especifico")
    print("7. Consultar historial de actividad de un cliente")
    print("8. Consultar actividad de clientes por tipo de evento y fecha")

    print("\n--- MONGODB ---")
    print("9. Consultar restaurantes disponibles")
    print("10. Consultar menu de un restaurante")
    print("11. Buscar platillos por categoria y precio")
    print("12. Consultar clientes por nombre o correo electronico")
    print("13. Consultar los platillos mas caros de un restaurante")
    print("14. Consultar el total de ventas por restaurante")
    print("15. Consultar detalle de un pedido")
    print("16. Consultar los platillos mas vendidos")

    print("\n--- DGRAPH ---")
    print("17. Consultar platillos ofrecidos por un restaurante")
    print("18. Consultar restaurantes que ofrecen un platillo")
    print("19. Consultar platillos favoritos de un cliente")
    print("20. Consultar restaurantes favoritos de un cliente")
    print("21. Consultar restaurantes por tipo de comida preferida")
    print("22. Encontrar clientes con platillos favoritos en comun")
    print("23. Recomendar platillos segun preferencias similares")
    print("24. Recomendar restaurantes a partir de platillos favoritos")


if __name__ == "__main__":
    main()
