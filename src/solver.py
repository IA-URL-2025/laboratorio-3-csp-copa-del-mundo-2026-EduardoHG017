import copy
from src.world_cup_csp import WorldCupCSP
from src.data import TEAMS, GROUPS

def run_solver(debug=False, preassign_pots_1_2=True):
    """
    Ejecuta el solver CSP para encontrar una asignación válida de equipos a grupos.
    :param debug: Activa las trazas de depuración.
    :param preassign_pots_1_2: Si es True, preasigna de forma secuencial los bombos 1 y 2
                               para simplificar el problema.
    :return: Diccionario con la asignación final o None si no hay solución.
    """

    csp = WorldCupCSP(TEAMS, GROUPS, debug=debug, restrict_pots=[3, 4])

    initial_assignment = {}

    PREASSIGNED = {
        "A": ["Mexico", "South Korea"],
        "B": ["Canada", "Japan"],
        "C": ["Brazil", "Denmark"],
        "D": ["USA", "Iran"],
        "E": ["England", "Colombia"],
        "F": ["Netherlands", "Ecuador"],
        "G": ["Belgium", "Morocco"],
        "H": ["Spain", "Germany"],
        "I": ["France", "Senegal"],
        "J": ["Argentina", "Ecuador"],
        "K": ["Portugal", "Iran"],
        "L": ["Croatia", "Uruguay"],
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

        teams_in_group.sort(key=lambda x: TEAMS[x]["pot"])

        for team in teams_in_group:
            info = TEAMS[team]
            print(f"  - {team} ({info['conf']}, Bombo {info['pot']})")
