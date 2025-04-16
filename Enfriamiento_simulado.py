#28kg
import random
import math
import time
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import concurrent.futures

df = pd.read_excel("objects.xlsx")

# Función para calcular el peso total y el valor total de una solución
def calcular_peso_valor(solution, df):
    peso_total = 0
    valor_total = 0
    for i, cantidad in enumerate(solution):
        peso_total += df.loc[i, "Peso_kg"] * cantidad
        valor_total += df.loc[i, "Valor"] * cantidad
    return peso_total, valor_total

# Función para generar una solución inicial
def generar_solucion_inicial(df):
    return [0] * len(df)

# Función para generar un vecino modificando aleatoriamente la cantidad de un objeto
def generar_vecino(solution, df):
    vecino = solution[:]
    i = random.randint(0, len(df) - 1)
    if vecino[i] > 0 and random.random() < 0.5:
        vecino[i] -= 1
    else:
        vecino[i] += 1
    return vecino

def enfriamiento_simulado(df, capacidad, temp_inicial, temp_final, alpha, iteraciones_por_temp):
    start_time = time.time()

    sol_actual = generar_solucion_inicial(df)
    peso_actual, valor_actual = calcular_peso_valor(sol_actual, df)
    mejor_sol = sol_actual[:]
    mejor_valor = valor_actual

    temp = temp_inicial
    iteracion_global = 0
    iteracion_convergencia = 0

    historia_valor = []
    iteraciones_historia = []

    while temp > temp_final:
        for _ in range(iteraciones_por_temp):
            iteracion_global += 1

            sol_vecina = generar_vecino(sol_actual, df)
            peso_vecina, valor_vecina = calcular_peso_valor(sol_vecina, df)

            if peso_vecina <= capacidad:
                delta = valor_vecina - valor_actual
                if delta > 0:
                    sol_actual = sol_vecina
                    valor_actual = valor_vecina
                else:
                    if random.random() < math.exp(delta / temp):
                        sol_actual = sol_vecina
                        valor_actual = valor_vecina

                if valor_actual > mejor_valor:
                    mejor_sol = sol_actual[:]
                    mejor_valor = valor_actual
                    iteracion_convergencia = iteracion_global

                    # Solo guardar si hay mejora
                    historia_valor.append(mejor_valor)
                    iteraciones_historia.append(iteracion_global)

        temp *= alpha

    total_time = time.time() - start_time
    return mejor_sol, mejor_valor, iteracion_convergencia, historia_valor, iteraciones_historia, total_time

def ejecutar_ejecucion(index):
    mejor_solucion, mejor_valor, iter_convergencia, historia_valor, iteraciones_historia, tiempo_total = enfriamiento_simulado(
        df, 28, 1000, 0.01, 0.95, 100
    )
    return {
        'indice': index,
        'mejor_solucion': mejor_solucion,
        'mejor_valor': mejor_valor,
        'iter_convergencia': iter_convergencia,
        'historia_valor': historia_valor,
        'iteraciones_historia': iteraciones_historia,
        'tiempo_total_funcion': tiempo_total
    }

if __name__ == "__main__":
    n_ejecuciones = 100

    # Ejecutar el algoritmo de enfriamiento simulado en paralelo
    # utilizando ProcessPoolExecutor para aprovechar múltiples núcleos
    # de CPU y mejorar el rendimiento
    with concurrent.futures.ProcessPoolExecutor() as executor:
        resultados = list(executor.map(ejecutar_ejecucion, range(n_ejecuciones)))

    for r in resultados:
        print(f"Ejecución {r['indice']:2d} | "
              f"Tiempo: {r['tiempo_total_funcion']:.4f}s | "
              f"Mejor valor: {r['mejor_valor']} | "
              f"Iteración convergencia: {r['iter_convergencia']}")

    mejor_ejecucion_global = max(resultados, key=lambda x: x["mejor_valor"])
    print("\n--- Mejor solución global ---")
    print("Índice de ejecución:", mejor_ejecucion_global["indice"])
    print("Con valor total:", mejor_ejecucion_global["mejor_valor"])
    print("Solución (objetos en la mochila):", mejor_ejecucion_global["mejor_solucion"])

    peso_mejor_sol, _ = calcular_peso_valor(mejor_ejecucion_global["mejor_solucion"], df)
    print("Peso total de la mejor solución:", peso_mejor_sol)

    # Gráfica de ejecución vs mejor valor (gráfico de barras)
    indices = [r["indice"] for r in resultados]
    valores = [r["mejor_valor"] for r in resultados]

    # Gráfica de barras
    plt.figure()
    plt.bar(indices, valores, color='skyblue')
    plt.title("Mejor Valor por Ejecución")
    plt.xlabel("Ejecución")
    plt.ylabel("Mejor Valor")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()


    historia_mejor = mejor_ejecucion_global["historia_valor"]
    iteraciones_mejor = mejor_ejecucion_global["iteraciones_historia"]

    while len(historia_mejor) < 100:
        historia_mejor.append(historia_mejor[-1]) 

    # Gráfica de convergencia
    plt.figure()
    plt.step(range(1, 101), historia_mejor, where='post')
    plt.title("Convergencia de la Mejor Ejecución")
    plt.xlabel("Iteración")
    plt.ylabel("Mejor valor")
    plt.grid(True)
    plt.show()
