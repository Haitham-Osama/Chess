'''
initializing Pygame window, loading images, drawing the screen, Handling User events, drawing board and pieces and handling results, Window loop 
'''
import pygame as p
import ChessEngine
import sys
import os

''' Initilaize pygame font & sound library'''
p.init()
p.font.init() 
p.mixer.init()

''' CONSTANTS '''
GAME_WIDTH = 1280
GAME_HEIGHT = 720
FPS = 30
DIMENSION = 8 # board
TILE_SIZE = 90 # tile
IMAGES={}
# BOARD_WIDTH = GAME_WIDTH//TILE_SIZE
# BOARD_HEIGHT = GAME_HEIGHT//TILE_SIZE
BACKGROUND_COLOR = (20,20,20)
WHITE = (255,255,255)
BLACK = (0,0,0)
OBJECTS = []
BUTTON_WIDTH = 327
BUTTON_HEIGHT = 99
COLOR_INACTIVE = p.Color('gray')
COLOR_ACTIVE = ((40,40,40))
INPUT = {'white':'Guest','black':'Guest','time':''}
undo_width = BUTTON_WIDTH - 60
undo_height = BUTTON_HEIGHT - 50

''' IMAGES '''
def load_images():  #* pieces Images
    pieces =['wp','wR','wN','wK','wQ','wB','bp','bR','bN','bK','bQ','bB']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load('assets/game/'+piece+'.png'),(TILE_SIZE-20,TILE_SIZE-20))    
        
ICON = (p.image.load('assets/icon.png'))
BACKGROUND_IMAGE = p.transform.scale(p.image.load(os.path.join('assets','main menu','background.png')),(GAME_WIDTH,GAME_HEIGHT))
MAIN_MENU_LOGO = p.transform.scale(p.image.load('assets/main menu/logo.png'),(376,397))
PLAY_BUTTON_IMAGE = p.image.load('assets/main menu/play_button.png')
QUIT_BUTTON_IMAGE = p.image.load('assets/main menu/quit_button.png')
START_BUTTON_IMAGE = p.image.load('assets/game setup/start_button.png')
BACK_BUTTON_IMAGE = p.image.load('assets/game setup/back_button.png')
UNDO_BUTTON_IMAGE = p.image.load('assets/game/undo_button.png')
WHITE_QUEEN_IMAGE_SETUP = p.transform.scale(p.image.load('assets/game setup/white_queen.png'),(87,63))
BLACK_QUEEN_IMAGE_SETUP = p.transform.scale(p.image.load('assets/game setup/black_queen.png'),(87,63))

''' FONTS '''
FONT = p.font.Font('assets/fonts/Minecraft.ttf',50)
BIG_FONT = p.font.Font('assets/fonts/Minecraft.ttf',110)
USER_FONT = p.font.Font('assets/fonts/Minecraft.ttf',35)
NAME_FONT = p.font.Font('assets/fonts/Minecraft.ttf',30)
RESULT_FONT = p.font.Font('assets/fonts/Minecraft.ttf',75)
UNDO_RESET_FONT = p.font.Font('assets/fonts/Minecraft.ttf',30)

''' AUDIO'''
BUTTON_CLICK = p.mixer.Sound(os.path.join('assets','audio','button_click.wav'))
PIECE_MOVE = p.mixer.Sound('assets/audio/move_piece.wav')

''' CREATE WINDOW '''
WINDOW = p.display.set_mode((GAME_WIDTH,GAME_HEIGHT))
p.display.set_caption("Chess")
p.display.set_icon(ICON)


''' GUI CLASSES '''
class Button(): # https://www.thepythoncode.com/article/make-a-button-using-pygame-in-python
    def __init__(self, x, y, width, height,button_img, buttonText='Button', onclickFunction=None, onePress=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.button_img = button_img
        self.onclickFunction = onclickFunction
        self.onePress = onePress
        self.alreadyPressed = False

        self.fillColors = {
                            'normal': '#ffffff',
                            'hover': '#666666',
                            'pressed': '#333333',
                          }
        
        self.buttonSurface = p.Surface((self.width, self.height))
        self.buttonRect = p.Rect(self.x, self.y, self.width, self.height)
        self.buttonSurf = FONT.render(buttonText, True, (20, 20, 20))
        
        
        OBJECTS.append(self)
    
    def process(self):
        mousePos = p.mouse.get_pos()
        self.buttonSurface.fill(self.fillColors['normal'])
        if self.buttonRect.collidepoint(mousePos):
            self.buttonSurface.fill(self.fillColors['hover'])
            if p.mouse.get_pressed(num_buttons=3)[0]:
                BUTTON_CLICK.play()
                p.time.delay(10)
                self.buttonSurface.fill(self.fillColors['pressed'])
                if self.onePress:
                    self.onclickFunction()
                elif not self.alreadyPressed:
                    self.onclickFunction()
                    self.alreadyPressed = True
            else:
                self.alreadyPressed = False
                
        self.buttonSurface.blit(self.buttonSurf, [
                                self.buttonRect.width/2 - self.buttonSurf.get_rect().width/2,
                                self.buttonRect.height/2 - self.buttonSurf.get_rect().height/2
                                                 ])
        
    def draw(self):
        if self.button_img != None:
            self.button_img = p.transform.scale(self.button_img,(self.width,self.height))
            WINDOW.blit(self.button_img, (self.x, self.y))
        else:
            WINDOW.blit(self.buttonSurface, self.buttonRect)
    
    def get_width(self):
        return self.ship_img.get_width()
    
    def get_height(self):
        return self.ship_img.get_height()
        
class InputBox:

    def __init__(self, x, y, w, h, text='',tag=''):
        self.rect = p.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False
        self.tag = tag
        

    def handle_event(self, event):
        if event.type == p.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        if event.type == p.KEYDOWN:
            if self.active:
                if event.key == p.K_RETURN:
                    INPUT[self.tag]=self.text
                    print(INPUT)
                elif event.key == p.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = USER_FONT.render(self.text, True, self.color)

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the text.
        WINDOW.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect.
        p.draw.rect(WINDOW, self.color, self.rect, 2)
       
    
''' FUNCTIONS '''
def quit_function():
    p.quit()
    sys.exit()

def undo_function():
    pass

''' BOARD GRAPHICS FUNCTIONS'''
def drawChess(screen,gl,validMoves,selected):
    drawBoard(screen) # draw squares on screen
    highlight(screen,gl,validMoves,selected)
    drawPieces(screen,gl.board)
    
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

def drawResult(text):
    
    
    result_text = RESULT_FONT.render(text,1,(100,100,100))
    result_text_shadow = RESULT_FONT.render(text,1,(0,0,0))

    WINDOW.blit(result_text_shadow,((GAME_WIDTH-result_text.get_width())//2+4,(GAME_HEIGHT-result_text_shadow.get_height())//2+4))
    WINDOW.blit(result_text,((GAME_WIDTH-result_text.get_width())//2,(GAME_HEIGHT-result_text_shadow.get_height())//2))
    
    undo_resest_text = UNDO_RESET_FONT.render('Press Z/R to Undo/Restart',1,(100,100,100))
    undo_resest_text_shadow = UNDO_RESET_FONT.render('Press Z/R to Undo/Restart',1,(0,0,0))
    WINDOW.blit(undo_resest_text_shadow,((GAME_WIDTH-undo_resest_text_shadow.get_width())//2+2,(GAME_HEIGHT-undo_resest_text_shadow.get_height())//2+2+50))
    WINDOW.blit(undo_resest_text,((GAME_WIDTH-undo_resest_text.get_width())//2,(GAME_HEIGHT-undo_resest_text.get_height())//2+50))
        
def highlight(screen,gl,validMoves,selected):
    if selected != ():
        r,c = selected[0],selected[1]
        # c*TILE_SIZE +(GAME_WIDTH//4-45) = location[0]-(GAME_WIDTH//4-45)
        if gl.board[r][c][0] == ('w' if gl.whiteToMove else 'b'): # selected is a piece that can be moved
            # highlight selected square
            highlight_rect = p.Surface((TILE_SIZE,TILE_SIZE))
            highlight_rect.set_alpha(150)
            highlight_rect.fill(p.Color('blue'))
            screen.blit(highlight_rect,(c*TILE_SIZE +(GAME_WIDTH//4-45),r*TILE_SIZE))
            # highlight moves
            highlight_rect.fill(p.Color('cadetblue2'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(highlight_rect,(move.endCol*TILE_SIZE+(GAME_WIDTH//4-45),move.endRow*TILE_SIZE))     


    
''' MAIN '''
def drawMainmenu():

    WINDOW.fill((WHITE))
    WINDOW.blit(BACKGROUND_IMAGE,(0,0))
    WINDOW.blit(MAIN_MENU_LOGO,((GAME_WIDTH-MAIN_MENU_LOGO.get_width())//2,(GAME_HEIGHT-MAIN_MENU_LOGO.get_height())//2-150))
    
    PLAY_BUTTON.draw()
    QUIT_BUTTON.draw()
    # text = FONT.render('Text',1,WHITE)
    # WINDOW.blit(text,(45,20))
    p.display.update()

def MainMenu():
    clock = p.time.Clock()
    run = True

    while run:
        clock.tick(FPS)
        drawMainmenu()
        
        ''' Events '''
        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
                sys.exit()
                
        ''' KEYBOARD '''  
        # keys_pressed = pygame.key.get_pressed()
        
        ''' CALLING FUNCTIONS '''
        for object in OBJECTS[:2]:
            object.process()
  
  
def drawGameSetup():
    WINDOW.fill(WHITE)
    WINDOW.blit(BACKGROUND_IMAGE,(0,0))
    
    Setup = BIG_FONT.render('Setup',1,(0,0,0))
    SetupShadow = BIG_FONT.render('Setup',1,(150,150,150))
    WINDOW.blit(SetupShadow,((GAME_WIDTH-Setup.get_width())//2+4,100+4))  
    WINDOW.blit(Setup,((GAME_WIDTH-Setup.get_width())//2,100))


    white = FONT.render('White',1,(0,0,0))
    black = FONT.render('Black',1,(0,0,0))
    whiteshadow = FONT.render('White',1,(150,150,150))
    blackshadow = FONT.render('Black',1,(150,150,150))
    WINDOW.blit(blackshadow,(GAME_WIDTH*3/4-black.get_width()//2+4,GAME_HEIGHT//4+79))
    WINDOW.blit(whiteshadow,(GAME_WIDTH//4-white.get_width()//2+4,GAME_HEIGHT//4+79))
    WINDOW.blit(black,(GAME_WIDTH*3/4-black.get_width()//2,GAME_HEIGHT//4+75))
    WINDOW.blit(white,(GAME_WIDTH//4-white.get_width()//2,GAME_HEIGHT//4+75))
    WINDOW.blit(BLACK_QUEEN_IMAGE_SETUP,(GAME_WIDTH*3/4-BLACK_QUEEN_IMAGE_SETUP.get_width()//2,GAME_HEIGHT//4))
    WINDOW.blit(WHITE_QUEEN_IMAGE_SETUP,(GAME_WIDTH//4-WHITE_QUEEN_IMAGE_SETUP.get_width()//2,GAME_HEIGHT//4))
    
    time = FONT.render('Time',1,(0,0,0))
    timeshadow = FONT.render('Time',1,(150,150,150))
    WINDOW.blit(timeshadow,((GAME_WIDTH-time.get_width())//2+4,375+4))  
    WINDOW.blit(time,((GAME_WIDTH-time.get_width())//2,375))
    
    START_BUTTON.draw()
    BACK_BUTTON.draw()
    for box in input_boxes:
        box.draw(WINDOW)


    p.display.update()
           
def GameSetup():
    clock = p.time.Clock()
    run = True
    while run:
        events = p.event.get()
        clock.tick(FPS)
        drawGameSetup()
        
        ''' Events '''
        for event in events:
            if event.type == p.QUIT:
                p.quit()
                sys.exit()
                
            for box in input_boxes:
                if box == input_boxes[2]:
                    if box.text.isnumeric():pass
                    else: box.text = ''
                box.handle_event(event)
                
        for box in input_boxes:
            box.update()

        for object in OBJECTS[2:4]:
            object.process()    

    p.quit()    

       
def drawGame(screen,gl,validMoves,selected,wP,bP,last_move,whiteWon,blackWon,draw):
    WINDOW.fill(WHITE)
    WINDOW.blit(BACKGROUND_IMAGE,(0,0))
    GAME_BACK_BUTTON.draw()
    # board
    drawChess(WINDOW,gl,validMoves,selected)
    # users
    WINDOW.blit(BLACK_QUEEN_IMAGE_SETUP,(BLACK_QUEEN_IMAGE_SETUP.get_width()//2,70))
    WINDOW.blit(WHITE_QUEEN_IMAGE_SETUP,(WHITE_QUEEN_IMAGE_SETUP.get_width()//2,GAME_HEIGHT-130))
    wtext = NAME_FONT.render('{}'.format(wP),1,(0,0,0))
    btext = NAME_FONT.render('{}'.format(bP),1,(0,0,0))
    wtextshadow = NAME_FONT.render('{}'.format(wP),1,(150,150,150))
    btextshadow = NAME_FONT.render('{}'.format(bP),1,(150,150,150))
    WINDOW.blit(btextshadow,(BLACK_QUEEN_IMAGE_SETUP.get_width()//2+100+3,70+(BLACK_QUEEN_IMAGE_SETUP.get_height()+btext.get_height())//4+3))
    WINDOW.blit(wtextshadow,(WHITE_QUEEN_IMAGE_SETUP.get_width()//2+100+3,GAME_HEIGHT-130+(WHITE_QUEEN_IMAGE_SETUP.get_height()+btext.get_height())//4+3))
    WINDOW.blit(btext,(BLACK_QUEEN_IMAGE_SETUP.get_width()//2+100,70+(BLACK_QUEEN_IMAGE_SETUP.get_height()+btext.get_height())//4))
    WINDOW.blit(wtext,(WHITE_QUEEN_IMAGE_SETUP.get_width()//2+100,GAME_HEIGHT-130+(WHITE_QUEEN_IMAGE_SETUP.get_height()+btext.get_height())//4))
    # last move
    last_move_text = NAME_FONT.render('Last Move:',1,(0,0,0))
    last_move_notation = NAME_FONT.render('{}'.format(last_move),1,(20,20,20))
    last_move_text_shadow = NAME_FONT.render('Last Move:',1,(150,150,150))
    last_move_notation_shadow = NAME_FONT.render('{}'.format(last_move),1,(150,150,150))
    WINDOW.blit(last_move_text_shadow,(BLACK_QUEEN_IMAGE_SETUP.get_width()//2-2,(GAME_HEIGHT-last_move_text_shadow.get_height())//2+3))
    WINDOW.blit(last_move_text,(BLACK_QUEEN_IMAGE_SETUP.get_width()//2-5,(GAME_HEIGHT-last_move_text_shadow.get_height())//2))
    WINDOW.blit(last_move_notation_shadow,(BLACK_QUEEN_IMAGE_SETUP.get_width()//2+last_move_text.get_width()-2,(GAME_HEIGHT-last_move_text_shadow.get_height())//2+3))
    WINDOW.blit(last_move_notation,(BLACK_QUEEN_IMAGE_SETUP.get_width()//2+last_move_text.get_width()-5,(GAME_HEIGHT-last_move_text_shadow.get_height())//2))
    
    if whiteWon:drawResult('White Won!')
    if blackWon:drawResult('Black Won!')
    if draw:drawResult('Draw!')

def game():

    clock = p.time.Clock()
    gl = ChessEngine.GameLogic()
    validMoves = gl.getValidMoves()
    moveMade = False  # flag for when a move is made

    load_images()
    
    selected = ()
    playerClicks = [] # keep track of player clicks --two tuples:[(selected),(destination)]
    
    ''' 
    FUTURE:
     - Ranks and files (a,b,c..//1,2,3..)
     - unique users stats
     - timer
     - Move log
     - showcase pieces captured
    '''
    whitePlayer = INPUT['white']
    blackPlayer = INPUT['black']
    # time = INPUT['time']
    # whiteTimer = time
    # blackTimer = time
    last_move = ''
    gameOver = False
    whiteWon = False
    blackWon = False
    draw = False
    run = True
    while run:
        for event in p.event.get():
            
            if event.type == p.QUIT:
                run = False
                sys.exit()
            #Mouse Handling 
            elif event.type == p.MOUSEBUTTONDOWN and event.button == 1:
                if not gameOver:
                    location = p.mouse.get_pos()
                    if location[0] > 7*TILE_SIZE+GAME_WIDTH//4+45 or location[0] < 0*TILE_SIZE+GAME_WIDTH//4-45 :pass
                    else:
                        row = location[1]//TILE_SIZE
                        col = (location[0]-(GAME_WIDTH//4-45))//TILE_SIZE
                        # print(row,col)
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
                            for i in range(len(validMoves)):
                                if move == validMoves[i]:
                                    last_move = move.getChessNotation()
                                    PIECE_MOVE.play()
                                    gl.make_move(validMoves[i])
                                    moveMade = True
                                    selected = () #reset clicks
                                    playerClicks = []
                            if not moveMade:playerClicks = [selected]
                        
            # Key Handling
            elif event.type == p.KEYDOWN:
                if event.key == p.K_z: # undo when z is pressed pr button is pressed
                    gl.undo_move()
                    gl.checkMate = False
                    gl.staleMate = False
                    moveMade = True
                    gameOver = False
                    whiteWon = False
                    blackWon = False
                    draw = False
                # RESET
                if event.key == p.K_r:
                    gl=ChessEngine.GameLogic()
                    validMoves = gl.getValidMoves()
                    selected = ()
                    playerClicks = []
                    gl.checkMate = False
                    gl.staleMate = False
                    gameOver = False
                    moveMade = False
                    whiteWon = False
                    blackWon = False
                    draw = False
        if moveMade:
            validMoves = gl.getValidMoves()
            moveMade = False

        if gl.checkMate:
            gameOver = True
            if gl.whiteToMove: # black won
                blackWon = True
            else: # white won
                whiteWon = True
        
        if gl.staleMate:
            gameOver = True
            draw = True
        
        OBJECTS[4].process()
        
        drawGame(WINDOW,gl,validMoves,selected,whitePlayer,blackPlayer,last_move,whiteWon,blackWon,draw)
        clock.tick(FPS)
        p.display.update()
        # p.display.flip()

''' BUTTONS '''
PLAY_BUTTON = Button((GAME_WIDTH-BUTTON_WIDTH)//2,(GAME_HEIGHT-BUTTON_HEIGHT)//2+150,BUTTON_WIDTH,BUTTON_HEIGHT, PLAY_BUTTON_IMAGE, '', GameSetup)
QUIT_BUTTON = Button((GAME_WIDTH-BUTTON_WIDTH)//2,PLAY_BUTTON.y+110,BUTTON_WIDTH,BUTTON_HEIGHT, QUIT_BUTTON_IMAGE, '', quit_function)
START_BUTTON = Button((GAME_WIDTH-BUTTON_WIDTH)//2+200,(GAME_HEIGHT-BUTTON_HEIGHT)//2+150+110,BUTTON_WIDTH,BUTTON_HEIGHT, START_BUTTON_IMAGE, '', game)
BACK_BUTTON = Button((GAME_WIDTH-BUTTON_WIDTH)//2-200,(GAME_HEIGHT-BUTTON_HEIGHT)//2+150+110,BUTTON_WIDTH,BUTTON_HEIGHT, BACK_BUTTON_IMAGE, '', MainMenu)

GAME_BACK_BUTTON = Button(GAME_WIDTH-undo_width-10,GAME_HEIGHT-undo_height-30,undo_width,BUTTON_HEIGHT-30, BACK_BUTTON_IMAGE, '', GameSetup)
# UNDO_BUTON = Button(GAME_WIDTH-undo_width-20,GAME_HEIGHT-undo_height-20,undo_width,undo_height,UNDO_BUTTON_IMAGE,'',undo_button_function)

''' INPUT '''
whiteInput = InputBox(GAME_WIDTH//4-100,GAME_HEIGHT//4+50+75, 140, 40,tag='white')
blackInput = InputBox(GAME_WIDTH*3/4-100,GAME_HEIGHT//4+50+75, 140, 40,tag='black')
timeInput = InputBox(GAME_WIDTH//2-100,375+50,140,40,tag='time')
input_boxes = [whiteInput, blackInput,timeInput]


''' START '''
if __name__ == '__main__':MainMenu()