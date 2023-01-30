from itertools import pairwise
from router import Router, RouterType
from random import random


class AdaptiveRouter(Router):
    network_distance: dict[Router, list[tuple[Router, int]]]

    def __init__(self, type: RouterType, name: str) -> None:
        super().__init__(type, name)
        self.network_distance = {}
    
    def connect(self, other: Router):
        super().connect(other)

    def calculate_paths(self, routers: list[Router]):
        if len(self.network_distance) > 0:
            return

        for other in routers:
            if other is self:
                continue

            distances = []
            if other in self.neighbors:
                distances += [(other, 1)]

            for neigh in self.neighbors:
                if other in neigh.neighbors:
                    distances += [(neigh, 2)]
            
            self.network_distance[other] = distances

        for other in self.neighbors:
            if type(other) is AdaptiveRouter:
                other.calculate_paths(routers)

    def find_shortest_paths(self, destination: Router, min: int, sec: int) -> list[list[Router]]:
        # Ne prenez en compte les liens plein

        paths = []
        
        # Chercher un chemin de longueur 1
        for neigh, conn in self.neighbors.items():
            if neigh is destination and not conn.was_full_at(min, sec):
                paths.append([self, neigh])
        
        if len(paths) > 0:
            return paths

        for n1, c1 in self.neighbors.items():
            if c1.was_full_at(min, sec):
                continue
            for n2, c2 in n1.neighbors.items():
                if c2.was_full_at(min, sec):
                    continue
                if n2 is destination:
                    paths.append([self, n1, n2])
        
        return paths

    def number_of_free_spots(path: list[Router], min: int, sec: int) -> int:
        spots = -1

        assert type(path) is list

        for a, b in pairwise(path):
            conn = a.neighbors[b]
            free_space = conn.free_space_at(min, sec)

            if spots == -1 or free_space < spots:
                spots = free_space
        
        return spots
                

    def route(self, destination: Router, min: int, sec: int, delay: int = 3) -> list[Router] | None:
        # identify the desired moment
        sec -= delay
        if sec < 0:
            sec += 60
            min -= 1
            if min < 0:
                sec = 0
                min = 0

        # chercher les plus courts chemins
        paths = self.find_shortest_paths(destination, min, sec)

        # arg    max ( min (placeLibre) )
        # C1    liens de C1
        max_spots = 0
        best_path = None
        for path in paths:
            spots = AdaptiveRouter.number_of_free_spots(path, min, sec)

            if spots > max_spots:
                max_spots = spots
                best_path = path
        
        if best_path is None:
            return None

        # Check if the chosen path is still valid on the present
        for a, b in pairwise(best_path):
            if a.neighbors[b].is_full():
                return None
        
        # It's ok to return None here
        return best_path

    def save_all(self, min: int, sec: int, depth: int=3):
        if depth == 0:
            return

        for n, c in self.neighbors.items():
            c.save_moment(min, sec)

            if type(n) is AdaptiveRouter:
                n.save_all(min, sec, depth-1)
