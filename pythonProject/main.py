# main.py


from interfaz.interfaz_grafica import InterfazCerchas

'''
from entrada_datos.lector_datos import leer_datos
from entrada_datos.dimensionador import dimensionar_sistema
from entrada_datos.matriz_inicial import crear_matriz_rigidez
from procesamiento.conectividad import leer_conectividad
from procesamiento.rigidez_elemento import calcular_rigidez_elemento
from procesamiento.ensamblaje import ensamblar_matriz_global
from solucion.factorizador import factorizar_matriz
from solucion.lector_cargas import leer_cargas
from solucion.solucionador import resolver_sistema
from solucion.salida_resultados import imprimir_resultados

'''


def main():
    # 1. Interfaz gráfica
    ventana = InterfazCerchas()
    ventana.mainloop()

    '''
    # 2. Entrada y dimensionamiento
    nodos, elementos = leer_datos(datos_entrada)
    sistema = dimensionar_sistema(nodos, elementos)
    K_global = crear_matriz_rigidez(sistema)

    # 3. Procesamiento estructural
    conectividad = leer_conectividad(elementos)
    for elemento in elementos:
        Ke = calcular_rigidez_elemento(elemento)
        K_global = ensamblar_matriz_global(K_global, Ke, elemento)

    # 4. Solución del sistema
    K_fact = factorizar_matriz(K_global)
    F = leer_cargas(datos_entrada)
    desplazamientos = resolver_sistema(K_fact, F)
    
    # 5. Salida
    imprimir_resultados(desplazamientos)
    '''


if __name__ == "__main__":
    main()
