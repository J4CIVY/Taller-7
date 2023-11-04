import matplotlib.pyplot as plt
import networkx as nx
import sys
import json
from fastapi import FastAPI

app = FastAPI()

class Nodo:
    def __init__(self, datos):
        self.datos = datos
        self.siguiente = None

def floyd_tortoise(cabeza):
    if cabeza is None:
        return False

    tortuga = cabeza
    liebre = cabeza

    while liebre is not None and liebre.siguiente is not None:
        tortuga = tortuga.siguiente
        liebre = liebre.siguiente.siguiente

        if tortuga == liebre:
            return True

    return False

def crear_lista_enlazada(datos):
    # Convierte los datos JSON en una lista
    valores = datos

    cabeza = None
    actual = None
    nodos = {}

    for valor in valores:
        nuevo_nodo = Nodo(valor)

        if valor in nodos:
            nodo_existente = nodos[valor]
            actual.siguiente = nodo_existente
            break

        nodos[valor] = nuevo_nodo

        if cabeza is None:
            cabeza = nuevo_nodo
            actual = nuevo_nodo
        else:
            actual.siguiente = nuevo_nodo
            actual = nuevo_nodo

    return cabeza

def encontrar_ciclo(cabeza):
    tortuga = cabeza
    liebre = cabeza

    while liebre is not None and liebre.siguiente is not None:
        tortuga = tortuga.siguiente
        liebre = liebre.siguiente.siguiente

        if tortuga == liebre:
            ciclo_detectado = True
            tortuga = cabeza
            while tortuga != liebre:
                tortuga = tortuga.siguiente
                liebre = liebre.siguiente
            return tortuga  # Nodo donde se inicia el ciclo

    return None

def visualizar_lista_enlazada(cabeza, ciclo_inicio):
    G = nx.DiGraph()
    current = cabeza

    while current is not None:
        G.add_node(current.datos)
        if current.siguiente:
            G.add_edge(current.datos, current.siguiente.datos)
        current = current.siguiente
        if current == ciclo_inicio:
            break  # Detenerse al llegar al nodo de inicio del ciclo

    pos = nx.spring_layout(G)
    plt.figure(figsize=(10, 6))

    if ciclo_inicio:
        # Resalta los nodos del ciclo
        ciclo_nodes = set()
        current = ciclo_inicio
        while True:
            ciclo_nodes.add(current.datos)
            current = current.siguiente
            if current == ciclo_inicio:
                break

        node_colors = ['lightblue' if node not in ciclo_nodes else 'red' for node in G.nodes]

        nx.draw(G, pos, with_labels=True, node_size=2000, node_color=node_colors, font_size=10, font_color='black')
    else:
        # Sin ciclo, utiliza colores predeterminados
        nx.draw(G, pos, with_labels=True, node_size=2000, node_color='lightblue', font_size=10, font_color='black')

    plt.title("Lista Enlazada")
    plt.show()

@app.post('/api/detectar-ciclo')
async def detectar_ciclo(data: dict):
    try:
        datos = data.get('datos')
        cabeza = crear_lista_enlazada(datos)
        tiene_ciclo = floyd_tortoise(cabeza)

        if tiene_ciclo:
            ciclo_inicio = encontrar_ciclo(cabeza)
        else:
            ciclo_inicio = None

        result = {
            'tiene_ciclo': tiene_ciclo,
            'ciclo_inicio': ciclo_inicio.datos if ciclo_inicio else None
        }

        return result

    except json.JSONDecodeError:
        return {'error': 'Formato JSON inválido'}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=3001)