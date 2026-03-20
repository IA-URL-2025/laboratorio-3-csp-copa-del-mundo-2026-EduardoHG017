import pytest
from src.solver import run_solver
from src.world_cup_csp import WorldCupCSP
from src.data import TEAMS, GROUPS

def test_full_solution_found():
    """Prueba que el solver encuentre una solución válida para el problema completo."""
    solution = run_solver(debug=False, preassign_pots_1_2=True)
    assert solution is not None
    assert len(solution) == 48 # Todos los 48 equipos deben estar asignados

def test_all_groups_have_4_teams():
    """Verifica que cada grupo en la solución final tenga exactamente 4 equipos."""
    solution = run_solver(debug=False, preassign_pots_1_2=True)

    # Contar equipos por grupo
    group_counts = {g: 0 for g in GROUPS}
    for team, group in solution.items():
        group_counts[group] += 1

    for group, count in group_counts.items():
        assert count == 4, f"El grupo {group} no tiene 4 equipos, tiene {count}"

def test_solution_validity():
    """Prueba que la solución final cumple con todas las restricciones requeridas."""
    solution = run_solver(debug=False, preassign_pots_1_2=True)

    # Agrupar equipos por grupo
    groups_dict = {g: [] for g in GROUPS}
    for team, group in solution.items():
        groups_dict[group].append(team)

    for group, teams_in_group in groups_dict.items():
        # Restricción: Cada grupo debe tener exactamente un equipo de cada bombo
        pots = [TEAMS[team]["pot"] for team in teams_in_group]
        assert len(set(pots)) == 4, f"El grupo {group} no tiene equipos de 4 bombos diferentes."

        # Restricción de confederación
<<<<<<< HEAD
        confs = [TEAMS[team]["conf"] for team in teams_in_group]
        for conf in set(confs):
            count = confs.count(conf)
=======
        expanded_confs = []
        for team in teams_in_group:
            conf = TEAMS[team]["conf"]
            if isinstance(conf, list):
                expanded_confs.extend(conf)
            else:
                expanded_confs.append(conf)

        for conf in set(expanded_confs):
            count = expanded_confs.count(conf)
>>>>>>> b421739 (Implement CSP constraints+MRV+FC with real 2026 preselections)
            if conf == "UEFA":
                assert count <= 2, f"El grupo {group} excede el límite de 2 equipos UEFA."
            else:
                assert count == 1, f"El grupo {group} tiene más de un equipo de {conf}."

def test_backtracking_without_preassignment():
    """Verifica que el backtracking puro (sin preasignaciones fuertes) encuentre solución (aunque puede tardar más)."""
    # En lugar de resolver los 48 (puede ser lento), probamos con un subconjunto de datos
    # para asegurar que backtracking funciona.
    mini_teams = {
        "A1": {"conf": "CONMEBOL", "pot": 1},
        "A2": {"conf": "UEFA", "pot": 2},
        "A3": {"conf": "AFC", "pot": 3},
        "A4": {"conf": "CAF", "pot": 4},

        "B1": {"conf": "UEFA", "pot": 1},
        "B2": {"conf": "CONCACAF", "pot": 2},
        "B3": {"conf": "UEFA", "pot": 3},
        "B4": {"conf": "OFC", "pot": 4},
    }
    mini_groups = ["G1", "G2"]

    csp = WorldCupCSP(mini_teams, mini_groups, debug=False)
    domains = {t: list(mini_groups) for t in mini_teams.keys()}
    solution = csp.backtrack({}, domains)

    assert solution is not None
    assert len(solution) == 8 # 8 equipos asignados
