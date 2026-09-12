# Laberinto (según tu imagen)
# 0=libre, 1=muro, 2=queso, 3=ducha, 9=meta
laberinto = [
    [0, 1, 3, 3, 3],   # fila 0 (inicio en (0,0))
    [0, 1, 3, 1, 3],   # fila 1
    [0, 0, 0, 1, 3],   # fila 2
    [1, 1, 2, 2, 0],   # fila 3
    [0, 0, 0, 1, 9]    # fila 4 (meta en (4,4))
]

# Estado inicial y meta
pos = [0, 0]
meta = (4, 4)
total_costo = 0

# Función de costo
def costo_celda(valor):
    if valor == 0:
        return 1
    elif valor == 2:
        return 2
    elif valor == 3:
        return 0.5
    elif valor == 9:
        return 0
    else:
        return float("inf")

# Imprimir tablero
def imprimir_tablero(lab, pos):
    for i in range(len(lab)):
        fila = []
        for j in range(len(lab[0])):
            if (i, j) == tuple(pos):
                fila.append(8)
            else:
                fila.append(lab[i][j])
        print(fila)
    print()

# Juego
print("Bienvenido al juego del laberinto 🐭🎮")
print("Controles: w=arriba, s=abajo, a=izquierda, d=derecha")
imprimir_tablero(laberinto, pos)

while True:
    mov = input("Ingresa tu movimiento (w/a/s/d): ").strip().lower()
    if mov not in ["w", "a", "s", "d"]:
        print("Movimiento inválido.")
        continue

    # Calcular nueva posición
    nueva_pos = pos.copy()
    if mov == "w":
        nueva_pos[0] -= 1
    elif mov == "s":
        nueva_pos[0] += 1
    elif mov == "a":
        nueva_pos[1] -= 1
    elif mov == "d":
        nueva_pos[1] += 1

    # Validar movimiento
    x, y = nueva_pos
    if not (0 <= x < len(laberinto) and 0 <= y < len(laberinto[0])):
        print("No puedes salirte del tablero ❌")
        continue
    if laberinto[x][y] == 1:
        print("Choque con un muro 🚧")
        continue

    # Actualizar posición y costo
    pos = nueva_pos
    total_costo += costo_celda(laberinto[x][y])

    imprimir_tablero(laberinto, pos)

    # Verificar meta
    if tuple(pos) == meta:
        print("🎉 ¡Has llegado a la meta!")
        print(f"✅ Total de puntos consumidos: {total_costo}")
        break