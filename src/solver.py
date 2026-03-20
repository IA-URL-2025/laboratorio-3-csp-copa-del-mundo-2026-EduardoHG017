"""
Solver para el sorteo del Mundial 2026 usando Constraint Satisfaction Problem (CSP).
Implementa backtracking con forward checking y heurística MRV.
"""
import copy
from src.world_cup_csp import WorldCupCSP
from src.data import TEAMS, GROUPS


def run_solver(debug=False, preassign_pots_1_2=True):
    """
    Ejecuta el solver CSP para encontrar una asignación válida de equipos a grupos.

    Args:
        debug: Activa las trazas de depuración (default: False).
        preassign_pots_1_2: Si es True, preasigna los bombos 1 y 2 (default: True).

    Returns:
        Diccionario con la asignación final (equipo -> grupo) o None si no hay solución.

    Raises:
        ValueError: Si un equipo preasignado no existe en TEAMS.
    """
    csp = WorldCupCSP(TEAMS, GROUPS, debug=debug, restrict_pots=[3, 4])

    initial_assignment = {}

    # Preasignación de bombos 1 y 2 según 2026 World Cup propuesto
    PREASSIGNED = {
        "A": ["Mexico", "South Korea"],
        "B": ["Canada", "Japan"],
        "C": ["Brazil", "Morocco"],
        "D": ["USA", "Colombia"],
        "E": ["England", "Germany"],
        "F": ["Netherlands", "Uruguay"],
        "G": ["Belgium", "Senegal"],
        "H": ["Spain", "Switzerland"],
        "I": ["France", "Iran"],
        "J": ["Argentina", "Peru"],
        "K": ["Portugal", "Denmark"],
        "L": ["Croatia", "Italy"],
    }

    if preassign_pots_1_2:
        for group, teams_in_group in PREASSIGNED.items():
            for t in teams_in_group:
                if t not in TEAMS:
                    raise ValueError(f"Equipo preasignado desconocido: {t}")

                initial_assignment[t] = group
                if debug:
                    print(f"Preasignado {t} -> Grupo {group}")

    print("\nIniciando Solver CSP...")
    domains = copy.deepcopy(csp.domains)
    success, domains = csp.forward_check(initial_assignment, domains)
    if not success:
        if debug:
            print("Fallo en forward_check con la asignación inicial.")
        return None

    solution = csp.backtrack(initial_assignment, domains)

    return solution


def print_solution(solution):
    """
    Imprime la solución agrupada por cada uno de los grupos (A-L).

    Args:
        solution: Diccionario con asignación equipo -> grupo, o None.
    """
    if not solution:
        print("No se encontró solución.")
        return

    print("\n=== Sorteo Final de la Copa Mundial 2026 ===")

    groups_dict = {g: [] for g in GROUPS}
    for team, group in solution.items():
        groups_dict[group].append(team)

    for group in GROUPS:
        print(f"\nGrupo {group}:")
        teams_in_group = groups_dict[group]

        # Ordenar por bombo
        teams_in_group.sort(key=lambda x: TEAMS[x]["pot"])

        for team in teams_in_group:
            info = TEAMS[team]
            print(f"  - {team} ({info['conf']}, Bombo {info['pot']})")
