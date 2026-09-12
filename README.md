# Laberinto con Grafos 🧩

Proyecto de la **Actividad Final de IA** — modelado de un mini-laberinto 9×9  
como grafo de estados en Python (un solo archivo).

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
├── laberinto.py          # ← archivo principal (todo el juego)
├── requirements.txt      # colorama (opcional, para colores)
├── tests/
│   └── test_laberinto.py
└── examples/
    ├── laberinto1.py     # referencia de clase
    └── laberinto2.py     # referencia de clase
```

`laberinto.py` está organizado en secciones:

| Sección | Contenido |
|---|---|
| 1 | Representación del entorno (mapa + `construir_grafo`) |
| 2 | Modelo del agente (estado, operadores, transición, prueba de meta) |
| 3 | Visualización ASCII con colores |
| 4 | Lógica de juego e historial de puntajes |
| 5 | Menú principal |

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
```

---

## Controles en el juego

| Tecla | Acción |
|---|---|
| `w` | Mover arriba |
| `s` | Mover abajo |
| `a` | Mover izquierda |
| `d` | Mover derecha |
| `g` | Ver grafo de adyacencia |
| `r` | Reiniciar partida |
| `q` | Volver al menú |
