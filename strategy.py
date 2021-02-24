import random

from dto import *
from utils import are_cells_equal, dist_between_cells, find_move_between_cells, DX, DY
from path_finding import dijkstra_modified


def make_next_move(request: MovePostRequest) -> Move:
    # print('Doing move for')
    # print(request.to_json())

    # decide where to go
    move_to_food = find_move_to_food(request)
    if move_to_food:
        return move_to_food

    # if can't decide - just make safe move
    if safe_move(request, Move.up):
        return Move.up
    elif safe_move(request, Move.down):
        return Move.down
    elif safe_move(request, Move.left):
        return Move.left
    elif safe_move(request, Move.right):
        return Move.right

    # make almost safe move
    if safe_move(request, Move.up, True):
        return Move.up
    elif safe_move(request, Move.down, True):
        return Move.down
    elif safe_move(request, Move.left, True):
        return Move.left
    elif safe_move(request, Move.right, True):
        return Move.right

    print('NO TURNS, WE GONNA COLLAPSE!')

    # Choose a random direction to move in
    possible_moves = [Move.up, Move.down, Move.left, Move.right]
    move = random.choice(possible_moves)
    return move


def safe_move(request: MovePostRequest, move: Move, skip_enemies_possible_moves: bool = False) -> bool:
    my_head = request.you.head

    if move == Move.up:
        move_to = Cell(my_head.x, my_head.y + 1)
    elif move == Move.down:
        move_to = Cell(my_head.x, my_head.y - 1)
    elif move == Move.left:
        move_to = Cell(my_head.x - 1, my_head.y)
    else:
        move_to = Cell(my_head.x + 1, my_head.y)

    # validate self collision, except the tail
    for coord in request.you.body[:-1]:
        if are_cells_equal(move_to, coord):
            return False

    # validate walls
    if move_to.x == request.board.width or move_to.x == -1 or move_to.y == request.board.height or move_to.y == -1:
        return False

    # validate other snakes body
    for snake in request.board.snakes:
        if snake.id == request.you.id:
            continue

        # move to the place where enemy tail was is allowed
        for enemy_snake_coord in snake.body[:-1]:
            if are_cells_equal(move_to, enemy_snake_coord):
                return False

    # validate other snakes possible moves
    if not skip_enemies_possible_moves:
        for snake in request.board.snakes:
            if snake.id == request.you.id:
                continue

            if snake.length < request.you.length:
                # smaller snakes are not a danger
                continue

            for i in range(4):
                dx = DX[i]
                dy = DY[i]
                possible_enemy_turn = Cell(snake.head.x + dx, snake.head.y + dy)
                if are_cells_equal(move_to, possible_enemy_turn):
                    return False

    return True


def do_we_want_nearest_food(request: MovePostRequest) -> bool:
    if request.you.health <= 60:
        return True
    else:
        max_snake_size = 0
        for v in request.board.snakes:
            if v.id != request.you.id:
                max_snake_size = max(max_snake_size, v.length)

        return max_snake_size >= request.you.length


def find_desired_food(request: MovePostRequest):
    if do_we_want_nearest_food(request):
        # find nearest food
        operation = lambda x, y: x < y
    else:
        # find furthest food
        operation = lambda x, y: x > y

    my_head = request.you.head
    desired_food = request.board.food[0]
    best_dist = dist_between_cells(my_head, desired_food)
    for food in request.board.food:
        if food in request.board.hazards:
            # hazarded food is not good for us
            continue

        dist = dist_between_cells(food, my_head)
        if operation(dist, best_dist):
            best_dist = dist
            desired_food = food

    return desired_food


def not_snake_or_hazard(cell, board):
    if cell in board.hazards:
        return False
    for snake in board.snakes:
        if cell in snake.body:
            return False

    return True;


def calculate_food_safety_score(food, board):
    score = 0
    margin = 6
    # get bottom left as we treat the food as if it is in the center
    start_x = food.x - margin/2
    start_y = food.y - margin/2
    for i in range(margin):
        for j in range(margin):
            if not_snake_or_hazard(Cell(start_x + i, start_y + j), board):
                score+= 1
    return score

def calculate_score(food, board ,request):
    score = 0;
    distance_from_my_head = dist_between_cells(food, request.you.head) + 1
    safety = calculate_food_safety_score(food, board)
    health = request.you.health

    score = (1/health) + (1/distance_from_my_head) + safety
    score = score * 1000
    return score

def evaluate_food(board, request: MovePostRequest):
    ranked_food = []
    for food in board.food:
        if food in board.hazards:
            # hazarded food is not good for us
            ranked_food.append(RankedCell(Cell(food.x, food.y), -1))
        else:
            ranked_food.append(RankedCell(Cell(food.x, food.y), calculate_score(food, board ,request)))


    desired_food = ranked_food[0]
    for food in ranked_food:
        desired_food = max(food, desired_food)

    print('desired foooood')
    print(desired_food)
    return desired_food.cell



def find_desired_food_far_from_enemies(request: MovePostRequest):
    my_head = request.you.head
    desired_food = request.board.food[0]
    best_dist = 0
    for food in request.board.food:
        if food in request.board.hazards:
            # hazarded food is not good for us
            continue

        min_dist = 1000000
        our_dist = dist_between_cells(my_head, food)
        for snake in request.board.snakes:
            if snake.id == request.you.id:
                continue

            min_dist = min(min_dist, dist_between_cells(snake.head, food))

        if our_dist < min_dist and best_dist < min_dist:
            best_dist = min_dist
            desired_food = food

    return desired_food



def find_move_to_food(request: MovePostRequest):
    if not request.board.food:
        # no food in the board ... instead  chase tail ?
        return None

    my_head = request.you.head
    desired_food = evaluate_food(request.board, request)

    # find path to the food
    path = dijkstra_modified(my_head, desired_food, request.board, request.you.id)
    if not path:
        return None

    move = find_move_between_cells(path[0], path[1])
    if safe_move(request, move):
        return move
    else:
        return None # no food in the board ... instead  chase tail more safe ?
