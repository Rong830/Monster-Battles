from __future__ import annotations

from random_gen import RandomGen
from team import MonsterTeam
from battle import Battle

from elements import Element

from data_structures.referential_array import ArrayR

class BattleTower:

    MIN_LIVES = 2
    MAX_LIVES = 10

    def __init__(self, battle: Battle|None=None) -> None:
        self.battle = battle or Battle(verbosity=0)
        self.player_team = None
        self.enemy_teams = []
        self.enemy_teams_order = []

    def set_my_team(self, team: MonsterTeam) -> None:
        # Generate the team lives here too.
        self.player_team = team
        self.player_team.regenerate_team()
        self.player_team.lives = RandomGen.randint(self.MIN_LIVES, self.MAX_LIVES + 1)

    def generate_teams(self, n: int) -> None:
        for _ in range(n):
            enemy_team = MonsterTeam(MonsterTeam.TeamMode.BACK, MonsterTeam.SelectionMode.RANDOM)
            enemy_team.regenerate_team()
            enemy_team.lives = RandomGen.randint(self.MIN_LIVES, self.MAX_LIVES + 1)
            self.enemy_teams.append(enemy_team)
            self.enemy_teams_order.append(enemy_team)

    def battles_remaining(self) -> bool:
        return self.player_team.lives > 0 and any(team.lives > 0 for team in self.enemy_teams)

    def next_battle(self) -> tuple[Battle.Result, MonsterTeam, MonsterTeam, int, int]:
        if not self.battles_remaining():
            raise ValueError("No battles remaining.")

        enemy_team = self.enemy_teams_order.pop(0)
        result, player_lives, enemy_lives = self.battle.battle(self.player_team, enemy_team)
        return result, self.player_team, enemy_team, player_lives, enemy_lives

    def out_of_meta(self) -> ArrayR[Element]:
        elements_present = ArrayR(len(Element), False)
        
        for team in self.enemy_teams:
            for monster in team.monster_order:
                for element in Element:
                    if element in monster.get_element():
                        elements_present[element.value - 1] = True
        
        for monster in self.player_team.monster_order:
            for element in Element:
                if element in monster.get_element():
                    elements_present[element.value - 1] = True

        return elements_present.filter(lambda x: not x)

    def sort_by_lives(self):
        # 1054 ONLY
        raise NotImplementedError

    def __next__(self):
        if not self.battles_remaining():
            raise StopIteration
        return self.next_battle()
    
    def __iter__(self):
        return self
    
def tournament_balanced(tournament_array: ArrayR[str]):
    # 1054 ONLY
    raise NotImplementedError

if __name__ == "__main__":

    RandomGen.set_seed(129371)

    bt = BattleTower(Battle(verbosity=3))
    bt.set_my_team(MonsterTeam(MonsterTeam.TeamMode.BACK, MonsterTeam.SelectionMode.RANDOM))
    bt.generate_teams(3)

    for result, my_team, tower_team, player_lives, tower_lives in bt:
        print(result, my_team, tower_team, player_lives, tower_lives)
