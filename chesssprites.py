"""This file is responsible for handling pygame's sprites and giving each sprite the correct attributes."""

import pygame as pyg


class InvalidPieceException(Exception):
    """Raised when a piece passed to 'Piece' is not recognized."""

    def __init__(self, piece: str):
        message: str = f"Piece entered must be one of ['p', 'R', 'N', 'B', 'Q', 'K']. You entered {piece}."
        super().__init__(message)


class Tile(pyg.sprite.Sprite):
    def __init__(self, size: int, pos: tuple[int, int], colour: tuple[int, int, int], tile_id: str, show_id: bool):
        """Creates a square with the desired properties."""
        super().__init__()

        self.ID: str = tile_id  # Holds a value such as 'A1' or 'G6'.

        # Creates a square.
        self.image: pyg.Surface = pyg.Surface((size, size))
        pyg.draw.rect(self.image, colour, [0, 0, size, size])

        # Puts the tile in the correct position.
        self.rect: pyg.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]

        if show_id:
            # Adds the tile ID to the tile.
            font: pyg.font.SysFont = pyg.font.SysFont('Arial', 20)
            text_surf: pyg.image = font.render(self.ID, True, (0, 0, 0))
            text_rect: pyg.rect = text_surf.get_rect(center=(10, size - 10))
            self.image.blit(text_surf, text_rect)


class Piece(pyg.sprite.Sprite):
    def __init__(self, piece: str, tile: str, pos: tuple, size: int):
        """Creates a piece with the desired properties."""
        super().__init__()

        if piece.lower() not in "prnbqk":
            raise InvalidPieceException(piece)

        self.piece = piece

        if piece.isupper():
            self.team = "w"
        else:
            self.team = "b"

        # Sets up the sprite.
        self.image: pyg.image = pyg.image.load(f"sprites/{self.team}{self.piece}.png").convert_alpha()
        self.image = pyg.transform.scale(self.image, (size, size))

        self.rect: pyg.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]

        self.tile: str = tile
        self.clicked: bool = False


class PlayerInfo(pyg.sprite.Sprite):
    def __init__(self, dimensions, center, info):
        super().__init__()
        self.image = pyg.Surface(dimensions)
        self.image.fill((0, 0, 0))

        # To add text.
        pyg.font.init()
        font = pyg.font.SysFont('Monospace', 40)
        text_surface = font.render(info, True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.center = (dimensions[0] / 2, dimensions[1] / 2)
        self.image.blit(text_surface, text_rect)

        self.rect = self.image.get_rect()
        self.rect.center = center


class EndScreen(pyg.sprite.Sprite):
    def __init__(self, dimensions: tuple[int, int], center: tuple[int, int], board):
        super().__init__()
        self.image = pyg.Surface(dimensions)
        self.image.fill((0, 0, 0))

        if board.is_checkmate():
            title = "Checkmate"
            if board.outcome().winner:
                desc = "White wins via checkmate."
            else:
                desc = "Black wins via checkmate."

        else:
            title = "Stalemate"
            if board.is_stalemate():
                if board.turn:
                    desc = "White is out of playable moves."
                else:
                    desc = "Black is out of playable moves."
            elif board.can_claim_threefold_repetition():
                desc = "The position has been repeated 3 times."
            elif board.can_claim_fifty_moves():
                desc = "50 non-pawn moves have been made without a piece being captured."

        # To add text.
        pyg.font.init()
        font = pyg.font.SysFont('CAD:', 100)
        title_text_surface = font.render(title, True, (255, 255, 255))
        title_text_rect = title_text_surface.get_rect()
        title_text_rect.center = (dimensions[0] / 2, dimensions[1] / 4)
        self.image.blit(title_text_surface, title_text_rect)

        font = pyg.font.SysFont('CAD:', 40)
        desc_text_surface = font.render(desc, True, (255, 255, 255))
        desc_text_rect = desc_text_surface.get_rect()
        desc_text_rect.center = (dimensions[0] / 2, dimensions[1] - (dimensions[1] / 3))
        self.image.blit(desc_text_surface, desc_text_rect)

        self.rect = self.image.get_rect()
        self.rect.center = center

