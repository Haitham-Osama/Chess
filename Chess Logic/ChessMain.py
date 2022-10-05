''' 
Main file,handling user input and displaying current GameState object.
'''

import pygame as p
import ChessEngine
import sys

p.init()

GAME_WIDTH = 1280
GAME_HEIGHT = 720
FPS = 30
DIMENSION = 8 # board
TILE_SIZE = 90
IMAGES={}
# BOARD_WIDTH = GAME_WIDTH//TILE_SIZE
# BOARD_HEIGHT = GAME_HEIGHT//TILE_SIZE

''' IMAGES '''
def load_images():  
    pieces =['wp','wR','wN','wK','wQ','wB','bp','bR','bN','bK','bQ','bB']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load('assets/game/'+piece+'.png'),(TILE_SIZE-20,TILE_SIZE-20))


''' MAIN '''
def game():
    WINDOW = p.display.set_mode((GAME_WIDTH,GAME_HEIGHT))
    clock = p.time.Clock()
    WINDOW.fill(p.Color('white'))
    gl = ChessEngine.GameLogic()
    validMoves = gl.getValidMoves()
    moveMade = False  # flag variable for when a move is made
    
    load_images()
    
    selected = ()
    playerClicks = [] # keep track of player clicks (two tuples)
    
    run = True
    while run:
        for event in p.event.get():
            
            if event.type == p.QUIT:
                run = False
                sys.exit()
            #Mouse Handling 
            elif event.type == p.MOUSEBUTTONDOWN and event.button == 1:    
                
                location = p.mouse.get_pos()
                if location[0] > 7*TILE_SIZE+GAME_WIDTH//4+45 or location[0] < 0*TILE_SIZE+GAME_WIDTH//4-45 :pass
                else:
                    row = location[1]//TILE_SIZE
                    col = (location[0]-(GAME_WIDTH//4-45))//TILE_SIZE
                    print(row,col)
                    if selected == (row,col):
                        selected = ()
                        playerClicks = []
                    else:
                        selected = (row,col)
                        playerClicks.append(selected)
                    if len(playerClicks) == 2:
                        sr,sc = playerClicks[0][0],playerClicks[0][1]
                        startPiece = gl.board[sr][sc]
                        move = ChessEngine.Move(playerClicks[0],playerClicks[1],gl.board)
                        print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gl.make_move(validMoves[i])
                                moveMade = True
                                selected = () #reset clicks
                                playerClicks = []
                        if not moveMade:playerClicks = [selected]
            # Key Handling
            elif event.type == p.KEYDOWN:
                if event.key == p.K_z: # undo when z is pressed
                    gl.undo_move()
                    moveMade = True
                    
        if moveMade:
            validMoves = gl.getValidMoves()
            moveMade = False
                
        drawGame(WINDOW,gl,validMoves,selected)
        clock.tick(FPS)
        p.display.flip()

''' GRAPHICS FUNCTIONS'''
def drawGame(screen,gs,validMoves,selected):
    drawBoard(screen) # draw squares on screen
    highlight(screen,gs,validMoves,selected)
    drawPieces(screen,gs.board)
    

def drawBoard(screen):
    colors = [p.Color('white'),p.Color('gray')]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c)%2)]
            p.draw.rect(screen,color,p.Rect(c*TILE_SIZE+GAME_WIDTH//4-45,r*TILE_SIZE,TILE_SIZE,TILE_SIZE))
            
def drawPieces(screen,board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != '--':
                screen.blit(IMAGES[piece],p.Rect(c*TILE_SIZE+GAME_WIDTH//4-37,r*TILE_SIZE+10,TILE_SIZE,TILE_SIZE))
            
def highlight(screen,gs,validMoves,selected):
    if selected != ():
        r,c = selected[0],selected[1]
        # c*TILE_SIZE +(GAME_WIDTH//4-45) = location[0]-(GAME_WIDTH//4-45)
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'): # selected is a piece that can be moved
            # highlight selected square
            highlight_rect = p.Surface((TILE_SIZE,TILE_SIZE))
            highlight_rect.set_alpha(150)
            highlight_rect.fill(p.Color('blue'))
            screen.blit(highlight_rect,(c*TILE_SIZE +(GAME_WIDTH//4-45),r*TILE_SIZE))
            # highlight moves
            highlight_rect.fill(p.Color('azure3'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(highlight_rect,(move.endCol*TILE_SIZE+(GAME_WIDTH//4-45),move.endRow*TILE_SIZE))
            

if __name__ == '__main__':game()