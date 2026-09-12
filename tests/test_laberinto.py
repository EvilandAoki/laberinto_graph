"""
tests/test_laberinto.py — Pruebas del laberinto base.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from laberinto import (
    LABERINTO, N, INICIO, META, COSTO_BASE, COINS_INICIALES,
    costo_celda, construir_grafo, prueba_meta, transicion, OPERADORES, GRAFO,
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
