
# Copyright (c) 2026 Mohamed-Amine Ben Njima
# Licensed under the MIT License.
# See LICENSE for details.

from pathlib import Path
import pygame as pg
import engine

WIDTH = HEIGHT = 512
PANEL_WIDTH = 100
DIMENSION = 8
CELL_SIZE = WIDTH/DIMENSION
MAX_FPS = 15
IMAGES = {}
FLIP_BOARD = False

def loadImages():
    for x in Path("images").iterdir():
        image = pg.image.load(x).convert_alpha()
        image = pg.transform.smoothscale(image, (CELL_SIZE, CELL_SIZE))
        IMAGES[x.name.removesuffix(".png")] = image

def main():
    global FLIP_BOARD
    pg.init()

    screen = pg.display.set_mode((WIDTH + PANEL_WIDTH*2, HEIGHT))
    font = pg.font.SysFont(None, 28)
    clock = pg.time.Clock()
    screen.fill(pg.Color("white"))

    gs = engine.GameState()
    loadImages()

    pg.display.set_caption("Python Chess")
    pg.display.set_icon(IMAGES['wK'])

    running = True
    Promotionfrozen = False

    buttons = {}

    sqSelected = ()
    playerClicks = []

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1 and buttons['N'].collidepoint(event.pos) and Promotionfrozen:
                    gs.finishMoveAfterPromotion(playerClicks, 'N')
                    Promotionfrozen = False
                    sqSelected = ()
                    playerClicks.clear()
                if event.button == 1 and buttons['Q'].collidepoint(event.pos) and Promotionfrozen:
                    gs.finishMoveAfterPromotion(playerClicks, 'Q')
                    Promotionfrozen = False
                    sqSelected = ()
                    playerClicks.clear()
                if event.button == 1 and buttons['R'].collidepoint(event.pos) and Promotionfrozen:
                    gs.finishMoveAfterPromotion(playerClicks, 'R')
                    Promotionfrozen = False
                    sqSelected = ()
                    playerClicks.clear()
                if event.button == 1 and buttons['B'].collidepoint(event.pos) and Promotionfrozen:
                    gs.finishMoveAfterPromotion(playerClicks, 'B')
                    Promotionfrozen = False
                    sqSelected = ()
                    playerClicks.clear()

                if event.button == 1 and buttons['flip'].collidepoint(event.pos):
                    FLIP_BOARD = not FLIP_BOARD
                
                if gs.concluded == True or Promotionfrozen == True:
                    continue

                if event.button == 1 and buttons['undo'].collidepoint(event.pos):
                    gs.undoMove()
                    sqSelected = ()
                    playerClicks.clear()
                
                location = pg.mouse.get_pos()
                col = int(location[0]//CELL_SIZE)
                row = int("76543210"[int(location[1]//CELL_SIZE)])
                if col < 0 or col > 7 or row < 0 or row > 7:
                    continue
                if FLIP_BOARD:
                    row = int("76543210"[row]) if gs.turn == 'b' else row
                    col = int("76543210"[col]) if gs.turn == 'b' else col

                if sqSelected == (col, row):
                    sqSelected = ()
                    playerClicks.clear()
                else:
                    if len(playerClicks) < 1:
                        if gs.board[col][row].id == "--":
                            continue

                        if gs.board[col][row].side != gs.turn:
                            continue

                    if gs.board[col][row].side == gs.turn:
                        sqSelected = (col, row)
                        playerClicks = [sqSelected]
                        continue

                    sqSelected = (col, row)
                    playerClicks.append(sqSelected)

                if len(playerClicks) == 2:
                    move = gs.executeMove(playerClicks)

                    if len(move) > 0:
                        Promotionfrozen = True
                        continue
                    
                    sqSelected = ()
                    playerClicks.clear()

        drawGameState(screen, gs, sqSelected)
        buttons = renderSideMenus(screen, font, gs, Promotionfrozen)
        clock.tick(MAX_FPS)
        pg.display.flip()

def renderSideMenus(screen, font, gs:engine.GameState, Promotionfrozen:bool):
    pg.draw.rect(screen, pg.Color(60, 60, 60), pg.Rect(WIDTH, 0, PANEL_WIDTH, HEIGHT))
    pg.draw.line(screen, (120, 120, 120), (WIDTH+2, 0), (WIDTH+2, HEIGHT), 5)

    pg.draw.rect(screen, pg.Color(60, 60, 60), pg.Rect(WIDTH+PANEL_WIDTH, 0, PANEL_WIDTH, HEIGHT))
    pg.draw.line(screen, (120, 120, 120), (WIDTH+2, HEIGHT-70), (WIDTH+PANEL_WIDTH*2, HEIGHT-70), 5)
    pg.draw.line(screen, (120, 120, 120), (WIDTH+PANEL_WIDTH, 0), (WIDTH+PANEL_WIDTH, HEIGHT-70), 5)

    y = 10
    for annotation in reversed(gs.moveLog):
        text = font.render(annotation, True, (220, 220, 220))
        text_rect = text.get_rect()

        text_rect.centerx = WIDTH+PANEL_WIDTH//2
        text_rect.y = y

        if gs.moveLog.index(annotation) > len(gs.moveLog)-15:
            screen.blit(text, text_rect)
            y += 30
        else:
            continue

    undo_button_rect = pg.Rect(WIDTH+PANEL_WIDTH+6, 5, PANEL_WIDTH-8, 55)
    flip_button_rect = pg.Rect(WIDTH+8, 450, PANEL_WIDTH*2-10, 55)

    knight_button = pg.Rect(WIDTH+PANEL_WIDTH+6, 75, PANEL_WIDTH-8, 85)
    bishop_button = pg.Rect(WIDTH+PANEL_WIDTH+6, 165, PANEL_WIDTH-8, 85)
    rook_button = pg.Rect(WIDTH+PANEL_WIDTH+6, 255, PANEL_WIDTH-8, 85)
    queen_button = pg.Rect(WIDTH+PANEL_WIDTH+6, 345, PANEL_WIDTH-8, 85)

    button_text = font.render("Undo", True, (220, 220, 220))
    button_text_rect = button_text.get_rect(center=undo_button_rect.center)

    flip_button_text = font.render("Flip board: " + str(FLIP_BOARD), True, (220, 220, 220))
    flip_button_text_rect = button_text.get_rect(center=flip_button_rect.center)
    flip_button_text_rect.centerx = WIDTH+PANEL_WIDTH//2

    Nimage = pg.image.load(Path("images/"+gs.turn+"N.png")).convert_alpha()
    Nimage = pg.transform.smoothscale(Nimage, (80, 80))
    N_rect = Nimage.get_rect(center=knight_button.center)
    Bimage = pg.image.load(Path("images/"+gs.turn+"B.png")).convert_alpha()
    Bimage = pg.transform.smoothscale(Bimage, (80, 80))
    B_rect = Bimage.get_rect(center=bishop_button.center)
    Rimage = pg.image.load(Path("images/"+gs.turn+"R.png")).convert_alpha()
    Rimage = pg.transform.smoothscale(Rimage, (80, 80))
    R_rect = Rimage.get_rect(center=rook_button.center)
    Qimage = pg.image.load(Path("images/"+gs.turn+"Q.png")).convert_alpha()
    Qimage = pg.transform.smoothscale(Qimage, (80, 80))
    Q_rect = Qimage.get_rect(center=queen_button.center)

    pg.draw.rect(screen, (80, 80, 80), undo_button_rect, border_radius=8)
    pg.draw.rect(screen, (140, 140, 140), undo_button_rect, 2, border_radius=8)
    pg.draw.rect(screen, (80, 80, 80), flip_button_rect, border_radius=8)
    pg.draw.rect(screen, (140, 140, 140), flip_button_rect, 2, border_radius=8)
    screen.blit(flip_button_text, flip_button_text_rect)
    screen.blit(button_text, button_text_rect)

    if Promotionfrozen:
        pg.draw.rect(screen, (80, 80, 80), knight_button, border_radius=8)
        pg.draw.rect(screen, (140, 140, 140), knight_button, 2, border_radius=8)
        pg.draw.rect(screen, (80, 80, 80), bishop_button, border_radius=8)
        pg.draw.rect(screen, (140, 140, 140), bishop_button, 2, border_radius=8)
        pg.draw.rect(screen, (80, 80, 80), rook_button, border_radius=8)
        pg.draw.rect(screen, (140, 140, 140), rook_button, 2, border_radius=8)
        pg.draw.rect(screen, (80, 80, 80), queen_button, border_radius=8)
        pg.draw.rect(screen, (140, 140, 140), queen_button, 2, border_radius=8)

        screen.blit(Nimage, N_rect)
        screen.blit(Bimage, B_rect)
        screen.blit(Rimage, R_rect)
        screen.blit(Qimage, Q_rect)

    return {
        'undo': undo_button_rect,
        'N': knight_button,
        'B': bishop_button,
        'R': rook_button,
        'Q': queen_button,
        'flip': flip_button_rect
    }

def drawGameState(screen, gs:engine.GameState, sqSelected):
    renderBoard(screen, gs.board, gs.winner, sqSelected, gs.turn)

def renderBoard(screen, board:list[list[engine.Square]], winner:str, sqSelected, turn:str):
    colors = [pg.Color((237, 236, 215)), pg.Color((77, 109, 147))]
    slColor = pg.Color(255, 245, 0, 50)
    slLM = []
    if sqSelected:
        slLM = board[sqSelected[0]][sqSelected[1]].legalMoves
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            correctedRow = int("76543210"[row])
            correctedCol = col
            if FLIP_BOARD:
                correctedRow = int("76543210"[row]) if turn == 'w' else row
                correctedCol = col if turn == 'w' else int("76543210"[col])
            else:
                correctedRow = int("76543210"[row])
                correctedCol = col
            color = colors[((col+row)%2)]
            piece = board[col][row]
            pg.draw.rect(screen, color, pg.Rect(correctedCol*CELL_SIZE, correctedRow*CELL_SIZE, CELL_SIZE, CELL_SIZE))

            if list(sqSelected) == [col, row]:
                pg.draw.rect(screen, slColor, pg.Rect(correctedCol*CELL_SIZE, correctedRow*CELL_SIZE, CELL_SIZE, CELL_SIZE))
            
            if piece.id != "--":
                if piece.underAttack == True and piece.type == 'K':
                    screen.blit(IMAGES["check"], pg.Rect(correctedCol*CELL_SIZE, correctedRow*CELL_SIZE, CELL_SIZE, CELL_SIZE))

                screen.blit(IMAGES[piece.id], pg.Rect(correctedCol*CELL_SIZE, correctedRow*CELL_SIZE, CELL_SIZE, CELL_SIZE))

                if piece.type == 'K' and winner != piece.side and winner != "-" and piece.underAttack:
                    screen.blit(IMAGES["checkmate"], pg.Rect(correctedCol*CELL_SIZE, correctedRow*CELL_SIZE, CELL_SIZE, CELL_SIZE))
                    continue
                if piece.type == 'K' and winner == "1/2" and not piece.underAttack:
                    screen.blit(IMAGES["stalemate"], pg.Rect(correctedCol*CELL_SIZE, correctedRow*CELL_SIZE, CELL_SIZE, CELL_SIZE))
                    continue
                if piece.type != 'K' and (col, row) in slLM:
                    screen.blit(IMAGES["lc"], pg.Rect(correctedCol*CELL_SIZE, correctedRow*CELL_SIZE, CELL_SIZE, CELL_SIZE))
            else:
                if (col, row) in slLM:
                    screen.blit(IMAGES["lm"], pg.Rect(correctedCol*CELL_SIZE, correctedRow*CELL_SIZE, CELL_SIZE, CELL_SIZE))

if __name__ == "__main__":
    main()