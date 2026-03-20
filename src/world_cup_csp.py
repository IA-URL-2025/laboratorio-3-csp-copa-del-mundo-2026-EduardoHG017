import copy

class WorldCupCSP:
<<<<<<< HEAD
    def __init__(self, teams, groups, debug=False):
        """
        Inicializa el problema CSP para el sorteo del Mundial.
        :param teams: Diccionario con los equipos, sus confederaciones y bombos.
        :param groups: Lista con los nombres de los grupos (A-L).
        :param debug: Booleano para activar trazas de depuración.
=======
    TOP_4 = {"Argentina", "France", "Brazil", "England"}

    def __init__(self, teams, groups, debug=False, restrict_pots=None):
        """
        Inicializa el problema CSP para el sorteo del Mundial.
        Si restrict_pots se proporciona (lista), las variables se limitan a esos bombos.
>>>>>>> b421739 (Implement CSP constraints+MRV+FC with real 2026 preselections)
        """
        self.teams = teams
        self.groups = groups
        self.debug = debug

<<<<<<< HEAD
        # Las variables son los equipos.
        self.variables = list(teams.keys())
=======
        if restrict_pots is None:
            self.variables = list(teams.keys())
        else:
            self.variables = [team for team, info in teams.items() if info["pot"] in restrict_pots]
>>>>>>> b421739 (Implement CSP constraints+MRV+FC with real 2026 preselections)

        # El dominio de cada variable inicialmente son todos los grupos.
        self.domains = {team: list(groups) for team in self.variables}

<<<<<<< HEAD
    def get_team_confederation(self, team):
        return self.teams[team]["conf"]
=======
    def get_confederations(self, team):
        conf = self.teams[team]["conf"]
        return conf if isinstance(conf, list) else [conf]
>>>>>>> b421739 (Implement CSP constraints+MRV+FC with real 2026 preselections)

    def get_team_pot(self, team):
        return self.teams[team]["pot"]

    def is_valid_assignment(self, group, team, assignment):
        """
<<<<<<< HEAD
        Verifica si asignar un equipo a un grupo viola
        las restricciones de confederación o tamaño del grupo.
        """
        # TODO: implementar restricción de tamaño del grupo (máximo 4)
        # TODO: implementar restricción de que no puede haber dos equipos del mismo bombo
        # TODO: implementar restricción de confederaciones (máximo 1, excepto UEFA máximo 2)

        # Este es un valor de retorno por defecto, debes modificarlo
        pass

    def forward_check(self, assignment, domains):
        """
        Propagación de restricciones.
        Debe eliminar valores inconsistentes en dominios futuros.
        Retorna True si la propagación es exitosa, False si algún dominio queda vacío.
        """
        # Hacemos una copia de los dominios actuales para modificarla de forma segura
        new_domains = copy.deepcopy(domains)

        # TODO: implementar forward checking para filtrar grupos inválidos
        # en los dominios de las variables no asignadas.

        # Este es un valor de retorno por defecto, debes modificarlo
        return True, new_domains

    def select_unassigned_variable(self, assignment, domains):
        """
        Heurística MRV (Minimum Remaining Values).
        Selecciona la variable no asignada con el dominio más pequeño.
        """
        # TODO: implementar MRV

        # Este es un valor de retorno por defecto, debes modificarlo
        unassigned_vars = [v for v in self.variables if v not in assignment]
        return unassigned_vars[0] if unassigned_vars else None

    def backtrack(self, assignment, domains=None):
        """
        Backtracking search para resolver el CSP.
        """
        if domains is None:
            domains = copy.deepcopy(self.domains)

        # Condición de parada: Si todas las variables están asignadas, retornamos la asignación.
        if len(assignment) == len(self.variables):
            return assignment

        # TODO: implementar algoritmo de backtracking
        # 1. Seleccionar variable con MRV
        # 2. Iterar sobre sus valores (grupos) posibles en el dominio
        # 3. Verificar si es válido, hacer la asignación y aplicar forward checking
        # 4. Llamada recursiva
        # 5. Deshacer la asignación si falla (backtrack)

        # Este es un valor de retorno por defecto, debes modificarlo
=======
        Verifica si asignar un equipo a un grupo viola restricciones.
        - máximo 4 equipos por grupo
        - no repetir bombo
        - máximo 2 UEFA, máximo 1 resto
        - playoffs inter no chocan con confederaciones heredadas
        - top-4 anti-colisión
        """
        teams_in_group = [t for t, g in assignment.items() if g == group]

        # máximo 4 equipos
        if len(teams_in_group) >= 4:
            if self.debug:
                print(f"[FAIL] {team} -> {group}, grupo lleno ({len(teams_in_group)}).")
            return False

        # no repetir bombo
        team_pot = self.get_team_pot(team)
        for t in teams_in_group:
            if self.get_team_pot(t) == team_pot:
                if self.debug:
                    print(f"[FAIL] {team} -> {group}, mismo bombo que {t}.")
                return False

        # anti-colisión top-4
        if team in self.TOP_4 and any(t in self.TOP_4 for t in teams_in_group):
            if self.debug:
                print(f"[FAIL] {team} -> {group}, choque top-4.")
            return False

        # validar confederaciones
        uefa_count = 0
        used_non_uefa = set()

        for t in teams_in_group:
            for conf in self.get_confederations(t):
                if conf == "UEFA":
                    uefa_count += 1
                else:
                    used_non_uefa.add(conf)

        candidate_confs = self.get_confederations(team)

        if "UEFA" in candidate_confs:
            if uefa_count >= 2:
                if self.debug:
                    print(f"[FAIL] {team} -> {group}, excede UEFA (actual {uefa_count}).")
                return False

        for conf in candidate_confs:
            if conf != "UEFA" and conf in used_non_uefa:
                if self.debug:
                    print(f"[FAIL] {team} -> {group}, ya existe confederación {conf}.")
                return False

        # Para equipos con confederaciones list (Inter), validar explícito
        if isinstance(self.teams[team]["conf"], list):
            for conf in self.teams[team]["conf"]:
                if conf in used_non_uefa or (conf == "UEFA" and uefa_count >= 2):
                    if self.debug:
                        print(f"[FAIL] {team} -> {group}, choque interconfederación {conf}.")
                    return False

        return True

    def forward_check(self, assignment, domains):
        """
        Propagación de restricciones: actualizar dominios de variables no asignadas.
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
        unassigned = [v for v in self.variables if v not in assignment]
        if not unassigned:
            return None

        var = min(unassigned, key=lambda v: len(domains[v]))
        if self.debug:
            print(f"[MRV] Seleccionada variable: {var} con dominio {domains[var]}")
        return var

    def backtrack(self, assignment, domains=None):
        if domains is None:
            domains = copy.deepcopy(self.domains)

        # Condición de parada: si todos los equipos de pot3 y pot4 están asignados.
        if all(var in assignment for var in self.variables):
            return assignment

        var = self.select_unassigned_variable(assignment, domains)
        if var is None:
            return assignment

        for group in domains[var]:
            if self.debug:
                print(f"[TRY] {var} -> {group}")

            if not self.is_valid_assignment(group, var, assignment):
                if self.debug:
                    print(f"[FAIL] {var} -> {group} inválido")
                continue

            new_assignment = assignment.copy()
            new_assignment[var] = group

            ok, new_domains = self.forward_check(new_assignment, domains)
            if not ok:
                if self.debug:
                    print(f"[BACKTRACK] forward checking falló para {var} -> {group}")
                continue

            result = self.backtrack(new_assignment, new_domains)
            if result is not None:
                return result

            if self.debug:
                print(f"[BACKTRACK] Retrocediendo desde {var} -> {group}")

>>>>>>> b421739 (Implement CSP constraints+MRV+FC with real 2026 preselections)
        return None
