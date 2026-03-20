"""
Programa principal para ejecutar el CSP Solver de la Copa Mundial 2026.
Resuelve el problema de asignación de equipos a grupos usando backtracking,
forward checking y heurística MRV.
"""
import argparse
from src.solver import run_solver, print_solution


def main():
    """
    Punto de entrada principal del programa.
    """
    parser = argparse.ArgumentParser(
        description='Solver CSP para el Sorteo del Mundial 2026'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Activa el modo depuración (trazas detalladas de ejecución)'
    )
    args = parser.parse_args()

    # Ejecutar el solver con modo debug si se solicita
    print(f"Modo debug: {'Activado' if args.debug else 'Desactivado'}")
    solution = run_solver(debug=args.debug, preassign_pots_1_2=True)

    if solution:
        print_solution(solution)
    else:
        print("\nNo se pudo encontrar una asignación válida para todos los equipos.")


if __name__ == "__main__":
    main()
