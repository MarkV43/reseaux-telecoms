from itertools import pairwise
from router import Router, RouterType
from random import random


class LoadBalancerRouter(Router):
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
            if type(other) is LoadBalancerRouter:
                other.calculate_paths(routers)

    def route(self, destination: Router, path: list[Router] = None) -> list[Router] | None:
        if path is None:
            path = []
        else:
            # check for capacity
            connection = self.neighbors[path[-1]]
            count = 1
            for a, b in pairwise(path):
                if a.neighbors[b] is connection:
                    count += 1

            if not connection.can_receive(count):
                return None

        if self is destination:
            return path + [self]

        total = sum(1/x for r, x in self.network_distance[destination])
        rand = random() * total
        run = 0.0
        for r, x in self.network_distance[destination]:
            run += 1/x
            if rand < run:
                return r.route(destination, path + [self])
        
