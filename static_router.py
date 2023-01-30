from router import Router, RouterType
import random

class StaticRouter(Router):
    routes: dict[Router, Router]

    def __init__(self, type: RouterType, name: str) -> None:
        super().__init__(type, name)
        self.routes = {}

    def connect(self, other: "Router"):
        if self.type != other.type:
            super().connect(other)

    def set_route(self, destination: Router, path: Router):
        assert path in self.neighbors
        self.routes[destination] = path

    def route(self, destination: Router, path: list[Router] = None) -> list[Router] | None:
        if path is None:
            path = []
        else:
            # check for capacity
            connection = self.neighbors[path[-1]]
            if connection.amount == connection.capacity:
                return None

        if self is destination:
            return path + [self]

        if destination in self.neighbors:
            return destination.route(destination, path + [self])
        else:
            # next = random.choice(list(self.neighbors.keys()))
            # return next.route(destination, path + [self])
            return self.routes[destination].route(destination, path + [self])