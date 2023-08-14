from __future__ import annotations
import abc

from stats import Stats

class MonsterBase(abc.ABC):

    def __init__(self, simple_mode=True, level:int=1, reduced_hp:int=0) -> None:
        """
        Initialise an instance of a monster.

        :simple_mode: Whether to use the simple or complex stats of this monster
        :level: The starting level of this monster. Defaults to 1.
        """
        self.simple_mode = simple_mode
        self.level = level
        self.original_level = level
        self.hp = self.get_max_hp() - reduced_hp

    def __str__(self) -> str:
        return f"LV.{self.level} {self.get_name()}, {self.hp}/{self.get_max_hp()} HP"
    
    def get_level(self):
        """The current level of this monster instance"""
        return self.level

    def level_up(self):
        """Increase the level of this monster instance by 1"""
        reduced_hp = self.get_max_hp() - self.hp
        self.level += 1
        self.hp = self.get_max_hp() - reduced_hp

    def get_hp(self):
        """Get the current HP of this monster instance"""
        return self.hp

    def set_hp(self, val):
        """Set the current HP of this monster instance"""
        self.hp = val

    def get_attack(self):
        """Get the attack of this monster instance"""
        if self.simple_mode:
            return self.get_simple_stats().get_attack()
        else:
            return self.get_complex_stats().get_attack()

    def get_defense(self):
        """Get the defense of this monster instance"""
        if self.simple_mode:
            return self.get_simple_stats().get_defense()
        else:
            return self.get_complex_stats().get_defense()

    def get_speed(self):
        """Get the speed of this monster instance"""
        if self.simple_mode:
            return self.get_simple_stats().get_speed()
        else:
            return self.get_complex_stats().get_speed()
    def get_max_hp(self):
        """Get the maximum HP of this monster instance"""
        if self.simple_mode:
            return self.get_simple_stats().get_max_hp()
        else:
            return self.get_complex_stats().get_max_hp()

    def alive(self) -> bool:
        """Whether the current monster instance is alive (HP > 0 )"""
        return self.hp > 0

    def attack(self, other: MonsterBase):
        """Attack another monster instance"""
        # Step 1: Compute attack stat vs. defense stat
        attack_power = self.get_attack()
        defense_power = other.get_defense()
        damage = max(1, attack_power - defense_power)
        # Step 2: Apply type effectiveness
        # print(EffectivenessCalculator.get_effectiveness(Element.FIRE, Element.WATER))
        
        # Step 3: Ceil to int
        # Step 4: Lose HP
        other.set_hp(other.get_hp() - damage)

    def ready_to_evolve(self) -> bool:
        """Whether this monster is ready to evolve. See assignment spec for specific logic."""
        return (self.original_level != self.level) and (self.get_evolution() is not None)

    def evolve(self) -> MonsterBase:
        """Evolve this monster instance by returning a new instance of a monster class."""
        evolution_class = self.get_evolution()
        reduced_hp = self.get_max_hp() - self.hp
        return evolution_class(simple_mode=self.simple_mode, level=self.level, reduced_hp=reduced_hp)

    ### NOTE
    # Below is provided by the factory - classmethods
    # You do not need to implement them
    # And you can assume they have implementations in the above methods.

    @classmethod
    @abc.abstractmethod
    def get_name(cls) -> str:
        """Returns the name of the Monster - Same for all monsters of the same type."""
        pass

    @classmethod
    @abc.abstractmethod
    def get_description(cls) -> str:
        """Returns the description of the Monster - Same for all monsters of the same type."""
        pass

    @classmethod
    @abc.abstractmethod
    def get_evolution(cls) -> type[MonsterBase]:
        """
        Returns the class of the evolution of the Monster, if it exists.
        Same for all monsters of the same type.
        """
        pass

    @classmethod
    @abc.abstractmethod
    def get_element(cls) -> str:
        """
        Returns the element of the Monster.
        Same for all monsters of the same type.
        """
        pass

    @classmethod
    @abc.abstractmethod
    def can_be_spawned(cls) -> bool:
        """
        Returns whether this monster type can be spawned on a team.
        Same for all monsters of the same type.
        """
        pass

    @classmethod
    @abc.abstractmethod
    def get_simple_stats(cls) -> Stats:
        """
        Returns the simple stats class for this monster, if it exists.
        Same for all monsters of the same type.
        """
        pass

    @classmethod
    @abc.abstractmethod
    def get_complex_stats(cls) -> Stats:
        """
        Returns the complex stats class for this monster, if it exists.
        Same for all monsters of the same type.
        """
        pass
