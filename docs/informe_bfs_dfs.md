# Entrega 2 — Búsqueda por amplitud (BFS) y por profundidad (DFS)

> Texto listo para pegar en el informe técnico (Google Docs), a continuación de la
> sección 6 "Conclusiones" de la primera entrega. La numeración continúa desde allí;
> la sección "Links" puede quedar al final.
>
> Todo lo que se muestra (código, tablas y tableros) sale del código real del
> repositorio: `laberinto.py`, ejecutable con `python laberinto.py` y verificable
> con `python tests/test_laberinto.py`.

---

## 8. Algoritmos de búsqueda sobre el grafo del laberinto

En la primera entrega el laberinto 9×9 se convirtió en un grafo de adyacencia:
cada celda transitable es un nodo `(fila, columna)` y cada movimiento válido
(arriba, abajo, izquierda, derecha) es una arista cuyo peso es el costo en
coins de la celda destino. En esta entrega se implementan sobre ese mismo grafo
los dos algoritmos de **búsqueda no informada** vistos en clase:

- **Búsqueda por amplitud** (*Breadth-First Search*, BFS).
- **Búsqueda por profundidad** (*Depth-First Search*, DFS).

Se llaman "no informados" porque no usan ninguna información sobre dónde está la
meta ni sobre el costo de las aristas: solo conocen la estructura del grafo.

### 8.1 Estructura común

Los dos algoritmos usan exactamente las mismas tres estructuras de datos:

| Estructura | Qué guarda | Para qué sirve |
|---|---|---|
| `frontera` | Nodos descubiertos pero aún no explorados | Decide cuál es el siguiente nodo a visitar |
| `visitados` | Conjunto de nodos ya descubiertos | Evita repetir nodos y entrar en ciclos |
| `predecesor` | Para cada nodo, desde qué nodo se descubrió | Reconstruir el camino cuando se llega a la meta |

El esqueleto es el mismo en ambos casos:

```
frontera ← [inicio]
visitados ← {inicio}
predecesor[inicio] ← nulo

mientras la frontera no esté vacía:
    nodo ← sacar un nodo de la frontera          ← ÚNICA diferencia entre BFS y DFS
    si nodo es la meta:
        devolver reconstruir_camino(predecesor, nodo)
    para cada vecino de nodo:
        si vecino no está en visitados:
            marcar vecino como visitado
            predecesor[vecino] ← nodo
            agregar vecino a la frontera

devolver "no hay camino"
```

La **única diferencia** entre los dos algoritmos es qué nodo se saca de la frontera:

| | BFS — amplitud | DFS — profundidad |
|---|---|---|
| La frontera es… | una **cola** (FIFO) | una **pila** (LIFO) |
| Se saca… | el **primero** que entró (`popleft()`) | el **último** que entró (`pop()`) |
| Efecto | Explora por niveles: todo lo que está a 1 paso, luego a 2, luego a 3… | Se mete por una rama hasta el fondo y solo retrocede cuando se agota |
| ¿Encuentra camino si existe? | Sí | Sí |
| ¿Garantiza el camino con menos pasos? | **Sí** | **No** |
| ¿Tiene en cuenta el costo (coins)? | No | No |

La reconstrucción del camino es compartida: se parte de la meta y se siguen los
predecesores hacia atrás hasta llegar al inicio, y luego se invierte la lista.

```python
def reconstruir_camino(predecesor: dict, nodo) -> list:
    """Sigue la cadena de predecesores desde `nodo` hasta el inicio y la invierte."""
    camino = []
    while nodo is not None:
        camino.append(nodo)
        nodo = predecesor[nodo]
    return list(reversed(camino))
```

### 8.2 Búsqueda por amplitud (BFS)

BFS explora el grafo "en anillos": primero todos los nodos a distancia 1 del
inicio, después todos los que están a distancia 2, y así sucesivamente. Como la
meta se alcanza la primera vez que aparece en su anillo, el camino encontrado es
necesariamente el de **menor número de pasos**.

La frontera se implementa con `collections.deque`, que equivale a la lista con
`pop(0)` del ejemplo de clase pero extrae el primer elemento en tiempo constante.

```python
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
```

### 8.3 Búsqueda por profundidad (DFS)

DFS toma siempre el último nodo descubierto, así que avanza por una rama hasta
que ya no encuentra vecinos nuevos y entonces retrocede al punto de bifurcación
más reciente. Encuentra un camino si existe, pero el camino depende del orden en
que se recorren los vecinos y **no tiene por qué ser el más corto**.

En el grafo del laberinto los vecinos se generan en orden arriba, abajo,
izquierda, derecha; como la pila saca el último, DFS prueba primero hacia la
derecha, luego hacia la izquierda, luego hacia abajo y por último hacia arriba.

```python
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
```

### 8.4 Integración en el laberinto

Ambas funciones reciben el grafo construido por `construir_grafo` (sección 2 del
informe) y devuelven dos cosas: el camino y la lista de nodos **explorados** en
orden, que permite visualizar cuánto trabajo hizo cada algoritmo.

Como BFS y DFS ignoran los pesos, el gasto en coins del camino se calcula aparte
con la misma regla del juego (se paga el costo de cada celda a la que se entra):

```python
def costo_camino(camino: list, lab: list) -> float:
    """
    Coins que consume recorrer `camino`.
    Igual que en el juego: se paga el costo de cada celda a la que se ENTRA,
    por eso se omite la primera (donde ya estamos).
    """
    return sum(costo_celda(lab[r][col]) for r, col in camino[1:])
```

La función `resolver(metodo, inicio, objetivo, coins)` ejecuta el algoritmo
pedido y resume: camino, pasos, coins gastados, coins restantes y nodos
explorados. Sobre ella se construyeron las nuevas opciones de la aplicación:

| Dónde | Qué hace |
|---|---|
| Menú `[4]` | Resuelve el laberinto con BFS y dibuja el camino y los nodos explorados |
| Menú `[5]` | Lo mismo con DFS |
| Menú `[6]` | Ejecuta ambos desde la misma celda y muestra una tabla comparativa |
| En partida, tecla `b` / `p` | Pista: ruta BFS / DFS desde la posición actual del jugador con sus coins actuales |

En los tableros el camino se marca con `*` y los nodos que el algoritmo exploró
pero descartó con `○`. Las pruebas automáticas (`tests/test_laberinto.py`, 33
casos) verifican, entre otras cosas, que los caminos solo usan aristas del grafo,
que BFS alcanza el mínimo de pasos, que DFS nunca da un camino más corto que BFS
desde ninguna celda y que ambos devuelven `None` cuando un muro separa inicio y
meta.

---

## 9. Resultados y comparación

### 9.1 Desde el inicio `S (0, 0)` hasta la meta `G (8, 8)` con 30 coins

| Método | Pasos | Coins gastados | Coins restantes | Nodos explorados |
|---|---:|---:|---:|---:|
| BFS — amplitud | 16 | 14.25 | 15.75 | 64 de 64 |
| DFS — profundidad | 16 | 15.00 | 15.00 | 44 de 64 |

Camino BFS:
`(0, 0) → (1, 0) → (2, 0) → (2, 1) → (2, 2) → (3, 2) → (4, 2) → (4, 3) → (4, 4) → (5, 4) → (6, 4) → (6, 5) → (7, 5) → (8, 5) → (8, 6) → (8, 7) → (8, 8)`

Camino DFS:
`(0, 0) → (0, 1) → (0, 2) → (1, 2) → (2, 2) → (2, 3) → (2, 4) → (2, 5) → (3, 5) → (4, 5) → (4, 6) → (4, 7) → (5, 7) → (5, 8) → (6, 8) → (7, 8) → (8, 8)`

```
  BFS — búsqueda por amplitud
    0  1  2  3  4  5  6  7  8
 0│ S  ○  ○  █  ○  ○  ○  ○  ○ 
 1│ *  ○  ○  █  ○  ○  ○  ○  ○ 
 2│ *  *  *  ○  ○  ○  █  ○  ○ 
 3│ █  █  *  █  █  ○  █  ○  ○ 
 4│ ○  ○  *  *  *  ○  ○  ○  █ 
 5│ ○  █  █  █  *  █  █  ○  ○ 
 6│ ○  ○  ○  ○  *  *  ○  █  ○ 
 7│ ○  █  ○  ○  █  *  ○  ○  ○ 
 8│ ○  ○  ○  ○  ○  *  *  *  G 

  DFS — búsqueda por profundidad
    0  1  2  3  4  5  6  7  8
 0│ S  *  *  █  ·  ·  ·  ·  · 
 1│ ·  P  *  █  ·  R  ·  ·  · 
 2│ ·  ·  *  *  *  *  █  ·  · 
 3│ █  █  ·  █  █  *  █  ·  · 
 4│ ○  ○  ○  ○  ·  *  *  *  █ 
 5│ ○  █  █  █  ○  █  █  *  * 
 6│ ○  ○  ○  ○  ○  ○  ○  █  * 
 7│ ○  █  ○  ○  █  ○  ○  ○  * 
 8│ ○  ○  ○  ○  ○  ○  ○  ○  G 

  *  camino encontrado      ○  explorado y descartado
```

Lectura de los resultados:

1. **Los dos llegan en 16 pasos**, que es el mínimo posible (la distancia
   Manhattan entre las esquinas `(0,0)` y `(8,8)` es 16). En BFS esto está
   garantizado por el algoritmo; en DFS es una casualidad de este mapa: la rama
   que prueba primero (derecha y abajo) resulta llevar directo a la meta.
2. **BFS exploró los 64 nodos y DFS solo 44.** La meta es la celda más lejana
   del inicio, está en el último "anillo", así que BFS no la alcanza hasta haber
   vaciado todos los anillos anteriores. DFS, en cambio, se lanzó hacia la
   derecha y encontró la meta sin recorrer la mitad izquierda del tablero.
3. **Ninguno optimiza coins.** BFS pasa por el premio `R(8,5)` y gasta 14.25;
   DFS no pasa por celdas especiales y gasta 15.00. Esa diferencia es consecuencia
   del camino que les tocó, no de una decisión del algoritmo: los dos ignoran el
   peso de las aristas.

### 9.2 Desde otras celdas la diferencia es evidente

La opción `[6]` del menú permite elegir la celda de inicio. Al ejecutar ambos
algoritmos desde cada una de las 64 celdas transitables, **DFS da un camino más
largo que BFS en 20 de ellas y nunca uno más corto**. Algunos casos:

| Inicio | Pasos BFS | Pasos DFS | Coins BFS | Coins DFS | Restantes BFS | Restantes DFS | Explorados BFS | Explorados DFS |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `(5, 8)` | 3 | 21 | 2.00 | 20.00 | 28.00 | 10.00 | 6 | 22 |
| `(0, 4)` | 12 | 28 | 11.00 | 27.00 | 19.00 | 3.00 | 62 | 29 |
| `(4, 7)` | 5 | 19 | 4.00 | 18.00 | 26.00 | 12.00 | 24 | 20 |
| `(7, 3)` | 6 | 20 | 4.25 | 21.00 | 25.75 | 9.00 | 31 | 32 |

Desde `(5, 8)` la meta está a 3 pasos en línea recta hacia abajo. BFS la
encuentra explorando 6 nodos; DFS, por el orden de los vecinos, primero sube y
recorre casi todo el tablero por la izquierda y llega en 21 pasos. Desde
`(0, 4)` un jugador que siguiera la ruta de DFS llegaría a la meta con 3 coins
de los 30 iniciales; con la de BFS llegaría con 19.

En cuanto al trabajo realizado, la cantidad de nodos explorados no favorece
siempre al mismo algoritmo: desde el inicio DFS exploró menos nodos que BFS,
pero desde 13 de las 64 celdas ocurre lo contrario. Depende de
si la rama que DFS elige primero conduce o no hacia la meta.

### 9.3 El mismo comportamiento en el grafo visto en clase

El archivo `examples/busqueda_bfs_dfs.py` reproduce el ejemplo de clase con el
grafo de letras. De `K` a `U` ambos algoritmos llegan con 3 aristas, pero de
`V` a `R` se ve la diferencia:

| Recorrido | BFS | DFS |
|---|---|---|
| `K → U` | `K → D → C → U` (3 aristas) | `K → M → C → U` (3 aristas) |
| `V → R` | `V → J → D → A → B → F → R` (6 aristas) | `V → J → D → C → U → H → B → F → R` (8 aristas) |

---

## 10. Conclusiones de la entrega 2

1. **BFS y DFS son el mismo algoritmo con una estructura de datos distinta.**
   Comparten frontera, conjunto de visitados y mapa de predecesores; solo cambia
   si la frontera es una cola (BFS) o una pila (DFS). En el código esa diferencia
   es una sola línea: `cola.popleft()` frente a `pila.pop()`.
2. **BFS garantiza el camino con menos pasos; DFS no.** En este laberinto ambos
   llegan en 16 pasos desde el inicio, pero desde 20 de las 64 celdas DFS
   produce caminos más largos, en un caso 21 pasos frente a 3. Esto confirma lo
   visto en clase: DFS es completo en grafos finitos pero no es óptimo.
3. **La cantidad de nodos explorados depende de la posición de la meta.** BFS
   recorre todos los anillos previos a la meta (64 de 64 nodos desde el inicio);
   DFS puede ser mucho más rápido si su primera rama apunta hacia la meta (44
   nodos), o peor si apunta en dirección contraria.
4. **Ninguno de los dos resuelve el objetivo real del juego**, que es llegar con
   la mayor cantidad de coins. Ambos ignoran el peso de las aristas: el gasto en
   coins es un efecto secundario del camino que encuentran. Para optimizar coins
   hace falta una búsqueda que sí considere el costo acumulado, como búsqueda de
   costo uniforme o A*, que sería la extensión natural de este trabajo.
5. **El laberinto como grafo permitió reutilizar todo lo anterior.** No hubo que
   cambiar la representación del entorno ni el modelo del agente: los algoritmos
   trabajan directamente sobre el diccionario de adyacencia construido en la
   primera entrega.
