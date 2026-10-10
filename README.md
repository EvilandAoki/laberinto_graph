# Laberinto con Grafos 🧩

Proyecto de la **Actividad Final de IA** — modelado de un mini-laberinto 9×9  
como grafo de estados en Python (un solo archivo).

**Entrega 2:** sobre ese mismo grafo se implementan los dos algoritmos de búsqueda
no informada vistos en clase: **búsqueda por amplitud (BFS)** y **búsqueda por
profundidad (DFS)**. Ver [Algoritmos de búsqueda](#algoritmos-de-búsqueda-bfs--dfs).

---

## Modelo del agente

| Concepto | Implementación |
|---|---|
| **Estado** | Posición del jugador `(fila, columna)` |
| **Operadores** | Movimientos válidos: `w` ↑ `s` ↓ `a` ← `d` → |
| **Prueba de meta** | `estado == (8, 8)` |
| **Costo de ruta** | Coins consumidos según tipo de celda |

---

## Reglas del juego

| Celda | Símbolo | Costo |
|---|---|---|
| Libre | `·` | 1 coin |
| Inicio | `S` | 0 coins |
| Meta | `G` | 0 coins |
| Penalti | `P` | 3 coins (×3) |
| Premio | `R` | 0.25 coins (÷4) |
| Muro | `█` | bloqueado |

- Coins iniciales: **30**
- Si llegas a 0 coins → **pierdes**
- Quien llega a la meta con más coins → **gana**

---

## Mapa 9×9

```
     0   1   2   3   4   5   6   7   8
   ─────────────────────────────────────
0 │  S   ·   ·   █   ·   ·   ·   ·   ·
1 │  ·   P   ·   █   ·   R   ·   ·   ·
2 │  ·   ·   ·   ·   ·   ·   █   ·   ·
3 │  █   █   ·   █   █   ·   █   ·   ·
4 │  ·   ·   ·   ·   ·   ·   ·   ·   █
5 │  ·   █   █   █   ·   █   █   ·   ·
6 │  ·   ·   ·   ·   ·   ·   ·   █   ·
7 │  ·   █   P   ·   █   ·   ·   ·   ·
8 │  ·   ·   ·   ·   ·   R   ·   ·   G
```

---

## Estructura del proyecto

```
laberinto_graph/
├── laberinto.py              # ← archivo principal (juego + algoritmos de búsqueda)
├── requirements.txt          # colorama (opcional, para colores)
├── tests/
│   └── test_laberinto.py     # pruebas del laberinto y de BFS / DFS
├── examples/
│   ├── laberinto1.py         # referencia de clase (laberinto)
│   ├── laberinto2.py         # referencia de clase (laberinto)
│   └── busqueda_bfs_dfs.py   # referencia de clase (BFS / DFS sobre grafo de letras)
└── docs/
    └── informe_bfs_dfs.md    # texto de la entrega 2 para el informe
```

`laberinto.py` está organizado en secciones:

| Sección | Contenido |
|---|---|
| 1 | Representación del entorno (mapa + `construir_grafo`) |
| 2 | Modelo del agente (estado, operadores, transición, prueba de meta) |
| 3 | **Algoritmos de búsqueda**: `bfs_camino`, `dfs_camino`, `costo_camino`, `resolver` |
| 4 | Visualización ASCII con colores (tablero, grafo, tablero con la solución) |
| 5 | Lógica de juego, historial, resultado y comparación de búsquedas |
| 6 | Menú principal |

---

## Algoritmos de búsqueda (BFS / DFS)

Los dos algoritmos recorren el **grafo de adyacencia** de la sección 1
(`grafo[(fila, col)] = [(vecino, costo), ...]`) buscando un camino desde una
celda de inicio hasta la meta. Comparten exactamente la misma estructura:

| Pieza | Para qué sirve |
|---|---|
| `frontera` | Nodos pendientes de explorar |
| `visitados` | Nodos ya descubiertos, para no repetirlos ni entrar en ciclos |
| `predecesor` | Desde qué nodo se descubrió cada nodo, para reconstruir el camino al final |

La **única** diferencia es qué nodo se saca de la frontera en cada iteración:

```python
# BFS — la frontera es una COLA: sale el PRIMERO que entró (FIFO)
nodo = cola.popleft()

# DFS — la frontera es una PILA: sale el ÚLTIMO que entró (LIFO)
nodo = pila.pop()
```

| | BFS — búsqueda por amplitud | DFS — búsqueda por profundidad |
|---|---|---|
| Frontera | Cola (FIFO) | Pila (LIFO) |
| Cómo explora | Por niveles: todo lo que está a 1 paso, luego a 2, luego a 3... | Se mete por una rama hasta el fondo y solo retrocede cuando se agota |
| ¿Encuentra camino si existe? | Sí | Sí |
| ¿Garantiza el camino con menos pasos? | **Sí** | **No** |
| ¿Tiene en cuenta el costo en coins? | No | No |

Ambas funciones retornan `(camino, explorados)`: el camino como lista de celdas
(o `None` si no existe) y la lista de nodos que el algoritmo fue sacando de la
frontera, en orden, que es lo que se dibuja con `○` en el tablero.

### Resultado sobre el laberinto desde `S (0, 0)`

| Método | Pasos | Coins gastados | Coins restantes | Nodos explorados |
|---|---:|---:|---:|---:|
| BFS — amplitud | 16 | 14.25 | 15.75 | 64 de 64 |
| DFS — profundidad | 16 | 15.00 | 15.00 | 44 de 64 |

```
  BFS (amplitud)                       DFS (profundidad)
    0  1  2  3  4  5  6  7  8            0  1  2  3  4  5  6  7  8
 0│ S  ○  ○  █  ○  ○  ○  ○  ○         0│ S  *  *  █  ·  ·  ·  ·  ·
 1│ *  ○  ○  █  ○  ○  ○  ○  ○         1│ ·  P  *  █  ·  R  ·  ·  ·
 2│ *  *  *  ○  ○  ○  █  ○  ○         2│ ·  ·  *  *  *  *  █  ·  ·
 3│ █  █  *  █  █  ○  █  ○  ○         3│ █  █  ·  █  █  *  █  ·  ·
 4│ ○  ○  *  *  *  ○  ○  ○  █         4│ ○  ○  ○  ○  ·  *  *  *  █
 5│ ○  █  █  █  *  █  █  ○  ○         5│ ○  █  █  █  ○  █  █  *  *
 6│ ○  ○  ○  ○  *  *  ○  █  ○         6│ ○  ○  ○  ○  ○  ○  ○  █  *
 7│ ○  █  ○  ○  █  *  ○  ○  ○         7│ ○  █  ○  ○  █  ○  ○  ○  *
 8│ ○  ○  ○  ○  ○  *  *  *  G         8│ ○  ○  ○  ○  ○  ○  ○  ○  G

  * camino encontrado   ○ explorado y descartado
```

Observaciones:

- **Los dos llegan en 16 pasos**, que es el mínimo posible (distancia Manhattan
  entre esquinas). En BFS está garantizado; en DFS es casualidad de este mapa.
- **BFS explora los 64 nodos** porque la meta es la celda más lejana del inicio:
  está en el último "anillo" y BFS no llega a ella hasta haber vaciado todos los
  anteriores. **DFS explora 44** porque se lanza hacia la derecha y abajo y
  encuentra la meta sin recorrer la mitad izquierda.
- **Ninguno optimiza coins.** BFS pasa por el premio `R(8,5)` y gasta 14.25;
  DFS no pasa por celdas especiales y gasta 15.00. Es consecuencia del camino
  que les tocó, no una decisión del algoritmo.

### Desde otras celdas se nota la diferencia

Opción `[6]` del menú permite elegir la celda de inicio. Algunos casos:

| Inicio | Pasos BFS | Pasos DFS | Coins BFS | Coins DFS |
|---|---:|---:|---:|---:|
| `(5, 8)` | 3 | 21 | 2.00 | 20.00 |
| `(0, 4)` | 12 | 28 | 11.00 | 27.00 |
| `(4, 7)` | 5 | 19 | 4.00 | 18.00 |
| `(7, 3)` | 6 | 20 | 4.25 | 21.00 |

Desde `(0, 4)` un jugador que siguiera la ruta de DFS llegaría con 3 coins de 30;
con la de BFS llegaría con 19. En 20 de las 64 celdas DFS da un camino más largo
que BFS; en ninguna da uno más corto (está probado en los tests).

### Cómo usarlos

- Menú `[4]` resuelve con BFS, `[5]` con DFS y `[6]` compara ambos. Los tres
  preguntan la celda de inicio (Enter = `(0, 0)`).
- Dentro de una partida, `b` muestra la ruta BFS desde tu posición actual y `p`
  la ruta DFS, con tus coins actuales.
- Desde código:

```python
from laberinto import GRAFO, INICIO, META, bfs_camino, dfs_camino, resolver

camino, explorados = bfs_camino(GRAFO, INICIO, META)
res = resolver("dfs", inicio=(4, 4), coins=12)   # dict con camino, pasos, costo, coins_restantes...
```

El ejemplo de clase con el grafo de letras está en `examples/busqueda_bfs_dfs.py`.

---

## Instalación y ejecución

```bash
cd laberinto_graph

# (Opcional) Entorno virtual y colores
python3 -m venv venv
source venv/bin/activate
pip install colorama

# Ejecutar el juego
python laberinto.py

# Ejecutar pruebas
python tests/test_laberinto.py

# Ejemplo de clase: BFS y DFS sobre el grafo de letras
python examples/busqueda_bfs_dfs.py
```

---

## Controles en el juego

| Tecla | Acción |
|---|---|
| `w` | Mover arriba |
| `s` | Mover abajo |
| `a` | Mover izquierda |
| `d` | Mover derecha |
| `b` | Pista: ruta BFS (amplitud) desde la posición actual |
| `p` | Pista: ruta DFS (profundidad) desde la posición actual |
| `g` | Ver grafo de adyacencia |
| `r` | Reiniciar partida |
| `q` | Volver al menú |
