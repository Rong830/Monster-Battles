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
        import math
        # Process actions chosen by each team
        action_team1 = self.team1.choose_action(self.out1, self.out2)
        action_team2 = self.team2.choose_action(self.out2, self.out1)

        print(self.out1, self.out1.get_attack(), self.out1.get_defense(), ' VS ', 
              self.out2, self.out2.get_attack(), self.out2.get_defense(), 'Begain!!!')

        def compute_damage(m1, m2):
            '''
            If defense < attack / 2: damage = attack - defense
            Otherwise, If defence < attack: damage = attack * 5/8 - defense / 4
            Otherwise, damage = attack / 4
            '''
            attack = m1.get_attack()
            defense = m2.get_defense()
            if defense < (attack / 2):
                return math.ceil(attack - defense)
            elif defense < attack:
                return math.ceil((attack * 5/8) - (defense / 4))
            else:
                return math.ceil(attack / 4)

        # Compare speed
        if self.out1.get_speed() >= self.out2.get_speed():
            # Handle actions
            if action_team1 == Battle.Action.ATTACK:
                damage = compute_damage(self.out1, self.out2)
                self.out2.hp -= damage                    
                print(f'{self.out2} takes {damage} damage from {self.out1}')
            elif action_team1 == Battle.Action.SWAP:
                self.out1 = self.team1.retrieve_from_team()
            if self.out2.alive():
                if action_team2 == Battle.Action.ATTACK:
                    damage = compute_damage(self.out2, self.out1)
                    self.out1.hp -= damage
                    print(f'{self.out1} takes {damage} damage from {self.out2}')
                elif action_team2 == Battle.Action.SWAP:
                    self.out2 = self.team2.retrieve_from_team()
        elif self.out1.get_speed() < self.out2.get_speed():
            if action_team2 == Battle.Action.ATTACK:
                damage = compute_damage(self.out2, self.out1)
                self.out1.hp -= damage
                print(f'{self.out1} takes {damage} damage from {self.out2}')
            elif action_team2 == Battle.Action.SWAP:
                self.out2 = self.team2.retrieve_from_team()
            if self.out1.alive():
                if action_team1 == Battle.Action.ATTACK:
                    damage = compute_damage(self.out1, self.out2)
                    self.out2.hp -= damage
                    print(f'{self.out2} takes {damage} damage from {self.out1}')
                elif action_team1 == Battle.Action.SWAP:
                    self.out1 = self.team1.retrieve_from_team()


        # Subtract 1 from HP if both survive
        if self.out1.alive() and self.out2.alive():
            print(f'{self.out1} and {self.out2} both alive and take 1 damage')
            self.out1.hp -= 1
            self.out2.hp -= 1

        if self.out1.alive() and (not self.out2.alive()):
            self.out1.level_up()
        elif self.out2.alive() and (not self.out1.alive()):
            self.out2.level_up()

        # Handle level ups and evolutions
        if self.out1.ready_to_evolve():
            print(f'{self.out1} evolve to {self.out1.evolve()}')
            self.out1 = self.out1.evolve()
        if self.out2.ready_to_evolve():
            print(f'{self.out2} evolve to {self.out2.evolve()}')
            self.out2 = self.out2.evolve()

        # Check if any monsters fainted and replace them
        if not self.out1.alive():
            print(f'{self.out1} fainted')
            self.out1 = self.team1.retrieve_from_team()
        if not self.out2.alive():
            print(f'{self.out2} fainted')
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
        print(self.out1, self.out2, 'One round end!!!!')
        return None

    def battle(self, team1: MonsterTeam, team2: MonsterTeam) -> Battle.Result:
        if self.verbosity > 0:
            print(f"Team 1: {team1} vs. Team 2: {team2}")
            print(f"Team 1: {team1.monster_order}")
            print(f"Team 2: {team2.monster_order}")
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
