# Laberinto definido manualmente
# 0 = libre
# 1 = muro
# 2 = penalización (triplica costo)
# 3 = premio (cuesta 1/4)
# 9 = meta

laberinto = [
    [0, 0, 0, 0, 0, 0, 0, 1, 0],  # fila 0
    [0, 1, 1, 1, 0, 1, 0, 1, 0],  # fila 1
    [0, 0, 0, 1, 0, 1, 0, 0, 0],  # fila 2
    [1, 1, 0, 0, 0, 1, 1, 1, 0],  # fila 3
    [0, 0, 0, 1, 0, 0, 0, 1, 0],  # fila 4
    [0, 1, 0, 1, 0, 1, 0, 1, 0],  # fila 5
    [0, 1, 0, 0, 0, 1, 0, 0, 3],  # fila 6 (con premio en (6,8))
    [0, 1, 1, 1, 0, 0, 0, 1, 0],  # fila 7
    [0, 0, 0, 0, 0, 1, 0, 2, 9]   # fila 8 (penalización en (8,7), meta en (8,8))
]

N = len(laberinto)

# Jugador inicial
pos = [0, 0]
coins = 30  # cantidad inicial de monedas

# Función de costo
def costo_celda(valor):
    if valor == 0:  # libre
        return 1
    elif valor == 2:  # penalización
        return 3
    elif valor == 3:  # premio
        return 0.25
    elif valor == 9:  # meta
        return 0
    else:  # muro
        return float("inf")

# Imprimir tablero
def imprimir_tablero(lab, pos, coins):
    print(f"\nMonedas actuales: {coins}")
    for i in range(len(lab)):
        fila = []
        for j in range(len(lab[0])):
            if (i, j) == tuple(pos):
                fila.append(8)
            else:
                fila.append(lab[i][j])
        print(fila)
    print()

# --- Juego ---
print("🐭 Bienvenido al laberinto de 9x9 🎮")
print("Reglas:")
print("- w = arriba, s = abajo, a = izquierda, d = derecha")
print("- Celdas normales cuestan 1 coin")
print("- Celda penalización (2) cuesta 3 coins")
print("- Celda premio (3) cuesta 0.25 coins")
print("- Si llegas a 0 coins pierdes ❌")
print("- Llega a la meta (9) para ganar 🎉")

imprimir_tablero(laberinto, pos, coins)

while True:
    mov = input("Ingresa tu movimiento (w/a/s/d): ").strip().lower()
    if mov not in ["w","a","s","d"]:
        print("Movimiento inválido ❌")
        continue

    nueva_pos = pos.copy()
    if mov == "w":
        nueva_pos[0] -= 1
    elif mov == "s":
        nueva_pos[0] += 1
    elif mov == "a":
        nueva_pos[1] -= 1
    elif mov == "d":
        nueva_pos[1] += 1

    x, y = nueva_pos

    # Validación
    if not (0 <= x < N and 0 <= y < N):
        print("No puedes salirte del tablero 🚧")
        continue
    if laberinto[x][y] == 1:
        print("Choque con un muro 🚧")
        continue

    # Movimiento válido
    costo = costo_celda(laberinto[x][y])
    coins -= costo
    if coins < 0:
        print("❌ Te quedaste sin coins. ¡Perdiste el juego!")
        break

    pos = nueva_pos
    imprimir_tablero(laberinto, pos, coins)

    # Verificar meta
    if laberinto[x][y] == 9:
        print("🎉 ¡Has llegado a la meta!")
        print(f"✅ Coins restantes: {coins}")
        break