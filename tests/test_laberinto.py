"""
tests/test_laberinto.py — Pruebas del laberinto base y de los algoritmos de búsqueda (BFS / DFS).
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from laberinto import (
    LABERINTO, N, INICIO, META, COSTO_BASE, COINS_INICIALES,
    costo_celda, construir_grafo, prueba_meta, transicion, OPERADORES, GRAFO,
    bfs_camino, dfs_camino, reconstruir_camino, costo_camino, resolver, ALGORITMOS,
)


# ── Costos de celda ──────────────────────────────────────────────────────────

def test_costo_libre():
    assert costo_celda(0) == COSTO_BASE

def test_costo_inicio():
    assert costo_celda(8) == COSTO_BASE

def test_costo_penalti_triple():
    assert costo_celda(2) == COSTO_BASE * 3

def test_costo_premio_cuarta_parte():
    assert costo_celda(3) == COSTO_BASE / 4

def test_costo_meta_cero():
    assert costo_celda(9) == 0

def test_costo_muro_infinito():
    assert costo_celda(1) == float("inf")


# ── Estructura del laberinto ─────────────────────────────────────────────────

def test_laberinto_es_9x9():
    assert len(LABERINTO) == N
    assert all(len(fila) == N for fila in LABERINTO)

def test_inicio_y_meta_existen():
    r_i, c_i = INICIO
    r_m, c_m = META
    assert LABERINTO[r_i][c_i] == 8, "Inicio debe ser celda 8"
    assert LABERINTO[r_m][c_m] == 9, "Meta debe ser celda 9"

def test_hay_celda_penalti():
    celdas = [LABERINTO[r][c] for r in range(N) for c in range(N)]
    assert 2 in celdas, "Debe haber al menos una celda penalti (2)"

def test_hay_celda_premio():
    celdas = [LABERINTO[r][c] for r in range(N) for c in range(N)]
    assert 3 in celdas, "Debe haber al menos una celda premio (3)"


# ── Grafo de adyacencia ──────────────────────────────────────────────────────

def test_grafo_tiene_nodos():
    assert len(GRAFO) > 0

def test_muros_no_son_nodos():
    for r in range(N):
        for c in range(N):
            if LABERINTO[r][c] == 1:
                assert (r, c) not in GRAFO, f"Muro {(r,c)} no debe ser nodo"

def test_inicio_es_nodo():
    assert INICIO in GRAFO

def test_meta_es_nodo():
    assert META in GRAFO

def test_aristas_tienen_peso_correcto():
    """El peso de cada arista debe coincidir con el costo de la celda destino."""
    for nodo, vecinos in GRAFO.items():
        for (nr, nc), peso in vecinos:
            esperado = costo_celda(LABERINTO[nr][nc])
            assert peso == esperado, f"Peso incorrecto en arista {nodo}→{(nr,nc)}"


# ── Modelo del agente ────────────────────────────────────────────────────────

def test_prueba_meta_en_meta():
    assert prueba_meta(META) is True

def test_prueba_meta_fuera_de_meta():
    assert prueba_meta(INICIO) is False

def test_transicion_valida():
    # Desde (0,0) moverse a (0,1) con 'd' debe ser válido
    nuevo, error = transicion((0, 0), "d", LABERINTO)
    assert error is None
    assert nuevo == (0, 1)

def test_transicion_muro():
    # Desde (0,0) moverse a (0,3) directamente pasaría por muro en col 3
    # Desde (0,2) moverse 'd' choca con muro en (0,3)
    nuevo, error = transicion((0, 2), "d", LABERINTO)
    assert nuevo is None
    assert error is not None

def test_transicion_limite():
    # Desde (0,0) moverse 'w' (arriba) sale del tablero
    nuevo, error = transicion((0, 0), "w", LABERINTO)
    assert nuevo is None
    assert error is not None


# ── Algoritmos de búsqueda: BFS y DFS ────────────────────────────────────────

def _assert_camino_valido(camino, inicio=INICIO, objetivo=META):
    """Un camino válido empieza en inicio, termina en objetivo y solo usa aristas del grafo."""
    assert camino is not None, "Debe existir un camino"
    assert camino[0] == inicio
    assert camino[-1] == objetivo
    for actual, siguiente in zip(camino, camino[1:]):
        vecinos = [v for v, _ in GRAFO[actual]]
        assert siguiente in vecinos, f"{actual} → {siguiente} no es una arista del grafo"
    assert len(set(camino)) == len(camino), "El camino no debe repetir nodos"


def test_bfs_encuentra_camino_valido():
    camino, _ = bfs_camino(GRAFO, INICIO, META)
    _assert_camino_valido(camino)


def test_dfs_encuentra_camino_valido():
    camino, _ = dfs_camino(GRAFO, INICIO, META)
    _assert_camino_valido(camino)


def test_bfs_es_optimo_en_pasos():
    """BFS devuelve el camino con menos pasos. La distancia Manhattan es una
    cota inferior; en este laberinto se alcanza, así que el óptimo es 16."""
    camino, _ = bfs_camino(GRAFO, INICIO, META)
    manhattan = abs(META[0] - INICIO[0]) + abs(META[1] - INICIO[1])
    assert len(camino) - 1 == manhattan == 16


def test_dfs_nunca_mas_corto_que_bfs():
    """Desde cualquier celda, DFS no puede dar un camino más corto que BFS."""
    for inicio in GRAFO:
        bfs, _ = bfs_camino(GRAFO, inicio, META)
        dfs, _ = dfs_camino(GRAFO, inicio, META)
        assert bfs is not None and dfs is not None
        assert len(dfs) >= len(bfs), f"DFS más corto que BFS desde {inicio}"


def test_dfs_a_veces_es_mas_largo_que_bfs():
    """DFS no garantiza el camino más corto: debe existir al menos un inicio donde se note."""
    mas_largo = [s for s in GRAFO
                 if len(dfs_camino(GRAFO, s, META)[0]) > len(bfs_camino(GRAFO, s, META)[0])]
    assert mas_largo, "Se esperaba al menos un inicio donde DFS dé un camino más largo"


def test_explorados_empiezan_en_inicio_y_terminan_en_meta():
    for funcion in (bfs_camino, dfs_camino):
        _, explorados = funcion(GRAFO, INICIO, META)
        assert explorados[0] == INICIO
        assert explorados[-1] == META
        assert len(explorados) == len(set(explorados)), "No se expande un nodo dos veces"
        assert len(explorados) <= len(GRAFO)


def test_bfs_explora_por_niveles():
    """En BFS la distancia al inicio de los nodos explorados nunca disminuye."""
    _, explorados = bfs_camino(GRAFO, INICIO, META)
    distancia = {INICIO: 0}
    # distancias reales con el propio BFS (predecesores implícitos en el orden)
    from collections import deque
    cola = deque([INICIO])
    while cola:
        n = cola.popleft()
        for v, _ in GRAFO[n]:
            if v not in distancia:
                distancia[v] = distancia[n] + 1
                cola.append(v)
    niveles = [distancia[n] for n in explorados]
    assert niveles == sorted(niveles)


def test_sin_camino_retorna_none():
    """Si un muro separa inicio y meta, ambos algoritmos devuelven None."""
    lab = [fila[:] for fila in LABERINTO]
    for r in range(N):
        lab[r][4] = 1                      # columna 4 completa de muros
    grafo = construir_grafo(lab)
    for funcion in (bfs_camino, dfs_camino):
        camino, explorados = funcion(grafo, INICIO, META)
        assert camino is None
        assert len(explorados) > 0
        assert all(c < 4 for _, c in explorados), "No debe cruzar el muro"


def test_reconstruir_camino():
    predecesor = {"A": None, "B": "A", "C": "B"}
    assert reconstruir_camino(predecesor, "C") == ["A", "B", "C"]
    assert reconstruir_camino(predecesor, "A") == ["A"]


def test_costo_camino_coincide_con_el_juego():
    """El costo del camino debe ser igual al que cobraría el juego moviéndose celda a celda."""
    camino, _ = bfs_camino(GRAFO, INICIO, META)
    coins = float(COINS_INICIALES)
    for (r, c) in camino[1:]:
        coins -= costo_celda(LABERINTO[r][c])
    assert abs((COINS_INICIALES - coins) - costo_camino(camino, LABERINTO)) < 1e-9


def test_resolver_resume_resultado():
    for metodo in ALGORITMOS:
        res = resolver(metodo)
        assert res["metodo"] == metodo
        assert res["camino"][0] == INICIO and res["camino"][-1] == META
        assert res["pasos"] == len(res["camino"]) - 1
        assert abs(res["coins_restantes"] - (COINS_INICIALES - res["costo"])) < 1e-9
        assert res["coins_restantes"] > 0, "Con 30 coins ambos deben llegar a la meta"


def test_resolver_desde_otra_posicion_y_coins():
    res = resolver("bfs", inicio=(4, 4), coins=5.0)
    assert res["inicio"] == (4, 4)
    assert res["camino"][0] == (4, 4)
    assert abs(res["coins_restantes"] - (5.0 - res["costo"])) < 1e-9


def test_ejemplo_de_clase_grafo_de_letras():
    """Los algoritmos reproducen el resultado del ejemplo visto en clase (K → U)."""
    letras = {
        'V': ['J'], 'J': ['D', 'V'], 'D': ['J', 'I', 'K', 'A', 'C'], 'K': ['D', 'M'],
        'I': ['D'], 'A': ['D', 'C', 'B', 'E'], 'C': ['D', 'A', 'M', 'L', 'U'],
        'M': ['K', 'C'], 'L': ['C', 'Y', 'Z'], 'Y': ['L'], 'Z': ['L'],
        'B': ['A', 'F', 'G', 'H'], 'F': ['B', 'R'], 'G': ['B'], 'H': ['B', 'S', 'T', 'U'],
        'R': ['F'], 'S': ['H'], 'T': ['H'], 'U': ['H', 'C'], 'E': ['A', 'N', 'O'],
        'N': ['E'], 'O': ['E'],
    }
    grafo = {n: [(v, 1) for v in vecinos] for n, vecinos in letras.items()}   # formato con costo
    assert bfs_camino(grafo, "K", "U")[0] == ["K", "D", "C", "U"]
    assert dfs_camino(grafo, "K", "U")[0] == ["K", "M", "C", "U"]
    # V → R: BFS da 6 aristas, DFS 8 → DFS no es óptimo
    assert len(bfs_camino(grafo, "V", "R")[0]) - 1 == 6
    assert len(dfs_camino(grafo, "V", "R")[0]) - 1 == 8


if __name__ == "__main__":
    test_fns = [v for k, v in globals().items() if k.startswith("test_")]
    passed = failed = 0
    for fn in test_fns:
        try:
            fn()
            print(f"  ✅ {fn.__name__}")
            passed += 1
        except Exception as e:
            print(f"  ❌ {fn.__name__}: {e}")
            failed += 1
    print(f"\n  {passed} passed, {failed} failed.")
