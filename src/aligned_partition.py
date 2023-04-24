# Created on:  Thursday, April 24, 2023
# author:     Sourabh Bhat <heySourabh@gmail.com>

from typing import Union
from matplotlib import pyplot as plt
import numpy as np


def main():
    dims = 2
    num_points = 100
    min_coord = -2
    max_coord = 5
    np.random.seed(123)
    point_array = (max_coord - min_coord) * \
        np.random.random_sample((num_points, dims)) + min_coord
    points = [Point(p) for p in point_array]

    root = build_tree(points)

    # --- Visualization code below this line ---
    def z(x, y):
        p = np.zeros(dims)
        p[:2] = x, y
        return points.index(root.search(Point(p)).point)

    X, Y = np.meshgrid(np.linspace(min_coord, max_coord, 500),
                       np.linspace(min_coord, max_coord, 500))
    Z = np.zeros_like(X)
    for i in range(len(X)):
        for j in range(len(X[i])):
            x = X[i, j]
            y = Y[i, j]
            Z[i, j] = z(x, y)

    levels = np.linspace(0, num_points, min(num_points+1, 100)) - 0.5
    plt.contourf(X, Y, Z, levels=levels, cmap="turbo")
    plt.xlabel("x")
    plt.ylabel("y")
    cb = plt.colorbar(label="point index")
    cb.set_ticks((cb.get_ticks()+0.5)[:-1])
    cb.set_ticklabels(np.array(cb.get_ticks(), dtype=int))
    plt.gca().set_aspect("equal")
    plt.scatter(point_array[:, 0], point_array[:, 1], s=max(500/num_points, 1))
    plt.savefig(f"aligned_partitions_{num_points}_points.png")
    plt.show()
    plt.clf()


overlap_eps = 1e-12


class Point:
    def __init__(self, coordinates: np.ndarray) -> None:
        self.coordinates = coordinates

    def __str__(self) -> str:
        return f"Point{self.coordinates}"


class Split:
    def __init__(self, direction: int, location: float) -> None:
        self.direction = direction
        self.location = location

    def __str__(self) -> str:
        return f"Split[dir: {self.direction}, loc: {self.location}]"


class Children:
    def __init__(self, left: "Cell", right: "Cell", split: Split) -> None:
        self.left = left
        self.right = right
        self.split = split


class Cell:
    def __init__(self, point: Point) -> None:
        self.point: Point = point
        self.children: Union[Children, None] = None

    def add_point(self, point: Point) -> None:
        if self.children == None:
            p1 = point.coordinates
            p2 = self.point.coordinates
            distance = np.abs(p1[:] - p2[:])
            if np.sum(distance**2) < overlap_eps:
                raise ValueError("Overlapping / almost overlapping points.")
            split_direction = int(np.argmax(distance))
            split_location = (p1[split_direction] + p2[split_direction]) / 2
            split = Split(split_direction, split_location)
            if p1[split_direction] < split_location:
                left = Cell(point)
                right = Cell(self.point)
            else:
                left = Cell(self.point)
                right = Cell(point)
            self.children = Children(left, right, split)
        else:
            split = self.children.split
            split_direction = split.direction
            split_location = split.location
            if point.coordinates[split_direction] < split_location:
                self.children.left.add_point(point)
            else:
                self.children.right.add_point(point)

    def search(self, point: Point) -> "Cell":
        if self.children == None:
            return self
        else:
            split = self.children.split
            split_direction = split.direction
            split_location = split.location
            if point.coordinates[split_direction] < split_location:
                return self.children.left.search(point)
            else:
                return self.children.right.search(point)

    def __str__(self) -> str:
        if self.children == None:
            info = str(self.point)
        else:
            info = str(self.children.split)
        return "Cell: " + info


def build_tree(points: list[Point]) -> Cell:
    root = Cell(points[0])

    for point in points[1:]:
        root.add_point(point)

    return root


def print_tree(root: Cell) -> None:
    print(root)
    if root.children != None:
        print_tree(root.children.left)
        print_tree(root.children.right)


if __name__ == "__main__":
    main()
