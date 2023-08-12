import pygame
import random
import math

class Tile:
    """A tile."""
    value: int
    def __init__(self, value=2):
        self.value = value
    def merge(self, other) -> bool:
        """Merge this tile with <other>."""
        if self.value == other.value:
            self.value *= 2
            return True
        return False


# Helper function for class Board
def _move_position(position: tuple[int, int], direction: tuple[int, int]) -> tuple[int, int]:
    """Return the position after moving <direction> from <position>."""
    return position[0] + direction[0], position[1] + direction[1]


class Board:
    """A board."""
    width: int
    height: int
    board: list[list[Tile | None]]

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[None for i in range(width)] for j in range(height)]


    # Private helper functions below
    def _is_valid(self, position: tuple[int, int]) -> bool:
        """Return whether <position> is a valid position on the board."""
        return 0 <= position[0] < self.width and 0 <= position[1] < self.height

    def _find_starts(self, direction: tuple[int, int]) -> list[tuple[int, int]]:
        """With a direction, find the set of positions to start merging."""
        # Start at (0, 0) and move in <direction> until we hit the edge of the board.

        side = (max(0, direction[0] * (self.width - 1)), max(0, direction[1] * (self.height - 1)))
        starts = []
        if direction[0] == 0:
            for x in range(self.width):
                starts.append((x, side[1]))
        elif direction[1] == 0:
            for y in range(self.height):
                starts.append((side[0], y))
        return starts

    def _get(self, position: tuple[int, int]) -> Tile | None:
        """Return the tile at <position>."""
        return self.board[position[0]][position[1]]

    def _set(self, position: tuple[int, int], tile: Tile | None) -> None:
        """Set the tile at <position> to <tile>."""
        self.board[position[0]][position[1]] = tile

    def _compact(self, direction: tuple[int, int]) -> bool:
        something_changed = False
        for i in range(max(self.width, self.height)):
            for x in range(self.width):
                for y in range(self.height):

                    if self.board[x][y] is None:
                        continue
                    curr_pos = (x, y)
                    next_pos = _move_position(curr_pos, direction)

                    while self._is_valid(next_pos) and self._get(next_pos) is None:
                        self._set(next_pos, self._get(curr_pos))
                        self._set(curr_pos, None)
                        curr_pos = next_pos
                        next_pos = _move_position(curr_pos, direction)
                        something_changed = True

        return something_changed

    def spawn(self) -> bool:
        """Spawn a new tile."""
        options = []
        for x in range(self.width):
            for y in range(self.height):
                if self.board[x][y] is None:
                    options.append((x, y))
        if len(options) == 0:
            return False

        x, y = random.choice(options)
        self.board[x][y] = Tile()

        # self.board[x][y] = Tile(512)  # for testing
        if random.random() < 0.1:
            self.board[x][y] = Tile(4)

    def move(self, direction: tuple[int, int]) -> None:
        """Move the board in <direction>."""
        # if abs(direction[0]) > 1 or abs(direction[1]) > 1:
        #     return False
        something_changed = self._compact(direction)

        inverse = (-direction[0], -direction[1])
        starts = self._find_starts(direction)

        for start in starts:

            curr_pos = start
            next_pos = _move_position(curr_pos, inverse)

            while self._is_valid(next_pos):
                x, y = curr_pos
                x2, y2 = next_pos

                first_tile = self.board[x][y]
                second_tile = self.board[x2][y2]

                if first_tile is None or second_tile is None:
                    curr_pos = next_pos
                    next_pos = _move_position(curr_pos, inverse)
                    continue

                if first_tile.merge(second_tile):
                    self.board[x2][y2] = None
                    something_changed = True

                curr_pos = next_pos
                next_pos = _move_position(curr_pos, inverse)

        something_changed = self._compact(direction) or something_changed

        if something_changed:
            self.spawn()

    def draw(self, screen: pygame.Surface, colour_choice: str) -> None:
        """Draw the board on <screen>."""
        for x in range(self.width):
            for y in range(self.height):
                tile = self.board[x][y]
                if tile is None:
                    continue

                # Colour Shade is proportional to the value of the tile. Use log.
                shade = min(255, int(math.log(tile.value, 2) * (255 / 10)))

                if colour_choice == 'red':
                    colour = (255, 255 - shade, 255 - shade)
                elif colour_choice == 'blue':
                    colour = (255 - shade, 255 - shade, 255)
                elif colour_choice == 'green':
                    colour = (255 - shade, 255, 255 - shade)

                pygame.draw.rect(screen, colour, pygame.Rect(x * 100, y * 100, 100, 100))
                font = pygame.font.SysFont('Arial', 30)
                text = font.render(str(tile.value), True, (0, 0, 0))
                screen.blit(text, (x * 100 + 50 - text.get_width() / 2, y * 100 + 50 - text.get_height() / 2))

    def check_game_over(self) -> bool:
        """Return whether the game is over."""
        for x in range(board.width):
            for y in range(board.height):
                tile = board._get((x, y))
                if tile is None:
                    return False

                for direction in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                    next_pos = _move_position((x, y), direction)
                    if not board._is_valid(next_pos):
                        continue

                    next_tile = board._get(next_pos)
                    if next_tile is None or tile.value == next_tile.value:
                        return False
        return True

    def check_win(self) -> bool:
        for row in self.board:
            for tile in row:
                if tile is not None and tile.value == 2048:
                    return True
        return False


# UI components

def display_colour_choice(screen: pygame.Surface):
    font = pygame.font.SysFont('Arial', 30)

    colour_choice_1 = font.render("Press [B] for blue,", True, (255, 255, 255))
    screen.blit(colour_choice_1, (400 // 2 - colour_choice_1.get_width() // 2, 150 - colour_choice_1.get_height() / 2))

    colour_choice_2 = font.render("[R] for red,", True, (255, 255, 255))
    screen.blit(colour_choice_2, (400 // 2 - colour_choice_2.get_width() // 2, 200 - colour_choice_2.get_height() / 2))

    colour_choice_3 = font.render("and [G] for green", True, (255, 255, 255))
    screen.blit(colour_choice_3, (400 // 2 - colour_choice_3.get_width() // 2, 250 - colour_choice_3.get_height() / 2))

    pygame.display.flip()

def display_game_over(screen):
    font = pygame.font.SysFont('Arial', 50)
    text = font.render("Game Over", True, (0, 0, 0))
    screen.blit(text, (200 - text.get_width() / 2, 200 - text.get_height() / 2))
    pygame.display.flip()

def display_winning_message(screen):
    yellow_overlay = pygame.Surface((400, 400), pygame.SRCALPHA)
    yellow_overlay.fill((255, 255, 0, 150))
    screen.blit(yellow_overlay, (0, 0))

    font = pygame.font.SysFont('Arial', 60)
    win_text = font.render("YOU WIN!", True, (0, 0, 0))
    screen.blit(win_text, (400 // 2 - win_text.get_width() // 2, 100))  # Move "YOU WIN" text up

    font = pygame.font.SysFont('Arial', 30)
    continue_messages = ["Press [Q] to continue,", "[W] to restart", "[E] to exit"]
    y_offset = 200  # offset from top of screen
    for message in continue_messages:
        continue_text = font.render(message, True, (0, 0, 0))
        screen.blit(continue_text, (400 // 2 - continue_text.get_width() // 2, y_offset))
        y_offset += continue_text.get_height() + 10  # Add 10 pixels of spacing between lines

    pygame.display.flip()


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((400, 400))
    board = Board(4, 4)
    board.spawn()
    board.spawn()

    # Display the colour choice screen
    display_colour_choice(screen)

    # Wait for user input to choose colour
    colour_choice = None
    while colour_choice is None:
        event = pygame.event.wait()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_b:
                colour_choice = 'blue'
            elif event.key == pygame.K_r:
                colour_choice = 'red'
            elif event.key == pygame.K_g:
                colour_choice = 'green'

    running = True
    game_won = False
    user_continued = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    board.move((0, -1))
                elif event.key == pygame.K_DOWN:
                    board.move((0, 1))
                elif event.key == pygame.K_LEFT:
                    board.move((-1, 0))
                elif event.key == pygame.K_RIGHT:
                    board.move((1, 0))

        screen.fill((255, 255, 255))
        board.draw(screen, colour_choice)
        pygame.display.flip()

        # Check game status (win or lose) and display appropriate message
        if board.check_win() and not game_won and not user_continued:
            display_winning_message(screen)
            while True:
                event = pygame.event.wait()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_e:
                        running = False
                        break
                    elif event.key == pygame.K_q:
                        user_continued = True  # Used to make sure winning screen doesn't pop up again
                        break
                    elif event.key == pygame.K_w:
                        # Reset the board and redraw the screen
                        board = Board(4, 4)
                        board.spawn()
                        board.spawn()
                        screen.fill((255, 255, 255))
                        board.draw(screen, colour_choice)
                        pygame.display.flip()
                        break
                    else:
                        continue

        if board.check_game_over():
            print("Game over!")
            display_game_over(screen)
            pygame.time.delay(10000)
            running = False
