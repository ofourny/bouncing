import pygame

class Quadtree:
    def __init__(self, boundary, capacity):
        self.boundary = boundary  # Boundary is a pygame.Rect
        self.capacity = capacity
        self.balls = []
        self.divided = False

    def subdivide(self):
        x, y, w, h = self.boundary
        nw = pygame.Rect(x, y, w / 2, h / 2)
        ne = pygame.Rect(x + w / 2, y, w / 2, h / 2)
        sw = pygame.Rect(x, y + h / 2, w / 2, h / 2)
        se = pygame.Rect(x + w / 2, y + h / 2, w / 2, h / 2)

        self.northwest = Quadtree(nw, self.capacity)
        self.northeast = Quadtree(ne, self.capacity)
        self.southwest = Quadtree(sw, self.capacity)
        self.southeast = Quadtree(se, self.capacity)
        self.divided = True

    def insert(self, ball):
        if not self.boundary.collidepoint(ball['pos']):
            return False

        if len(self.balls) < self.capacity:
            self.balls.append(ball)
            return True
        if not self.divided:
            self.subdivide()

        return (self.northwest.insert(ball) or
                self.northeast.insert(ball) or
                self.southwest.insert(ball) or
                self.southeast.insert(ball))

    def query(self, range, found):
        if not self.boundary.colliderect(range):
            return

        for ball in self.balls:
            if range.collidepoint(ball['pos']):
                found.append(ball)

        if self.divided:
            self.northwest.query(range, found)
            self.northeast.query(range, found)
            self.southwest.query(range, found)
            self.southeast.query(range, found)

    def clear(self):
        self.balls.clear()
        if self.divided:
            self.northwest.clear()
            self.northeast.clear()
            self.southwest.clear()
            self.southeast.clear()
            self.divided = False
