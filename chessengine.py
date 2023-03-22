"""This file is responsible for handling pygame and displaying the board to the user."""

import pygame as pyg
import chesssprites as spr
import chess
from dbmanager import ChessDatabase

a_to_h: list[str] = list("abcdefgh")
eight_to_one: list[str] = list("87654321")


class Chess:
    def __init__(self):
        """Creates the necessary variables to run the game."""

        # Initialising pygame variables.
        pyg.init()
        #self.SCREEN_RESOLUTION: tuple[int, int] = (800, 950)
        self.SCREEN_RESOLUTION: tuple[int, int] = (600, 713)
        self.screen: pyg.display = pyg.display.set_mode(self.SCREEN_RESOLUTION)  # Sets the resolution of the window.

        # Initialising variables for the game.
        self.board = chess.Board()

        self.tile_group: pyg.sprite.Group = pyg.sprite.Group()
        self.piece_group: pyg.sprite.Group = pyg.sprite.Group()
        self.other_sprites_group: pyg.sprite.Group = pyg.sprite.Group()

        self.sprite_groups: list[pyg.sprite.Group] = [self.tile_group, self. piece_group, self.other_sprites_group]

        # Dictionary that holds the tile ID as the key and the tile sprite object as the value.
        self.tile_dictionary: dict[str, spr.Tile] = {}
        self.piece_dictionary: dict[str, spr.Piece] = {}

        self.is_running: bool = False
        self.is_playing: bool = False

        self.w_name = "White"
        self.w_elo = "900"
        self.b_name = "Black"
        self.b_elo = "900"

        self.create_board()

    def create_board(self) -> None:
        """Responsible for creating tiles on the screen in the correct position and builds the tile dictionary."""

        # (255, 192, 203) (118, 150, 86)
        tile_colours: list[tuple] = [(118, 150, 86), (238, 238, 210)]
        tile_size: int = round(self.SCREEN_RESOLUTION[0] / 8)  # Calculates the size the tiles must be.

        # Calculates how far from the top of the screen it must start creating the tiles for it to be centered.
        y_offset: int = round((self.SCREEN_RESOLUTION[1] - self.SCREEN_RESOLUTION[0]) / 2)

        # Holds the variables that decide where the tiles get drawn.
        x_pos: int
        y_pos: int = y_offset - tile_size

        for y_row in range(8):
            x_pos = 0 - tile_size  # Resets the x position, so that it creates the sprites from the left.
            y_pos += tile_size  # Increments the y position down by 1 every time the x row has been completed.
            for x_row in range(8):
                x_pos += tile_size  # Increments the x position to the right by 1.

                # Determines if the tile will show its ID or not.
                show_id: bool = False
                if y_row == 7 or x_row == 0:
                    show_id = True

                tile_id: str = str(a_to_h[x_row] + eight_to_one[y_row])

                # Adds the sprite to it's group with its proper colour and ID.
                if ((x_row % 2) + (y_row % 2)) % 2 == 0:
                    tile = spr.Tile(tile_size, (x_pos, y_pos), tile_colours[1], tile_id, show_id)
                else:
                    tile = spr.Tile(tile_size, (x_pos, y_pos), tile_colours[0], tile_id, show_id)

                self.add_sprite(tile)
                self.tile_dictionary[tile_id] = tile

    def update_pieces(self) -> None:
        """Responsible for creating pieces on the screen in the correct position and builds the piece dictionary."""

        piece_size: int = round(self.SCREEN_RESOLUTION[0] / 8)  # The same calculation used to find the tile size.

        # Empties the piece sprite group.
        for sprite in self.piece_group:
            sprite.kill()

        # Empties the piece dictionary.
        self.piece_dictionary = {tile: None for tile in self.piece_dictionary}

        # 'tile' always refers to a tile in the format "A1" or "F6" etc. All dictionaries are made like this, so
        # calling the correct value from each dictionary for the correct tile is easy.
        pos = [0, 0]
        for piece in self.board.fen().split()[0]:
            if piece.isnumeric():
                pos[0] += int(piece)
            elif piece.isalpha():
                tile: str = a_to_h[pos[0]] + eight_to_one[pos[1]]
                tile_pos: tuple = (self.tile_dictionary[tile].rect.x, self.tile_dictionary[tile].rect.y)

                spr_piece: spr.Piece = spr.Piece(piece, tile, tile_pos, piece_size)

                self.add_sprite(spr_piece)
                self.piece_dictionary[tile] = spr_piece

                pos[0] += 1

            else:
                pos[0] = 0
                pos[1] += 1

            if pos[0] >= 8:
                pos[0] = 0

    def add_sprite(self, *sprites: any) -> None:
        """Responsible for adding sprites into their designated groups."""

        [self.tile_group.add(sprite) for sprite in sprites
         if type(sprite) == spr.Tile]

        [self.piece_group.add(sprite) for sprite in sprites
         if type(sprite) == spr.Piece]

        [self.other_sprites_group.add(sprite) for sprite in sprites
         if type(sprite) != spr.Piece and type(sprite) != spr.Tile]

    def update_screen(self, bg_colour: tuple, *sprite_groups: pyg.sprite.Group) -> None:
        """Responsible for updating the screen."""

        self.screen.fill(bg_colour)  # Fills the background.

        # Updates the sprite groups and draws them on the screen.
        [sprite_group.update() for sprite_group in sprite_groups]
        [sprite_group.draw(self.screen) for sprite_group in sprite_groups]
        
        pyg.display.flip()  # Refreshes the display.

    def event_handler(self, event) -> None:
        """Responsible for handling all events during runtime."""

        # When the window is closed.
        if event.type == pyg.QUIT:
            self.is_running = False  # Ends the mainloop.

        # If the game has not ended.
        elif self.is_playing:
            # When LMB is clicked.
            if event.type == pyg.MOUSEBUTTONDOWN and event.button == 1:
                self.lmb_down_event()

            # When LMB is released.
            elif event.type == pyg.MOUSEBUTTONUP and event.button == 1:
                self.lmb_up_event()

    def lmb_down_event(self) -> None:
        """Responsible for handling the 'left mouse button down' event."""
        mouse_pos: tuple = pyg.mouse.get_pos()
        for tile in self.piece_dictionary:
            if self.piece_dictionary[tile] is not None:
                # Only allows a piece to move if it is that team's turn.
                if self.piece_dictionary[tile].piece.isupper() and self.board.turn or \
                   self.piece_dictionary[tile].piece.islower() and not self.board.turn:
                    # If any piece in the dict is colliding with the mouse pos.
                    if self.piece_dictionary[tile].rect.collidepoint(mouse_pos):
                        self.piece_dictionary[tile].clicked = True

    def lmb_up_event(self) -> None:
        """Responsible for handling the 'left mouse button up' event."""

        for piece_tile in self.piece_dictionary:
            # If the tile is not empty.
            if self.piece_dictionary[piece_tile] is not None:
                if self.piece_dictionary[piece_tile].clicked:
                    self.piece_dictionary[piece_tile].clicked = False  # Unbinds the piece from the mouse.
                    mouse_pos: tuple = pyg.mouse.get_pos()
                    for tiledict_tile in self.tile_dictionary:
                        if self.tile_dictionary[tiledict_tile].rect.collidepoint(mouse_pos):
                            # Moves the pieces. If an illegal move is made, the exception will be handled.
                            try:
                                move = chess.Move.from_uci(self.piece_dictionary[piece_tile].tile +
                                                           tiledict_tile)

                                if self.piece_dictionary[piece_tile].piece == 'P' and \
                                     piece_tile[1] == "7" or \
                                     self.piece_dictionary[piece_tile].piece == 'p' and \
                                     piece_tile[1] == "2":
                                    move = chess.Move.from_uci(self.piece_dictionary[piece_tile].tile +
                                                               tiledict_tile + "q")

                                if move in self.board.legal_moves:
                                    self.board.push(move)

                            except ValueError:
                                pass

                            break  # Exits the inner loop.

                    self.update_pieces()  # Updates the piece sprites.
                    break  # Exits the outer loop.

    def end_game(self) -> None:
        """Ends the game once checkmate or stalemate is reached."""
        self.is_playing = False
        endscreen_dimentions = (self.SCREEN_RESOLUTION[0], self.SCREEN_RESOLUTION[1] / 4)
        endscreen_center = (self.SCREEN_RESOLUTION[0] / 2, self.SCREEN_RESOLUTION[1] / 2)

        self.add_sprite(spr.EndScreen(endscreen_dimentions, endscreen_center, self.board))

        self.add_game_to_database()

    def add_game_to_database(self):
        """Called once the game has ended."""

        all_moves = ""
        count = 0.5
        for move in self.board.move_stack:
            count += 0.5
            move = str(move)
            if count.is_integer():
                move = str(int(count)) + ". " + move[:2:] + " to " + move[2::]
            else:
                move = ", " + move[:2:] + " to " + move[2::] + ".\n"

            all_moves += move

        if self.board.is_stalemate() or self.board.can_claim_threefold_repetition() or \
           self.board.can_claim_fifty_moves() or self.board.can_claim_fifty_moves():
            winner = "Stalemate"
        else:
            if self.board.outcome().winner:
                winner = "White"
            else:
                winner = "Black"

        db = ChessDatabase()
        db.add_entry(self.w_name, self.w_elo, self.b_name, self.b_elo, winner, all_moves)
        db.save()
        db.close()

    def display_users(self, w_name, w_elo, b_name, b_elo):
        """Displays the users at the top and bottom of the screen."""

        self.w_name = w_name
        self.w_elo = w_elo
        self.b_name = b_name
        self.b_elo = b_elo

        w_info = w_name + "(" + w_elo + ")"
        b_info = b_name + "(" + b_elo + ")"

        top_tile_pos = self.tile_dictionary["d8"].rect.topright
        bottom_tile_pos = self.tile_dictionary["d1"].rect.bottomright

        b_info_location = (top_tile_pos[0], top_tile_pos[1] / 2)
        w_info_location = (bottom_tile_pos[0], self.SCREEN_RESOLUTION[1] - (top_tile_pos[1] / 2))

        info_dimentions = (self.SCREEN_RESOLUTION[0], top_tile_pos[1])

        w_info_sprite = spr.PlayerInfo(info_dimentions, w_info_location, w_info)
        b_info_sprite = spr.PlayerInfo(info_dimentions, b_info_location, b_info)

        self.add_sprite(w_info_sprite, b_info_sprite)

    def start_game(self) -> None:
        """Creates the sprites and starts the mainloop of the game."""

        self.update_pieces()

        self.is_running = True
        self.is_playing = True
        while self.is_running:
            # Checks for events.
            for event in pyg.event.get():
                # Passes the event to the event handler.
                self.event_handler(event)

            if self.is_playing:
                if self.board.is_checkmate():
                    self.end_game()

                elif self.board.is_stalemate() or self.board.can_claim_threefold_repetition() or \
                     self.board.can_claim_fifty_moves() or self.board.can_claim_fifty_moves():
                    self.end_game()

                # Updates the position of clicked pieces.
                for tile in self.piece_dictionary:
                    if self.piece_dictionary[tile] is not None:
                        if self.piece_dictionary[tile].clicked:
                            mouse_pos: tuple = pyg.mouse.get_pos()
                            self.piece_dictionary[tile].rect.centerx = mouse_pos[0]
                            self.piece_dictionary[tile].rect.centery = mouse_pos[1]

            self.update_screen((0, 0, 0), *self.sprite_groups)

        pyg.quit()
