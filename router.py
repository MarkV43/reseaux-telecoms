from abc import ABC, abstractmethod
from enum import Enum


class RouterType(Enum):
    CA = 0
    CTS = 1

class Connection:
    history: dict[tuple[int, int], int]
    amount: int
    capacity: int

    def __init__(self, amount: int, capacity: int) -> None:
        self.amount = amount
        self.capacity = capacity
        self.history = {}

    def reset(self):
        self.amount = 0

    def increment(self) -> bool:
        assert 0 <= self.amount <= self.capacity

        if self.amount < self.capacity:
            self.amount += 1
            return True
        else:
            return False

    def decrement(self):
        assert 0 <= self.amount <= self.capacity

        if self.amount > 0:
            self.amount -= 1
            return True
        else:
            return False

    def can_receive(self, amount) -> bool:
        assert 0 <= self.amount <= self.capacity

        return self.amount + amount <= self.capacity

    def is_full(self) -> bool:
        assert 0 <= self.amount <= self.capacity

        return self.amount == self.capacity

    def was_full_at(self, min: int, sec: int) -> bool:
        assert 0 <= self.amount <= self.capacity

        return self.history[(min, sec)] == self.capacity

    def amount_connexions_at(self, min: int, sec: int) -> int:
        assert 0 <= self.amount <= self.capacity

        return self.history[(min, sec)]

    def save_moment(self, min: int, sec: int):
        assert 0 <= self.amount <= self.capacity

        self.history[(min, sec)] = self.amount
    
    def free_space(self) -> int:
        assert 0 <= self.amount <= self.capacity

        return self.capacity - self.amount

    def free_space_at(self, min: int, sec: int) -> int:
        assert 0 <= self.amount <= self.capacity

        return self.capacity - self.history[(min, sec)]


class Router(ABC):
    name: str
    type: RouterType
    neighbors: dict["Router", Connection]

    def __init__(self, type: RouterType, name: str) -> None:
        self.neighbors = {}
        self.type = type
        self.name = name

    def connect(self, other: "Router"):
        if self.type == other.type:
            if self.type == RouterType.CA:
                capacity = 10
            else:
                capacity = 1000
        else:
            capacity = 100

        connection = Connection(0, capacity)

        self.neighbors[other] = connection
        other.neighbors[self] = connection

    def reset(self):
        for neigh in self.neighbors.values():
            neigh.reset()

    @abstractmethod
    def route(self, destination: "Router", path: list["Router"] = None) -> list["Router"] | None:
        ...

    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return self.name