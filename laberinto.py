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
# Entrega 2: se agregan dos algoritmos de búsqueda no informada sobre el
# grafo del laberinto (SECCIÓN 3):
#   BFS → búsqueda por amplitud   (frontera = cola)
#   DFS → búsqueda por profundidad (frontera = pila)
#
# =============================================================================

import os
from collections import deque

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
# SECCIÓN 3 — ALGORITMOS DE BÚSQUEDA (BFS / DFS)
# ─────────────────────────────────────────────────────────────────────────────
#
# Búsqueda NO informada sobre el grafo de adyacencia de la SECCIÓN 1.
# Los dos algoritmos comparten la misma estructura vista en clase:
#
#   frontera    → nodos pendientes de explorar (COLA en BFS, PILA en DFS)
#   visitados   → nodos ya descubiertos (evita ciclos y repeticiones)
#   predecesor  → desde qué nodo se descubrió cada nodo (reconstruye el camino)
#
# La ÚNICA diferencia es qué nodo se saca de la frontera en cada iteración:
#   BFS → el primero que entró  (FIFO)  → explora por niveles, en "anillos"
#   DFS → el último que entró   (LIFO)  → se mete por una rama hasta el fondo
#
# Ninguno usa el peso de las aristas (coins): buscan un camino en PASOS.
#   · BFS garantiza el camino con MENOS PASOS.
#   · DFS garantiza ENCONTRAR un camino si existe, pero no que sea el más corto.

def reconstruir_camino(predecesor: dict, nodo) -> list:
    """Sigue la cadena de predecesores desde `nodo` hasta el inicio y la invierte."""
    camino = []
    while nodo is not None:
        camino.append(nodo)
        nodo = predecesor[nodo]
    return list(reversed(camino))


def bfs_camino(grafo: dict, inicio, objetivo):
    """
    BÚSQUEDA POR AMPLITUD (Breadth-First Search).

    Explora el grafo por niveles: primero los nodos a 1 paso del inicio,
    luego los que están a 2 pasos, y así sucesivamente.
    La frontera es una COLA (FIFO): se saca siempre el nodo más antiguo.

    `grafo` tiene el formato de construir_grafo: grafo[nodo] = [(vecino, costo), ...]

    Retorna (camino, explorados):
      camino     → lista de nodos desde `inicio` hasta `objetivo`, o None si no hay
      explorados → nodos sacados de la frontera, en orden (sirve para visualizar)
    """
    cola       = deque([inicio])      # frontera FIFO (igual que lista + pop(0), pero O(1))
    visitados  = {inicio}
    predecesor = {inicio: None}
    explorados = []

    while cola:
        nodo = cola.popleft()         # ← saca el PRIMERO que entró
        explorados.append(nodo)

        if nodo == objetivo:
            return reconstruir_camino(predecesor, nodo), explorados

        for vecino, _costo in grafo[nodo]:
            if vecino not in visitados:
                visitados.add(vecino)
                predecesor[vecino] = nodo
                cola.append(vecino)

    return None, explorados


def dfs_camino(grafo: dict, inicio, objetivo):
    """
    BÚSQUEDA POR PROFUNDIDAD (Depth-First Search).

    Avanza por una rama hasta donde pueda y solo retrocede cuando se queda
    sin vecinos nuevos. La frontera es una PILA (LIFO): se saca siempre el
    último nodo agregado.

    Retorna (camino, explorados) con el mismo formato que `bfs_camino`.
    """
    pila       = [inicio]             # frontera LIFO
    visitados  = {inicio}
    predecesor = {inicio: None}
    explorados = []

    while pila:
        nodo = pila.pop()             # ← saca el ÚLTIMO que entró
        explorados.append(nodo)

        if nodo == objetivo:
            return reconstruir_camino(predecesor, nodo), explorados

        for vecino, _costo in grafo[nodo]:
            if vecino not in visitados:
                visitados.add(vecino)
                predecesor[vecino] = nodo
                pila.append(vecino)

    return None, explorados


# Registro de algoritmos disponibles: clave → (nombre para mostrar, función)
ALGORITMOS = {
    "bfs": ("Búsqueda por amplitud (BFS)",    bfs_camino),
    "dfs": ("Búsqueda por profundidad (DFS)", dfs_camino),
}


def costo_camino(camino: list, lab: list) -> float:
    """
    Coins que consume recorrer `camino`.
    Igual que en el juego: se paga el costo de cada celda a la que se ENTRA,
    por eso se omite la primera (donde ya estamos).
    """
    return sum(costo_celda(lab[r][col]) for r, col in camino[1:])


def resolver(metodo: str, inicio=INICIO, objetivo=META,
             coins: float = COINS_INICIALES, grafo: dict = None, lab: list = None) -> dict:
    """
    Ejecuta el algoritmo `metodo` ('bfs' | 'dfs') y resume el resultado:
    camino, pasos, costo en coins, coins restantes y nodos explorados.
    """
    grafo = GRAFO if grafo is None else grafo
    lab   = LABERINTO if lab is None else lab

    _, funcion = ALGORITMOS[metodo]
    camino, explorados = funcion(grafo, inicio, objetivo)

    costo = costo_camino(camino, lab) if camino else None
    return {
        "metodo":          metodo,
        "inicio":          inicio,
        "objetivo":        objetivo,
        "coins":           coins,
        "camino":          camino,
        "pasos":           len(camino) - 1 if camino else None,
        "costo":           costo,
        "coins_restantes": coins - costo if camino else None,
        "explorados":      explorados,
    }


# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN 4 — VISUALIZACIÓN ASCII
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


def mostrar_tablero_solucion(lab: list, camino: list, explorados: list = None,
                             jugador: tuple = None) -> None:
    """
    Imprime el laberinto marcando el resultado de una búsqueda:
      *  celda que forma parte del camino encontrado
      ○  celda explorada por el algoritmo pero descartada
      @  posición del jugador (opcional)
    Inicio (S) y meta (G) se muestran siempre con su símbolo.
    """
    en_camino  = set(camino)
    descartado = set(explorados or []) - en_camino

    print()
    print("  " + "─" * (N * 3 + 2))
    print("    " + "  ".join(c(str(col), Fore.WHITE + Style.DIM if COLOR else "") for col in range(N)))

    for r in range(N):
        fila = c(f" {r}│", Fore.WHITE + Style.DIM if COLOR else "")
        for col in range(N):
            pos = (r, col)
            val = lab[r][col]
            if jugador is not None and pos == jugador:
                fila += c(" @ ", Fore.MAGENTA + Style.BRIGHT if COLOR else "")
            elif val in (8, 9):
                fila += c(f" {SIMBOLOS[val]} ", COLORES[val])
            elif pos in en_camino:
                fila += c(" * ", Fore.MAGENTA + Style.BRIGHT if COLOR else "")
            elif pos in descartado:
                fila += c(" ○ ", Fore.WHITE + Style.DIM if COLOR else "")
            else:
                fila += c(f" {SIMBOLOS[val]} ", COLORES[val])
        print(fila)

    print("  " + "─" * (N * 3 + 2))
    print("  " + c("*", Fore.MAGENTA + Style.BRIGHT if COLOR else "") + " camino encontrado   "
          + c("○", Fore.WHITE + Style.DIM if COLOR else "") + " explorado y descartado")


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
# SECCIÓN 5 — LÓGICA DE JUEGO E HISTORIAL
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
    print("  Controles: w=↑  s=↓  a=←  d=→  |  b=pista BFS  p=pista DFS  g=ver grafo  r=reiniciar  q=salir")
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
        if mov in ("b", "p"):
            # Pista: resolver desde la posición actual con BFS (b) o DFS (p)
            metodo = "bfs" if mov == "b" else "dfs"
            mostrar_resultado_busqueda(resolver(metodo, inicio=estado, coins=coins), jugador=estado)
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


def mostrar_resultado_busqueda(res: dict, jugador: tuple = None) -> None:
    """Muestra el tablero con el camino encontrado y un resumen de la búsqueda."""
    nombre, _ = ALGORITMOS[res["metodo"]]
    print(c(f"\n  ══ {nombre} ══", Fore.CYAN + Style.BRIGHT if COLOR else ""))
    print(f"  Inicio: {res['inicio']}   Objetivo: {res['objetivo']}")

    if res["camino"] is None:
        print(c("\n  ❌ No existe ningún camino hasta el objetivo.", Fore.RED if COLOR else ""))
        print(f"  Nodos explorados : {len(res['explorados'])} de {len(GRAFO)}")
        return

    mostrar_tablero_solucion(LABERINTO, res["camino"], res["explorados"], jugador)

    especiales = [(p, LABERINTO[p[0]][p[1]]) for p in res["camino"][1:]
                  if LABERINTO[p[0]][p[1]] in (2, 3)]
    especiales_str = ", ".join(f"{'P' if v == 2 else 'R'}{p}" for p, v in especiales) or "ninguna"

    if res["coins_restantes"] > 0:
        veredicto = c("llega a la meta con coins ✅", Fore.GREEN + Style.BRIGHT if COLOR else "")
    else:
        veredicto = c("se queda sin coins antes de llegar 💀", Fore.RED + Style.BRIGHT if COLOR else "")

    print(f"\n  Pasos             : {res['pasos']}")
    print(f"  Coins gastados    : {res['costo']:.2f}")
    print(f"  Coins restantes   : {res['coins_restantes']:.2f}  (partiendo de {res['coins']:.2f})")
    print(f"  Nodos explorados  : {len(res['explorados'])} de {len(GRAFO)}")
    print(f"  Celdas especiales : {especiales_str}")
    print(f"  Resultado         : {veredicto}")
    print(f"  Ruta: {' → '.join(str(p) for p in res['camino'])}")


def comparar_busquedas(inicio=INICIO, objetivo=META) -> None:
    """Ejecuta BFS y DFS sobre el mismo laberinto y compara sus resultados."""
    print(c("\n  ══ Comparación BFS vs DFS ══", Fore.CYAN + Style.BRIGHT if COLOR else ""))
    print(f"  Inicio: {inicio}   Objetivo: {objetivo}   Coins iniciales: {COINS_INICIALES}\n")

    resultados = [resolver(m, inicio, objetivo) for m in ALGORITMOS]

    print(f"  {'Método':<32}{'Pasos':>7}{'Coins gast.':>13}{'Coins rest.':>13}{'Explorados':>12}")
    print(f"  {'─' * 32}{'─' * 7}{'─' * 13}{'─' * 13}{'─' * 12}")
    for res in resultados:
        nombre = ALGORITMOS[res["metodo"]][0]
        if res["camino"] is None:
            print(f"  {nombre:<32}{'—':>7}{'—':>13}{'—':>13}{len(res['explorados']):>12}")
        else:
            print(f"  {nombre:<32}{res['pasos']:>7}{res['costo']:>13.2f}"
                  f"{res['coins_restantes']:>13.2f}{len(res['explorados']):>12}")

    con_camino = [r for r in resultados if r["camino"]]
    if len(con_camino) == 2:
        bfs, dfs = con_camino
        print()
        if bfs["pasos"] < dfs["pasos"]:
            print(f"  · BFS encontró el camino más corto: {bfs['pasos']} pasos vs {dfs['pasos']} de DFS.")
        else:
            print(f"  · Ambos llegan en {bfs['pasos']} pasos. En DFS es casualidad: no está garantizado.")

        if bfs["costo"] == dfs["costo"]:
            print(f"  · Ambos gastan los mismos coins ({bfs['costo']:.2f}).")
        else:
            barato = min(con_camino, key=lambda r: r["costo"])
            caro   = max(con_camino, key=lambda r: r["costo"])
            print(f"  · {ALGORITMOS[barato['metodo']][0]} gasta menos coins "
                  f"({barato['costo']:.2f} vs {caro['costo']:.2f}). Ninguno optimiza coins: "
                  f"depende del camino que les tocó.")

        menos = min(con_camino, key=lambda r: len(r["explorados"]))
        mas   = max(con_camino, key=lambda r: len(r["explorados"]))
        if len(menos["explorados"]) == len(mas["explorados"]):
            print(f"  · Ambos exploraron {len(menos['explorados'])} nodos.")
        else:
            print(f"  · {ALGORITMOS[menos['metodo']][0]} exploró menos nodos "
                  f"({len(menos['explorados'])} vs {len(mas['explorados'])}).")

    for res in con_camino:
        print(c(f"\n  {ALGORITMOS[res['metodo']][0]}", Fore.CYAN if COLOR else ""))
        mostrar_tablero_solucion(LABERINTO, res["camino"], res["explorados"])


# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN 6 — MENÚ PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

def pedir_celda_inicio() -> tuple:
    """Pide una celda 'fila,columna' desde donde buscar. Enter = INICIO."""
    while True:
        txt = input(f"  Celda de inicio fila,columna [Enter = {INICIO}] > ").strip()
        if not txt:
            return INICIO
        try:
            r, col = (int(x) for x in txt.replace("(", "").replace(")", "").split(","))
        except ValueError:
            print(c("  Formato inválido. Ejemplo: 4,4", Fore.YELLOW if COLOR else ""))
            continue
        if (r, col) not in GRAFO:
            print(c(f"  {(r, col)} no es una celda transitable del laberinto.", Fore.YELLOW if COLOR else ""))
            continue
        return (r, col)


def menu() -> None:
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print(c("\n  ╔══ LABERINTO CON GRAFOS ═══════════════════╗", Fore.CYAN + Style.BRIGHT if COLOR else ""))
        print(c("  ║  Modelado con Grafos — Actividad Final IA ║", Fore.CYAN + Style.BRIGHT if COLOR else ""))
        print(c("  ╚═══════════════════════════════════════════╝\n", Fore.CYAN + Style.BRIGHT if COLOR else ""))
        print(c("  [1]", Fore.GREEN if COLOR else "") + "  🕹️  Jugar")
        print(c("  [2]", Fore.GREEN if COLOR else "") + "  📊  Ver grafo de adyacencia")
        print(c("  [3]", Fore.GREEN if COLOR else "") + "  🏅  Ver historial de partidas")
        print(c("  [4]", Fore.GREEN if COLOR else "") + "  🔎  Resolver con BFS (búsqueda por amplitud)")
        print(c("  [5]", Fore.GREEN if COLOR else "") + "  🧭  Resolver con DFS (búsqueda por profundidad)")
        print(c("  [6]", Fore.GREEN if COLOR else "") + "  ⚖️   Comparar BFS vs DFS")
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
        elif elec in ("4", "5"):
            os.system("cls" if os.name == "nt" else "clear")
            inicio = pedir_celda_inicio()
            mostrar_resultado_busqueda(resolver("bfs" if elec == "4" else "dfs", inicio=inicio))
            input("\n  Presiona Enter para continuar...")
        elif elec == "6":
            os.system("cls" if os.name == "nt" else "clear")
            inicio = pedir_celda_inicio()
            comparar_busquedas(inicio=inicio)
            input("\n  Presiona Enter para continuar...")
        elif elec == "0":
            print(c("\n  ¡Hasta luego! 👋\n", Fore.CYAN + Style.BRIGHT if COLOR else ""))
            break


if __name__ == "__main__":
    menu()
