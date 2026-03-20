========================
RESUMEN DE ARCHIVOS CORREGIDOS
========================

Este documento proporciona el código completo y correctamente formateado de los archivos principales.

================================================================================
1. src/world_cup_csp.py
================================================================================

"""
CSP Solver para el Sorteo del Mundial de Fútbol 2026.
Implementa backtracking con forward checking y heurística MRV.
"""
import copy


class WorldCupCSP:
    """
    Constraint Satisfaction Problem para asignar equipos de fútbol a grupos.
    Utiliza backtracking con forward checking y heurística MRV (Minimum Remaining Values).
    """

    TOP_4 = {"Argentina", "France", "Brazil", "England"}

    def __init__(self, teams, groups, debug=False, restrict_pots=None):
        """
        Inicializa el problema CSP para el sorteo del Mundial.

        Args:
            teams: Diccionario de equipos con información (pot, confederación)
            groups: Lista de grupos (A-L)
            debug: Activar modo depuración
            restrict_pots: Lista de bombos a usar como variables (default: todos)
        """
        self.teams = teams
        self.groups = groups
        self.debug = debug

        if restrict_pots is None:
            self.variables = list(teams.keys())
        else:
            self.variables = [
                team for team, info in teams.items()
                if info["pot"] in restrict_pots
            ]

        self.domains = {team: list(groups) for team in self.variables}

    def get_confederations(self, team):
        """
        Obtiene la confederación(es) de un equipo.
        Retorna una lista (incluso si es un único valor).

        Args:
            team: Nombre del equipo

        Returns:
            Lista de confederaciones del equipo
        """
        conf = self.teams[team]["conf"]
        return conf if isinstance(conf, list) else [conf]

    def get_team_pot(self, team):
        """
        Obtiene el bombo (pot) de un equipo.

        Args:
            team: Nombre del equipo

        Returns:
            Número del bombo (1, 2, 3, o 4)
        """
        return self.teams[team]["pot"]

    def is_valid_assignment(self, group, team, assignment):
        """
        Verifica si asignar un equipo a un grupo es válido.

        Restricciones validadas:
        1. Máximo 4 equipos por grupo
        2. No repetir bombo en un grupo
        3. Máximo 2 equipos UEFA por grupo
        4. Máximo 1 equipo por confederación no-UEFA
        5. No más de 1 equipo TOP-4 por grupo
        6. Validación de multi-confederaciones (playoffs)

        Args:
            group: Grupo (A-L)
            team: Nombre del equipo
            assignment: Diccionario actual de asignaciones

        Returns:
            True si la asignación es válida, False en caso contrario
        """
        teams_in_group = [t for t, g in assignment.items() if g == group]

        # Restricción 1: Máximo 4 equipos por grupo
        if len(teams_in_group) >= 4:
            if self.debug:
                print(f"[FAIL] {team} -> {group}, grupo lleno ({len(teams_in_group)}).")
            return False

        # Restricción 2: No repetir bombo
        team_pot = self.get_team_pot(team)
        for t in teams_in_group:
            if self.get_team_pot(t) == team_pot:
                if self.debug:
                    print(f"[FAIL] {team} -> {group}, mismo bombo que {t}.")
                return False

        # Restricción 5: No más de 1 equipo TOP-4
        if team in self.TOP_4 and any(t in self.TOP_4 for t in teams_in_group):
            if self.debug:
                print(f"[FAIL] {team} -> {group}, choque top-4.")
            return False

        # Restricción 3 y 4: Límites de confederaciones
        uefa_count = 0
        used_non_uefa = set()
        for t in teams_in_group:
            for conf in self.get_confederations(t):
                if conf == "UEFA":
                    uefa_count += 1
                else:
                    used_non_uefa.add(conf)

        candidate_confs = self.get_confederations(team)

        if "UEFA" in candidate_confs and uefa_count >= 2:
            if self.debug:
                print(f"[FAIL] {team} -> {group}, excede UEFA (actual {uefa_count}).")
            return False

        for conf in candidate_confs:
            if conf != "UEFA" and conf in used_non_uefa:
                if self.debug:
                    print(f"[FAIL] {team} -> {group}, ya existe confederación {conf}.")
                return False

        # Restricción 6: Validación de multi-confederaciones
        if isinstance(self.teams[team]["conf"], list):
            for conf in self.teams[team]["conf"]:
                if conf in used_non_uefa or (conf == "UEFA" and uefa_count >= 2):
                    if self.debug:
                        print(f"[FAIL] {team} -> {group}, choque interconfederación {conf}.")
                    return False

        return True

    def forward_check(self, assignment, domains):
        """
        Propagación hacia adelante: filtra dominios basado en restricciones.
        
        Reduce los dominios de variables no asignadas eliminando valores
        que violarían restricciones con asignaciones actuales.

        Args:
            assignment: Diccionario actual de asignaciones
            domains: Diccionario de dominios por variable

        Returns:
            (success, new_domains) - Tupla indicando éxito y dominios actualizados
        """
        new_domains = copy.deepcopy(domains)

        for var in self.variables:
            if var in assignment:
                continue

            valid_groups = []
            for group in new_domains[var]:
                if self.is_valid_assignment(group, var, assignment):
                    valid_groups.append(group)

            new_domains[var] = valid_groups

            if self.debug:
                print(f"[FC] Var {var} dominios filtrados: {valid_groups}")

            if not valid_groups:
                if self.debug:
                    print(f"[FC FAIL] Var {var} sin dominios.")
                return False, new_domains

        return True, new_domains

    def select_unassigned_variable(self, assignment, domains):
        """
        Selecciona la próxima variable sin asignar usando heurística MRV.
        
        MRV = Minimum Remaining Values (variable con menor dominio).
        Esta heurística mejora la eficiencia del backtracking al fallar rápidamente
        cuando un variable no tiene valores válidos.

        Args:
            assignment: Diccionario actual de asignaciones
            domains: Diccionario de dominios por variable

        Returns:
            Nombre del equipo con menor dominio, o None si todos están asignados
        """
        unassigned = [v for v in self.variables if v not in assignment]
        if not unassigned:
            return None

        var = min(unassigned, key=lambda v: len(domains[v]))
        if self.debug:
            print(f"[MRV] Seleccionada variable: {var} con dominio {domains[var]}")
        return var

    def backtrack(self, assignment, domains=None):
        """
        Algoritmo de backtracking con forward checking.
        
        Realiza una búsqueda exhaustiva con backtracking, utiliza forward checking
        para podar ramas inviables y MRV para seleccionar variables.

        Args:
            assignment: Diccionario actual de asignaciones
            domains: Diccionarios de dominios actuales (default: reiniciar)

        Returns:
            Solución completa (diccionario equipo->grupo) o None si no existe
        """
        if domains is None:
            domains = copy.deepcopy(self.domains)

        # Caso base: todas las variables están asignadas
        if all(var in assignment for var in self.variables):
            return assignment

        # Seleccionar próxima variable usando MRV
        var = self.select_unassigned_variable(assignment, domains)
        if var is None:
            return assignment

        # Intentar cada valor en el dominio
        for group in domains[var]:
            if self.debug:
                print(f"[TRY] {var} -> {group}")

            if not self.is_valid_assignment(group, var, assignment):
                if self.debug:
                    print(f"[FAIL] {var} -> {group} inválido")
                continue

            new_assignment = assignment.copy()
            new_assignment[var] = group

            # Forward checking
            ok, new_domains = self.forward_check(new_assignment, domains)
            if not ok:
                if self.debug:
                    print(f"[BACKTRACK] forward checking falló para {var} -> {group}")
                continue

            # Recursión
            result = self.backtrack(new_assignment, new_domains)
            if result is not None:
                return result

            if self.debug:
                print(f"[BACKTRACK] Retrocediendo desde {var} -> {group}")

        return None


================================================================================
2. src/solver.py
================================================================================

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


================================================================================
3. main.py
================================================================================

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


================================================================================
GARANTÍAS DE CALIDAD
================================================================================

✓ Indentación correcta: 4 espacios en todos los archivos
✓ Separación adecuada entre imports, clases y funciones
✓ Docstrings completos para cada clase y método
✓ Código legible y ejecutable
✓ Sintaxis verificada con py_compile

ESTRUCTURA CSP IMPLEMENTADA
================================================================================

Clase WorldCupCSP:
  - Método: __init__(teams, groups, debug=False, restrict_pots=None)
  - Método: get_confederations(team) -> Lista de confederaciones
  - Método: get_team_pot(team) -> Número del bombo
  - Método: is_valid_assignment(group, team, assignment) -> bool
    * Validación de 6 restricciones del problema
  - Método: forward_check(assignment, domains) -> (success, new_domains)
    * Propagación de restricciones
  - Método: select_unassigned_variable(assignment, domains) -> team
    * Heurística MRV (Minimum Remaining Values)
  - Método: backtrack(assignment, domains=None) -> solution
    * Algoritmo de backtracking con forward checking

Función run_solver(debug=False, preassign_pots_1_2=True):
  - Inicializa CSP con restrict_pots=[3,4] para variables
  - Preasigna bombos 1 y 2 según especificación
  - Ejecuta backtracking
  - Retorna diccionario equipo->grupo o None

Función print_solution(solution):
  - Imprime resultados agrupados por grupo (A-L)
  - Ordena equipos por bombo dentro de cada grupo

RESTRICCIONES IMPLEMENTADAS
================================================================================

1. Máximo 4 equipos por grupo
2. No repetir bombo en un grupo
3. Máximo 2 equipos UEFA por grupo
4. Máximo 1 confederación no-UEFA por grupo
5. Máximo 1 equipo TOP-4 por grupo
6. Manejo correcto de multi-confederaciones (playoffs)

CONSIDERACIONES
================================================================================

- Los archivos están completamente bien formateados
- No hay código compactado en una sola línea
- Todos los métodos tienen documentación completa
- El código es totalmente ejecutable y pasa validación de sintaxis
- Compatible con pytest sin errores

================================================================================
