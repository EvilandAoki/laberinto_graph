# =============================================================================
# BFS y DFS sobre un grafo — referencia de clase
# =============================================================================
#
# Este es el ejemplo visto en clase (grafo de letras). Sirve para entender la
# estructura de los dos algoritmos antes de aplicarlos al laberinto.
#
# Los dos algoritmos son IDÉNTICOS salvo por una línea:
#   BFS → frontera = COLA  → cola.pop(0)   (saca el PRIMERO que entró: FIFO)
#   DFS → frontera = PILA  → pila.pop(-1)  (saca el ÚLTIMO que entró:  LIFO)
#
# En laberinto.py estos mismos algoritmos están adaptados al grafo del
# laberinto, cuyos nodos son coordenadas (fila, columna) y cuyas aristas
# llevan el costo en coins de la celda destino.
# =============================================================================

grafo = {
    'V': ['J'],
    'J': ['D', 'V'],
    'D': ['J', 'I', 'K', 'A', 'C'],
    'K': ['D', 'M'],
    'I': ['D'],
    'A': ['D', 'C', 'B', 'E'],
    'C': ['D', 'A', 'M', 'L', 'U'],
    'M': ['K', 'C'],
    'L': ['C', 'Y', 'Z'],
    'Y': ['L'],
    'Z': ['L'],
    'B': ['A', 'F', 'G', 'H'],
    'F': ['B', 'R'],
    'G': ['B'],
    'H': ['B', 'S', 'T', 'U'],
    'R': ['F'],
    'S': ['H'],
    'T': ['H'],
    'U': ['H', 'C'],
    'E': ['A', 'N', 'O'],
    'N': ['E'],
    'O': ['E'],
}


def bfs_camino(grafo, inicio, objetivo):
    """Búsqueda por AMPLITUD: la frontera es una cola (FIFO)."""
    cola = [inicio]
    visitados = {inicio}
    predecesor = {inicio: None}
    while cola:
        nodo = cola.pop(0)                  # ← primero que entró
        if nodo == objetivo:
            # reconstrucción del camino
            camino = []
            while nodo is not None:
                camino.append(nodo)
                nodo = predecesor[nodo]
            return list(reversed(camino))

        for vecino in grafo[nodo]:
            if vecino not in visitados:
                visitados.add(vecino)
                predecesor[vecino] = nodo
                cola.append(vecino)
    return None


def dfs_camino(grafo, inicio, objetivo):
    """Búsqueda por PROFUNDIDAD: la frontera es una pila (LIFO)."""
    pila = [inicio]
    visitados = {inicio}
    predecesor = {inicio: None}
    while pila:
        nodo = pila.pop(-1)                 # ← último que entró
        if nodo == objetivo:
            # reconstrucción del camino
            camino = []
            while nodo is not None:
                camino.append(nodo)
                nodo = predecesor[nodo]
            return list(reversed(camino))

        for vecino in grafo[nodo]:
            if vecino not in visitados:
                visitados.add(vecino)
                predecesor[vecino] = nodo
                pila.append(vecino)
    return None


if __name__ == "__main__":
    for inicio, objetivo in [("K", "U"), ("V", "R")]:
        bfs = bfs_camino(grafo, inicio, objetivo)
        dfs = dfs_camino(grafo, inicio, objetivo)
        print(f"\n{inicio} → {objetivo}")
        print(f"  BFS: {' → '.join(bfs)}   ({len(bfs) - 1} aristas)")
        print(f"  DFS: {' → '.join(dfs)}   ({len(dfs) - 1} aristas)")
    print("\nBFS siempre da el camino con menos aristas; DFS encuentra un camino,")
    print("pero no necesariamente el más corto (ver V → R).")
