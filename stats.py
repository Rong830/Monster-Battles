import abc
import math
from typing import List
from data_structures.referential_array import ArrayR

class Stats(abc.ABC):

    @abc.abstractmethod
    def get_attack(self):
        pass

    @abc.abstractmethod
    def get_defense(self):
        pass

    @abc.abstractmethod
    def get_speed(self):
        pass

    @abc.abstractmethod
    def get_max_hp(self):
        pass


class SimpleStats(Stats):

    def __init__(self, attack, defense, speed, max_hp):
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.max_hp = max_hp

    def get_attack(self):
        return self.attack

    def get_defense(self):
        return self.defense

    def get_speed(self):
        return self.speed

    def get_max_hp(self):
        return self.max_hp

class ComplexStats(Stats):

    def __init__(
        self,
        attack_formula: ArrayR[str],
        defense_formula: ArrayR[str],
        speed_formula: ArrayR[str],
        max_hp_formula: ArrayR[str],
    ) -> None:
        # TODO: Implement
        self.attack_formula = attack_formula
        self.defense_formula = defense_formula
        self.speed_formula = speed_formula
        self.max_hp_formula = max_hp_formula

    def evaluate_expression(self, expression: List[str], level: int) -> int:
        stack = []
        for token in expression:
            if token.isnumeric():
                stack.append(int(token))
            elif token == 'level':
                stack.append(level)
            elif token == '+':
                stack.append(stack.pop() + stack.pop())
            elif token == '-':
                b = stack.pop()
                a = stack.pop()
                stack.append(a - b)
            elif token == '*':
                stack.append(stack.pop() * stack.pop())
            elif token == '/':
                b = stack.pop()
                a = stack.pop()
                stack.append(a // b)
            elif token == 'power':
                b = stack.pop()
                a = stack.pop()
                stack.append(a ** b)
            elif token == 'sqrt':
                stack.append(int(math.sqrt(stack.pop())))
            elif token == 'middle':
                c = stack.pop()
                b = stack.pop()
                a = stack.pop()
                stack.append(int(sorted([a, b, c])[1]))
        return stack.pop()

    def get_attack(self, level: int):
        return self.evaluate_expression(self.attack_formula, level)

    def get_defense(self, level: int):
        return self.evaluate_expression(self.defense_formula, level)

    def get_speed(self, level: int):
        return self.evaluate_expression(self.speed_formula, level)

    def get_max_hp(self, level: int):
        return self.evaluate_expression(self.max_hp_formula, level)
