from dto import *


DX = [0, 0, -1, 1]
DY = [1, -1, 0, 0]


def are_cells_equal(cell1: Cell, cell2: Cell) -> bool:
    return cell1.x == cell2.x and cell1.y == cell2.y


def dist_between_cells(cell1: Cell, cell2: Cell) -> int:
    return abs(cell1.x - cell2.x) + abs(cell1.y - cell2.y)


def find_move_between_cells(cell1: Cell, cell2: Cell) -> Move:
    assert (abs(cell1.x - cell2.x) + abs(cell1.y - cell2.y) == 1)
    dx = cell2.x - cell1.x
    if dx == 1:
        return Move.right
    elif dx == -1:
        return Move.left

    dy = cell2.y - cell1.y
    if dy == 1:
        return Move.up
    elif dy == -1:
        return Move.down