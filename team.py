from __future__ import annotations
from enum import auto
from typing import Optional, TYPE_CHECKING

from base_enum import BaseEnum
from monster_base import MonsterBase
from random_gen import RandomGen
from helpers import get_all_monsters

from data_structures.referential_array import ArrayR

if TYPE_CHECKING:
    from battle import Battle

class MonsterTeam:

    class TeamMode(BaseEnum):

        FRONT = auto()
        BACK = auto()
        OPTIMISE = auto()

    class SelectionMode(BaseEnum):

        RANDOM = auto()
        MANUAL = auto()
        PROVIDED = auto()

    class SortMode(BaseEnum):

        HP = auto()
        ATTACK = auto()
        DEFENSE = auto()
        SPEED = auto()
        LEVEL = auto()

    TEAM_LIMIT = 6

    def __init__(self, team_mode: TeamMode, selection_mode, **kwargs) -> None:
        # Add any preinit logic here.
        self.team_mode = team_mode
        self.monster_order = ArrayR(self.TEAM_LIMIT)
        self.current_size = 0
        if 'provided_monsters' in kwargs:
            self.provided_monsters = kwargs.get("provided_monsters")
        else:
            self.provided_monsters = None

        if selection_mode == self.SelectionMode.RANDOM:
            self.select_randomly(**kwargs)
        elif selection_mode == self.SelectionMode.MANUAL:
            self.select_manually(**kwargs)
        elif selection_mode == self.SelectionMode.PROVIDED:
            self.select_provided(**kwargs)
        else:
            raise ValueError(f"selection_mode {selection_mode} not supported.")

    def _get_sort_key_method(self):
        if self.sort_key == self.SortMode.HP:
            return lambda monster: monster.get_hp()
        elif self.sort_key == self.SortMode.ATTACK:
            return lambda monster: monster.get_attack()
        elif self.sort_key == self.SortMode.DEFENSE:
            return lambda monster: monster.get_defense()
        elif self.sort_key == self.SortMode.SPEED:
            return lambda monster: monster.get_speed()
        elif self.sort_key == self.SortMode.LEVEL:
            return lambda monster: monster.get_level()
        
    def add_to_team(self, monster: MonsterBase):
        if self.current_size >= self.TEAM_LIMIT:
            raise ValueError("Team is already at maximum capacity.")

        if self.team_mode == self.TeamMode.FRONT:
            for i in range(self.current_size, 0, -1):
                self.monster_order[i] = self.monster_order[i - 1]
            self.monster_order[0] = monster
        elif self.team_mode == self.TeamMode.BACK:
            self.monster_order[self.current_size] = monster
        elif self.team_mode == self.TeamMode.OPTIMISE:
            # Find the position to insert the monster based on the sorting stat
            insert_position = 0
            sort_key_method = self._get_sort_key_method()  # Retrieve the appropriate method
            
            while (
                insert_position < self.current_size
                and sort_key_method(monster) < sort_key_method(self.monster_order[insert_position])
            ):
                insert_position += 1
            
            # Shift elements manually to make space for the new monster
            for i in range(self.current_size, insert_position, -1):
                self.monster_order[i] = self.monster_order[i - 1]

            # Insert the monster at the correct position
            self.monster_order[insert_position] = monster

        self.current_size += 1

    def retrieve_from_team(self) -> MonsterBase:
        if self.current_size == 0:
            return self.monster_order[0]

        retrieved_monster = self.monster_order[0]

        if self.team_mode == self.TeamMode.FRONT:
            # Shift remaining monsters to the left
            for i in range(self.current_size - 1):
                self.monster_order[i] = self.monster_order[i + 1]
        elif self.team_mode == self.TeamMode.BACK:
            # Shift remaining monsters to the left (excluding the last one)
            for i in range(1, self.current_size):
                self.monster_order[i - 1] = self.monster_order[i]
        elif self.team_mode == self.TeamMode.OPTIMISE:
            for i in range(self.current_size - 1):
                self.monster_order[i] = self.monster_order[i + 1]

        self.current_size -= 1

        return retrieved_monster

    def special(self) -> None:
        middle_index = self.current_size // 2

        if self.team_mode == self.TeamMode.FRONT:
            self.monster_order[0], self.monster_order[middle_index] = self.monster_order[middle_index], self.monster_order[0]

        elif self.team_mode == self.TeamMode.BACK:
            for i in range(middle_index):
                j = self.current_size - i - 1
                x = self.monster_order[i]
                y = self.monster_order[j]
                self.monster_order[j] = x
                self.monster_order[i] = y
            if middle_index > 1:
                if (self.current_size % 2) == 0:
                    self.monster_order[middle_index], self.monster_order[self.current_size-1] = self.monster_order[self.current_size-1], self.monster_order[middle_index]
                else:
                    self.monster_order[middle_index+1], self.monster_order[self.current_size-1] = self.monster_order[self.current_size-1], self.monster_order[middle_index+1]

        elif self.team_mode == self.TeamMode.OPTIMISE:
            sort_key_method = self._get_sort_key_method()  # Retrieve the appropriate method

            index_dict = {
                monster: sort_key_method(monster)
                for monster in self.monster_order
                if monster is not None
            }
            monsters = sorted(index_dict, key=lambda x: index_dict[x])
            for i, monster in enumerate(monsters):
                self.monster_order[i] = monster

    def regenerate_team(self) -> None:
        if self.provided_monsters:
            for i in range(self.TEAM_LIMIT):
                self.monster_order[i] = None

            self.current_size = 0
            for i, m in enumerate(self.provided_monsters):
                if self.team_mode == self.TeamMode.FRONT:
                    num = len(self.provided_monsters)
                    self.monster_order[num-i-1] = m()
                    self.monster_order[num-i-1].level = 1  # Reset to level 1
                    self.monster_order[num-i-1].hp = self.monster_order[num-i-1].get_max_hp()  # Restore full health

                elif self.team_mode == self.TeamMode.BACK:
                    self.monster_order[i] = m()
                    self.monster_order[i].level = 1  # Reset to level 1
                    self.monster_order[i].hp = self.monster_order[i].get_max_hp()  # Restore full health
                self.current_size += 1
            return 
        for i in range(self.current_size):
            self.monster_order[i].level = 1  # Reset to level 1
            self.monster_order[i].hp = self.monster_order[i].get_max_hp()  # Restore full health

    def select_randomly(self, sort_key=None):
        self.sort_key = sort_key

        team_size = RandomGen.randint(1, self.TEAM_LIMIT)
        monsters = get_all_monsters()
        n_spawnable = 0
        for x in range(len(monsters)):
            if monsters[x].can_be_spawned():
                n_spawnable += 1

        for _ in range(team_size):
            spawner_index = RandomGen.randint(0, n_spawnable-1)
            cur_index = -1
            for x in range(len(monsters)):
                if monsters[x].can_be_spawned():
                    cur_index += 1
                    if cur_index == spawner_index:
                        # Spawn this monster
                        self.add_to_team(monsters[x]())
                        break
            else:
                raise ValueError("Spawning logic failed.")

    def select_manually(self, sort_key=None):
        """
        Prompt the user for input on selecting the team.
        Any invalid input should have the code prompt the user again.

        First input: Team size. Single integer
        For _ in range(team size):
            Next input: Prompt selection of a Monster class.
                * Should take a single input, asking for an integer.
                    This integer corresponds to an index (1-indexed) of the helpers method
                    get_all_monsters()
                * If invalid of monster is not spawnable, should ask again.

        Add these monsters to the team in the same order input was provided. Example interaction:

        How many monsters are there? 2
        MONSTERS Are:
        1: Flamikin [✔️]
        2: Infernoth [❌]
        3: Infernox [❌]
        4: Aquariuma [✔️]
        5: Marititan [❌]
        6: Leviatitan [❌]
        7: Vineon [✔️]
        8: Treetower [❌]
        9: Treemendous [❌]
        10: Rockodile [✔️]
        11: Stonemountain [❌]
        12: Gustwing [✔️]
        13: Stormeagle [❌]
        14: Frostbite [✔️]
        15: Blizzarus [❌]
        16: Thundrake [✔️]
        17: Thunderdrake [❌]
        18: Shadowcat [✔️]
        19: Nightpanther [❌]
        20: Mystifly [✔️]
        21: Telekite [❌]
        22: Metalhorn [✔️]
        23: Ironclad [❌]
        24: Normake [❌]
        25: Strikeon [✔️]
        26: Venomcoil [✔️]
        27: Pythondra [✔️]
        28: Constriclaw [✔️]
        29: Shockserpent [✔️]
        30: Driftsnake [✔️]
        31: Aquanake [✔️]
        32: Flameserpent [✔️]
        33: Leafadder [✔️]
        34: Iceviper [✔️]
        35: Rockpython [✔️]
        36: Soundcobra [✔️]
        37: Psychosnake [✔️]
        38: Groundviper [✔️]
        39: Faeboa [✔️]
        40: Bugrattler [✔️]
        41: Darkadder [✔️]
        Which monster are you spawning? 38
        MONSTERS Are:
        1: Flamikin [✔️]
        2: Infernoth [❌]
        3: Infernox [❌]
        4: Aquariuma [✔️]
        5: Marititan [❌]
        6: Leviatitan [❌]
        7: Vineon [✔️]
        8: Treetower [❌]
        9: Treemendous [❌]
        10: Rockodile [✔️]
        11: Stonemountain [❌]
        12: Gustwing [✔️]
        13: Stormeagle [❌]
        14: Frostbite [✔️]
        15: Blizzarus [❌]
        16: Thundrake [✔️]
        17: Thunderdrake [❌]
        18: Shadowcat [✔️]
        19: Nightpanther [❌]
        20: Mystifly [✔️]
        21: Telekite [❌]
        22: Metalhorn [✔️]
        23: Ironclad [❌]
        24: Normake [❌]
        25: Strikeon [✔️]
        26: Venomcoil [✔️]
        27: Pythondra [✔️]
        28: Constriclaw [✔️]
        29: Shockserpent [✔️]
        30: Driftsnake [✔️]
        31: Aquanake [✔️]
        32: Flameserpent [✔️]
        33: Leafadder [✔️]
        34: Iceviper [✔️]
        35: Rockpython [✔️]
        36: Soundcobra [✔️]
        37: Psychosnake [✔️]
        38: Groundviper [✔️]
        39: Faeboa [✔️]
        40: Bugrattler [✔️]
        41: Darkadder [✔️]
        Which monster are you spawning? 2
        This monster cannot be spawned.
        Which monster are you spawning? 1
        """
        self.sort_key = sort_key
        team_size = int(input("How many monsters are there? "))
        while team_size > self.TEAM_LIMIT:
            print("Too many monsters.")
            team_size = int(input("How many monsters are there? "))

        print("MONSTERS ARE:")
        monsters = get_all_monsters()
        for i, monster_cls in enumerate(monsters, start=1):
            spawnable = "✔️" if monster_cls.can_be_spawned() else "❌"
            print(f"{i}: {monster_cls.get_name()} [{spawnable}]")
        
        for _ in range(team_size):
            while True:
                selection = int(input("Which monster are you spawning? "))
                if selection < 1 or selection > len(monsters):
                    print("Invalid selection. Please choose a valid index.")
                    continue
                
                monster_cls = monsters[selection - 1]
                if not monster_cls.can_be_spawned():
                    print("This monster cannot be spawned.")
                else:
                    self.add_to_team(monster_cls())
                    break

    def select_provided(self, provided_monsters:Optional[ArrayR[type[MonsterBase]]]=None, sort_key=None):
        """
        Generates a team based on a list of already provided monster classes.

        While the type hint imples the argument can be none, this method should never be called without the list.
        Monsters should be added to the team in the same order as the provided array.

        Example input:
        [Flamikin, Aquariuma, Gustwing] <- These are all classes.

        Example team if in TeamMode.FRONT:
        [Gustwing Instance, Aquariuma Instance, Flamikin Instance]
        """
        self.sort_key = sort_key
        if not provided_monsters:
            raise ValueError("No provided monsters found.")
        
        for monster_class in provided_monsters:
            monster = monster_class()
            if not monster.can_be_spawned():
                raise ValueError("Monster not esits.")
            self.add_to_team(monster)

    def choose_action(self, currently_out: MonsterBase, enemy: MonsterBase) -> Battle.Action:
        # This is just a placeholder function that doesn't matter much for testing.
        from battle import Battle
        if currently_out.get_speed() >= enemy.get_speed() or currently_out.get_hp() >= enemy.get_hp():
            return Battle.Action.ATTACK
        return Battle.Action.SWAP

    def __len__(self) -> int:
        return self.current_size
    

if __name__ == "__main__":
    team = MonsterTeam(
        team_mode=MonsterTeam.TeamMode.OPTIMISE,
        selection_mode=MonsterTeam.SelectionMode.RANDOM,
        sort_key=MonsterTeam.SortMode.HP,
    )
    print(team)
    while len(team):
        print(team.retrieve_from_team())
