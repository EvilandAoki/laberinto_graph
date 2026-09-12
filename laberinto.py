# =============================================================================
# LABERINTO CON GRAFOS — Actividad Final IA
# =============================================================================
#
# Basado en el modelo de representación de problemas para agentes:
#
#   ESTADO       → posición actual del jugador en el tablero (fila, columna)
#   OPERADORES   → movimientos válidos: arriba / abajo / izquierda / derecha
#   PRUEBA META  → ¿está el jugador en la celda meta?
#   COSTO RUTA   → coins consumidos a lo largo del camino recorrido
#
# =============================================================================

import os

try:
    import colorama
    from colorama import Fore, Style
    colorama.init(autoreset=True)
    COLOR = True
except ImportError:
    COLOR = False

# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN 1 — REPRESENTACIÓN DEL ENTORNO
# ─────────────────────────────────────────────────────────────────────────────
#
# El laberinto se representa como una lista 2D (matriz 9×9).
# Codificación de celdas:
#   0 = libre      → costo base (1 coin)
#   1 = muro       → bloqueado, sin aristas en el grafo
#   2 = penalti    → costo × 3  (triple de coins)
#   3 = premio     → costo ÷ 4  (cuarta parte de coins)
#   8 = inicio     → costo 0
#   9 = meta       → costo 0

LABERINTO = [
    [8, 0, 0, 1, 0, 0, 0, 0, 0],   # fila 0
    [0, 2, 0, 1, 0, 3, 0, 0, 0],   # fila 1
    [0, 0, 0, 0, 0, 0, 1, 0, 0],   # fila 2
    [1, 1, 0, 1, 1, 0, 1, 0, 0],   # fila 3
    [0, 0, 0, 0, 0, 0, 0, 0, 1],   # fila 4
    [0, 1, 1, 1, 0, 1, 1, 0, 0],   # fila 5
    [0, 0, 0, 0, 0, 0, 0, 1, 0],   # fila 6
    [0, 1, 2, 0, 1, 0, 0, 0, 0],   # fila 7
    [0, 0, 0, 0, 0, 3, 0, 0, 9],   # fila 8
]

N              = 9          # dimensión del laberinto
INICIO         = (0, 0)     # posición inicial del jugador
META           = (8, 8)     # posición de la meta
COSTO_BASE     = 1          # coins que cuesta moverse a una celda libre
COINS_INICIALES = 30        # coins con los que comienza el jugador


def costo_celda(valor: int) -> float:
    """Retorna el costo en coins de entrar a una celda según su tipo."""
    if valor in (0, 8):   return COSTO_BASE          # libre / inicio
    if valor == 2:        return COSTO_BASE * 3       # penalti  (×3)
    if valor == 3:        return COSTO_BASE / 4       # premio   (÷4)
    if valor == 9:        return 0                    # meta
    return float("inf")                               # muro (nunca se llega)


def construir_grafo(lab: list) -> dict:
    """
    Construye el grafo del laberinto como diccionario de adyacencia.

    grafo[(r, c)] = [(vecino, costo), ...]

    - Cada celda transitable (valor != 1) es un NODO.
    - Dos nodos adyacentes (↑↓←→) se conectan con una ARISTA.
    - El PESO de la arista es el costo de entrar a la celda destino.
    """
    grafo = {}
    for r in range(N):
        for c in range(N):
            if lab[r][c] == 1:
                continue                          # los muros no son nodos
            nodo = (r, c)
            grafo[nodo] = []
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < N and 0 <= nc < N and lab[nr][nc] != 1:
                    grafo[nodo].append(((nr, nc), costo_celda(lab[nr][nc])))
    return grafo


# Grafo global construido una sola vez al iniciar
GRAFO = construir_grafo(LABERINTO)


# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN 2 — MODELO DEL AGENTE
# ─────────────────────────────────────────────────────────────────────────────

# ESTADO: posición del jugador como tupla (fila, columna)
estado_inicial = INICIO

# OPERADORES: tecla → delta de movimiento (dr, dc)
OPERADORES = {
    "w": (-1,  0),   # arriba
    "s": ( 1,  0),   # abajo
    "a": ( 0, -1),   # izquierda
    "d": ( 0,  1),   # derecha
}

NOMBRES_MOV = {"w": "↑ arriba", "s": "↓ abajo", "a": "← izquierda", "d": "→ derecha"}


def prueba_meta(estado: tuple) -> bool:
    """PRUEBA DE META: retorna True si el agente ha llegado a la casilla final."""
    return estado == META


def transicion(estado: tuple, operador: str, lab: list):
    """
    Función de transición del agente.
    Dado un estado y un operador, retorna (nuevo_estado, error).
    Si el movimiento es inválido, nuevo_estado=None y error describe el motivo.
    """
    r, c = estado
    dr, dc = OPERADORES[operador]
    nr, nc = r + dr, c + dc

    if not (0 <= nr < N and 0 <= nc < N):
        return None, "No puedes salirte del tablero 🚧"
    if lab[nr][nc] == 1:
        return None, "Choque con un muro 🚧"
    return (nr, nc), None


# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN 3 — VISUALIZACIÓN ASCII
# ─────────────────────────────────────────────────────────────────────────────

def c(texto: str, color: str) -> str:
    """Aplica color si colorama está disponible, sino devuelve texto plano."""
    return f"{color}{texto}{Style.RESET_ALL}" if COLOR else texto


# Paleta de colores por valor de celda
COLORES = {
    8: Fore.GREEN  + Style.BRIGHT if COLOR else "",   # inicio   S
    9: Fore.YELLOW + Style.BRIGHT if COLOR else "",   # meta     G
    1: Fore.BLACK  + Style.BRIGHT if COLOR else "",   # muro     █
    2: Fore.RED    + Style.BRIGHT if COLOR else "",   # penalti  P
    3: Fore.CYAN   + Style.BRIGHT if COLOR else "",   # premio   R
    0: Fore.WHITE                 if COLOR else "",   # libre    ·
}
SIMBOLOS = {8: "S", 9: "G", 1: "█", 2: "P", 3: "R", 0: "·"}


def mostrar_tablero(lab: list, estado: tuple, coins: float) -> None:
    """Imprime el laberinto con colores, posición del jugador y saldo de coins."""
    if COLOR:
        coins_color = (Fore.GREEN + Style.BRIGHT if coins > 20
                       else Fore.YELLOW + Style.BRIGHT if coins > 10
                       else Fore.RED + Style.BRIGHT)
    else:
        coins_color = ""

    print(f"\n  Coins: {c(f'{coins:.2f}', coins_color)}   "
          f"Posición: {estado}   Meta: {META}")
    print("  " + "─" * (N * 3 + 2))

    # Cabecera de columnas
    print("    " + "  ".join(c(str(col), Fore.WHITE + Style.DIM if COLOR else "") for col in range(N)))

    for r in range(N):
        fila = c(f" {r}│", Fore.WHITE + Style.DIM if COLOR else "")
        for col in range(N):
            pos = (r, col)
            val = lab[r][col]
            if pos == estado:
                fila += c(" @ ", Fore.MAGENTA + Style.BRIGHT if COLOR else "")
            else:
                fila += c(f" {SIMBOLOS[val]} ", COLORES[val])
        print(fila)

    print("  " + "─" * (N * 3 + 2))


def mostrar_leyenda() -> None:
    items = [
        ("@", Fore.MAGENTA + Style.BRIGHT if COLOR else "", "Jugador"),
        ("S", Fore.GREEN   + Style.BRIGHT if COLOR else "", "Inicio       (0 coins)"),
        ("G", Fore.YELLOW  + Style.BRIGHT if COLOR else "", "Meta         (0 coins)"),
        ("█", Fore.BLACK   + Style.BRIGHT if COLOR else "", "Muro         (bloqueado)"),
        ("P", Fore.RED     + Style.BRIGHT if COLOR else "", f"Penalti      (×3 = {COSTO_BASE*3} coins)"),
        ("R", Fore.CYAN    + Style.BRIGHT if COLOR else "", f"Premio       (÷4 = {COSTO_BASE/4} coins)"),
        ("·", Fore.WHITE               if COLOR else "", f"Libre        ({COSTO_BASE} coin)"),
    ]
    print("  Leyenda:")
    for sym, col, desc in items:
        print(f"    {c(sym, col)}  {desc}")


def mostrar_grafo() -> None:
    """Muestra el grafo de adyacencia del laberinto."""
    nodos = len(GRAFO)
    aristas = sum(len(v) for v in GRAFO.values()) // 2
    print(f"\n  Grafo del laberinto:")
    print(f"  · Nodos  (celdas transitables) : {nodos}")
    print(f"  · Aristas (conexiones ↑↓←→)    : {aristas}")
    print(f"  · Inicio : {INICIO}   Meta : {META}\n")
    print("  Adyacencia (primeros 10 nodos):")
    for i, (nodo, vecinos) in enumerate(GRAFO.items()):
        if i >= 10:
            print("    ...")
            break
        vstr = ", ".join(f"{v}(c={co:.2f})" for v, co in vecinos)
        print(f"    {nodo} → [{vstr}]")


# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN 4 — LÓGICA DE JUEGO E HISTORIAL
# ─────────────────────────────────────────────────────────────────────────────

historial: list[tuple[str, float, int]] = []
# Cada entrada: ("ganó"|"perdió"|"abandonó", coins_restantes, pasos)


def mostrar_historial() -> None:
    print(c("\n  ╔══ Historial de Partidas ═══════════════════╗", Fore.CYAN + Style.BRIGHT if COLOR else ""))
    if not historial:
        print("  ║  (sin partidas registradas aún)            ║")
        print(c("  ╚═══════════════════════════════════════════╝", Fore.CYAN + Style.BRIGHT if COLOR else ""))
        return

    print(f"  ║  {'#':<4} {'Resultado':<10} {'Coins':<10} {'Pasos'}")
    print(f"  ║  {'─'*4} {'─'*10} {'─'*10} {'─'*5}")
    for i, (resultado, coins, pasos) in enumerate(historial, 1):
        col = (Fore.GREEN + Style.BRIGHT if resultado == "ganó"
               else Fore.RED + Style.BRIGHT if resultado == "perdió"
               else Fore.YELLOW if COLOR else "")
        print(f"  ║  {i:<4} {c(resultado, col):<10} {coins:<10.2f} {pasos}")

    ganadores = [(coins, p) for res, coins, p in historial if res == "ganó"]
    if ganadores:
        mejor_coins = max(ganadores, key=lambda x: x[0])
        print(f"  ║")
        print(f"  ║  🏆 {c(f'Mejor partida: {mejor_coins[0]:.2f} coins en {mejor_coins[1]} pasos', Fore.YELLOW + Style.BRIGHT if COLOR else '')}")

    print(c("  ╚═══════════════════════════════════════════╝", Fore.CYAN + Style.BRIGHT if COLOR else ""))


def jugar() -> None:
    """Loop principal de una partida."""
    # Estado inicial del agente
    estado = estado_inicial
    coins  = float(COINS_INICIALES)
    ruta   = [estado]          # costo de ruta acumulado en camino
    pasos  = 0

    os.system("cls" if os.name == "nt" else "clear")
    print(c("\n  ╔══ LABERINTO CON GRAFOS ═══════════════════╗", Fore.CYAN + Style.BRIGHT if COLOR else ""))
    print(c("  ║  Modelado con Grafos — Actividad Final IA ║", Fore.CYAN + Style.BRIGHT if COLOR else ""))
    print(c("  ╚═══════════════════════════════════════════╝", Fore.CYAN + Style.BRIGHT if COLOR else ""))
    print(f"\n  Coins iniciales: {c(str(COINS_INICIALES), Fore.GREEN + Style.BRIGHT if COLOR else '')}")
    print("  Controles: w=↑  s=↓  a=←  d=→  |  g=ver grafo  r=reiniciar  q=salir")
    print()
    mostrar_leyenda()
    mostrar_tablero(LABERINTO, estado, coins)

    while True:
        mov = input("\n  Movimiento > ").strip().lower()

        # Comandos de utilidad
        if mov == "q":
            historial.append(("abandonó", coins, pasos))
            print(c("  Partida abandonada.", Fore.YELLOW if COLOR else ""))
            input("  Presiona Enter para continuar...")
            return
        if mov == "r":
            jugar()
            return
        if mov == "g":
            mostrar_grafo()
            continue
        if mov not in OPERADORES:
            print(c("  Entrada inválida. Usa w/a/s/d.", Fore.YELLOW if COLOR else ""))
            continue

        # ── Aplicar operador: transición de estado ──────────────────────────
        nuevo_estado, error = transicion(estado, mov, LABERINTO)

        if error:
            print(c(f"  ❌ {error}", Fore.RED if COLOR else ""))
            continue

        # ── Calcular costo de ruta ───────────────────────────────────────────
        r, col_idx = nuevo_estado
        costo = costo_celda(LABERINTO[r][col_idx])
        coins -= costo
        estado = nuevo_estado
        ruta.append(estado)
        pasos += 1

        # Feedback de celda especial
        val = LABERINTO[r][col_idx]
        if val == 2:
            print(c(f"  ⚠️  Celda PENALTI {estado} — costó {costo:.2f} coins (×3)", Fore.RED if COLOR else ""))
        elif val == 3:
            print(c(f"  🎁 Celda PREMIO {estado} — costó {costo:.2f} coins (÷4)", Fore.CYAN if COLOR else ""))

        # ── Verificar derrota (coins ≤ 0) ───────────────────────────────────
        if coins <= 0:
            mostrar_tablero(LABERINTO, estado, 0)
            print(c("\n  💀 ¡Sin coins! Perdiste el juego.", Fore.RED + Style.BRIGHT if COLOR else ""))
            print(f"  Pasos: {pasos}  |  Ruta: {' → '.join(str(p) for p in ruta)}")
            historial.append(("perdió", 0, pasos))
            input("\n  Presiona Enter para continuar...")
            return

        mostrar_tablero(LABERINTO, estado, coins)

        # ── Prueba de meta ───────────────────────────────────────────────────
        if prueba_meta(estado):
            print(c(f"\n  🏆 ¡META ALCANZADA! Coins restantes: {coins:.2f}", Fore.YELLOW + Style.BRIGHT if COLOR else ""))
            print(f"  Pasos: {pasos}  |  Ruta: {' → '.join(str(p) for p in ruta)}")
            historial.append(("ganó", coins, pasos))
            input("\n  Presiona Enter para continuar...")
            return


# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN 5 — MENÚ PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

def menu() -> None:
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print(c("\n  ╔══ LABERINTO CON GRAFOS ═══════════════════╗", Fore.CYAN + Style.BRIGHT if COLOR else ""))
        print(c("  ║  Modelado con Grafos — Actividad Final IA ║", Fore.CYAN + Style.BRIGHT if COLOR else ""))
        print(c("  ╚═══════════════════════════════════════════╝\n", Fore.CYAN + Style.BRIGHT if COLOR else ""))
        print(c("  [1]", Fore.GREEN if COLOR else "") + "  🕹️  Jugar")
        print(c("  [2]", Fore.GREEN if COLOR else "") + "  📊  Ver grafo de adyacencia")
        print(c("  [3]", Fore.GREEN if COLOR else "") + "  🏅  Ver historial de partidas")
        print(c("  [0]", Fore.GREEN if COLOR else "") + "  🚪  Salir\n")

        elec = input("  Opción > ").strip()

        if elec == "1":
            jugar()
        elif elec == "2":
            os.system("cls" if os.name == "nt" else "clear")
            mostrar_grafo()
            input("\n  Presiona Enter para continuar...")
        elif elec == "3":
            os.system("cls" if os.name == "nt" else "clear")
            mostrar_historial()
            input("\n  Presiona Enter para continuar...")
        elif elec == "0":
            print(c("\n  ¡Hasta luego! 👋\n", Fore.CYAN + Style.BRIGHT if COLOR else ""))
            break


if __name__ == "__main__":
    menu()
