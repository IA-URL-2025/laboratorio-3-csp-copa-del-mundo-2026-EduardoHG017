import copy

class WorldCupCSP:
    TOP_4 = {"Argentina", "France", "Brazil", "England"}

    def __init__(self, teams, groups, debug=False, restrict_pots=None):
        """
        Inicializa el problema CSP para el sorteo del Mundial.
        Si restrict_pots se proporciona (lista), las variables se limitan a esos bombos.
        """
        self.teams = teams
        self.groups = groups
        self.debug = debug

        if restrict_pots is None:
            self.variables = list(teams.keys())
        else:
            self.variables = [team for team, info in teams.items() if info["pot"] in restrict_pots]

        self.domains = {team: list(groups) for team in self.variables}

    def get_confederations(self, team):
        conf = self.teams[team]["conf"]
        return conf if isinstance(conf, list) else [conf]

    def get_team_pot(self, team):
        return self.teams[team]["pot"]

    def is_valid_assignment(self, group, team, assignment):
        teams_in_group = [t for t, g in assignment.items() if g == group]

        if len(teams_in_group) >= 4:
            if self.debug:
                print(f"[FAIL] {team} -> {group}, grupo lleno ({len(teams_in_group)}).")
            return False

        team_pot = self.get_team_pot(team)
        for t in teams_in_group:
            if self.get_team_pot(t) == team_pot:
                if self.debug:
                    print(f"[FAIL] {team} -> {group}, mismo bombo que {t}.")
                return False

        if team in self.TOP_4 and any(t in self.TOP_4 for t in teams_in_group):
            if self.debug:
                print(f"[FAIL] {team} -> {group}, choque top-4.")
            return False

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

        if isinstance(self.teams[team]["conf"], list):
            for conf in self.teams[team]["conf"]:
                if conf in used_non_uefa or (conf == "UEFA" and uefa_count >= 2):
                    if self.debug:
                        print(f"[FAIL] {team} -> {group}, choque interconfederación {conf}.")
                    return False

        return True

    def forward_check(self, assignment, domains):
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

        return None
