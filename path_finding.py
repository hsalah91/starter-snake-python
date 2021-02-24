from queue import PriorityQueue

from dto import *
from utils import are_cells_equal, dist_between_cells, DX, DY


def is_cell_achievable(cell: Cell, board: Board, deep: int = 1) -> bool:
    # board limits
    if cell.x == -1 or cell.y == -1:
        return False

    if cell.x >= board.width or cell.y >= board.height:
        return False

    # hazards
    for hazard in board.hazards:
        if are_cells_equal(cell, hazard):
            return False

    # if we will be in the cell in {deep} steps, then this part of tail can be skipped
    for snake in board.snakes:
        for c in snake.body[:-deep]:
            if are_cells_equal(c, cell):
                return False

    return True


def dijkstra_modified(cell1: Cell, cell2: Cell, board: Board) -> List[Cell]:
    path = PriorityQueue()
    path.put((0, cell1))
    prev_step = {cell1: None}
    current_cost = {cell1: 0}

    while not path.empty():
        current = path.get()[1]

        if current == cell2:
            break

        for i in range(4):
            next_cell = Cell(current.x + DX[i], current.y + DY[i])
            if not is_cell_achievable(next_cell, board, current_cost[current] + 1):
                continue

            new_cost = current_cost[current] + 1
            if next_cell not in current_cost or new_cost < current_cost[next_cell]:
                current_cost[next_cell] = new_cost
                priority = new_cost + dist_between_cells(cell2, next_cell)
                path.put((priority, next_cell))
                prev_step[next_cell] = current

    # restore path
    if cell2 not in current_cost:
        return []

    path = []
    current = cell2
    while current:
        path.append(current)
        current = prev_step[current]

    return path[::-1]