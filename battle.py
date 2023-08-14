from __future__ import annotations
from enum import auto
from typing import Optional

from base_enum import BaseEnum
from team import MonsterTeam


class Battle:

    class Action(BaseEnum):
        ATTACK = auto()
        SWAP = auto()
        SPECIAL = auto()

    class Result(BaseEnum):
        TEAM1 = auto()
        TEAM2 = auto()
        DRAW = auto()

    def __init__(self, verbosity=0) -> None:
        self.verbosity = verbosity

    def process_turn(self) -> Optional[Battle.Result]:
        """
        Process a single turn of the battle. Should:
        * process actions chosen by each team
        * level and evolve monsters
        * remove fainted monsters and retrieve new ones.
        * return the battle result if completed.
        """
        # Process actions chosen by each team
        action_team1 = self.team1.choose_action(self.out1, self.out2)
        action_team2 = self.team2.choose_action(self.out2, self.out1)

        # Handle actions
        if action_team1 == Battle.Action.ATTACK:
            self.out2.hp -= self.out1.get_attack()
        elif action_team1 == Battle.Action.SWAP:
            self.out1 = self.team1.retrieve_from_team()

        if action_team2 == Battle.Action.ATTACK:
            self.out1.hp -= self.out2.get_attack()
        elif action_team2 == Battle.Action.SWAP:
            self.out2 = self.team2.retrieve_from_team()

        # Subtract 1 from HP if both survive
        if self.out1.alive() and self.out2.alive():
            self.out1.hp -= 1
            self.out2.hp -= 1
        
        if self.out1.alive() and (not self.out2.alive()):
            self.out1.level_up()
        elif self.out2.alive() and (not self.out1.alive()):
            self.out2.level_up()

        # Handle level ups and evolutions
        if self.out1.ready_to_evolve():
            self.out1 = self.out1.evolve()
        if self.out2.ready_to_evolve():
            self.out2 = self.out2.evolve()

        # Check if any monsters fainted and replace them
        if not self.out1.alive():
            self.out1 = self.team1.retrieve_from_team()
        if not self.out2.alive():
            self.out2 = self.team2.retrieve_from_team()

        # Check if the battle is completed
        if not self.out1.alive() and not self.out2.alive():
            return Battle.Result.DRAW
        elif not self.out1.alive():
            return Battle.Result.TEAM2
        elif not self.out2.alive():
            return Battle.Result.TEAM1

        # Increment the turn number
        self.turn_number += 1
        return None

    def battle(self, team1: MonsterTeam, team2: MonsterTeam) -> Battle.Result:
        if self.verbosity > 0:
            print(f"Team 1: {team1} vs. Team 2: {team2}")
        # Add any pregame logic here.
        self.turn_number = 0
        self.team1 = team1
        # self.team1.regenerate_team()
        self.team2 = team2
        # self.team2.regenerate_team()
        self.out1 = team1.retrieve_from_team()
        self.out2 = team2.retrieve_from_team()
        result = None
        while result is None:
            result = self.process_turn()
        # Add any postgame logic here.
        return result

if __name__ == "__main__":
    t1 = MonsterTeam(MonsterTeam.TeamMode.BACK, MonsterTeam.SelectionMode.RANDOM)
    t2 = MonsterTeam(MonsterTeam.TeamMode.BACK, MonsterTeam.SelectionMode.RANDOM)
    b = Battle(verbosity=3)
    print(b.battle(t1, t2))
