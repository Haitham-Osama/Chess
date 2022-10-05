
'''
This class is responsible for storing all the information about the current state of a chess game. It will also 
be responsible for determining the valid moves at the current state making and undoing moves. It will also keep a move log.
'''

class GameLogic:
    def __init__(self):
        '''
        Board is an 8*8 2d list, each element has 2 chars.
        - First element is color (b or w)
        - second element is the type of piece 
        - '--' is an empty space
        '''
        self.board = [['bR','bN','bB','bQ','bK','bB','bN','bR'],
                      ['bp','bp','bp','bp','bp','bp','bp','bp'],
                      ['--','--','--','--','--','--','--','--'],
                      ['--','--','--','--','--','--','--','--'],
                      ['--','--','--','--','--','--','--','--'],
                      ['--','--','--','--','--','--','--','--'],
                      ['wp','wp','wp','wp','wp','wp','wp','wp'],
                      ['wR','wN','wB','wQ','wK','wB','wN','wR']]
        self.moveFunctions = {'p':self.getPawnMoves,'R':self.getRookMoves,
                              'N':self.getKnightMoves,'B':self.getBishopMoves,
                              'Q':self.getQueenMoves,'K':self.getKingMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7,4)
        self.blackKingLocation = (0,4)
        self.checkMate = False
        self.staleMate = False
        self.enpassantPossible = () # coordinates where passant capture is possible
        
        self.currentCastlingRights = CastleRights(True,True,True,True)
        # how to copy castling rights from what were modifing in the updateCastleRights function and then
        # store it in a log that keeps track of these changes as we're not creating another object each time; we're modifing it
        self.castleRightsLog = [CastleRights(self.currentCastlingRights.wks,self.currentCastlingRights.bks,
                                             self.currentCastlingRights.wqs,self.currentCastlingRights.bqs)]
    
    ''' Takes a move as a parameter and executes it '''
    def make_move(self,move):
        # move
        # this will not work for casling, pawn promotion and en-passent, they are done seperatly 
        self.board[move.startRow][move.startCol] = '--'
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) # log the move
        
        # update the king's location if moved 
        if move.pieceMoved == 'wK':self.whiteKingLocation = (move.endRow,move.endCol)
        if move.pieceMoved == 'bK':self.blackKingLocation = (move.endRow,move.endCol)            
        self.whiteToMove = not self.whiteToMove # swap players
        
        # pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'
            
        # enpassant move
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = '--' # capturing the pawn
        
            #update enpassantPossible variable
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2: # only on 2 square pawn advances
            self.enpassantPossible=((move.startRow + move.endRow)//2, move.startCol)
        else:
            self.enpassantPossible = ()
        
        # castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2: # kingside castle (if it's +2 it means it moves 2 spaces to the right so it's a king side move)
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol + 1] # move the rook
                self.board[move.endRow][move.endCol+1] = '--' # erase old rook
            else: # queen side move
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol - 2] # move the rook
                self.board[move.endRow][move.endCol-2] = '--' # erase old rook
                
        # castling rights (if it's a king or castle move)
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRights.wks,self.currentCastlingRights.bks,
                                                 self.currentCastlingRights.wqs,self.currentCastlingRights.bqs))
            
    ''' Undo the last move'''
    def undo_move(self):
        if len(self.moveLog) != 0: 
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            
            #update the king's location if needed 
            if move.pieceMoved == 'wK':self.whiteKingLocation = (move.startRow,move.startCol)
            if move.pieceMoved == 'bK':self.blackKingLocation = (move.startRow,move.startCol)                  
            self.whiteToMove = not self.whiteToMove # swap players
            
            # undo enpassant 
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--' # leave landing square black
                self.board[move.startRow][move.endCol] = move.pieceCaptured                
                self.enpassantPossible = (move.endRow, move.endCol)
                
                # undo a 2 square pawn advance
            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()

            # undo castling rights
            self.castleRightsLog.pop() # get rid of the new castle rights from the move we're undoing
            # set the current castle rights to the last one in the list
            newRights = self.castleRightsLog[-1] 
            self.currentCastlingRights = CastleRights(newRights.wks,newRights.bks,newRights.wqs,newRights.bqs)    
            
            # undo castle move
            if move.isCastleMove:
                if move.endCol - move.startCol ==2: # king side
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1] = '--'
                else: # queen side
                    self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1]
                    self.board[move.endRow][move.endCol+1] = '--'

    ''' All moves considering checks'''
    def getValidMoves(self):
        # debuging 
        # for log in self.castleRightsLog:
        #     print(log.wks,log.bqs,log.wqs,log.bqs)

        ### copy the current enpassant and castling rights so they don't change while making and undoing moves to get valid moves
        tempEnpassantPossible = self.enpassantPossible
        tempCastleRights = CastleRights(self.currentCastlingRights.wks,self.currentCastlingRights.bks,
                                        self.currentCastlingRights.wqs,self.currentCastlingRights.bqs) 
        # 1- get all possible moves and castle moves
        moves = self.getAllPossibleMoves()
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0],self.whiteKingLocation[1],moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0],self.blackKingLocation[1],moves)
        # 2- for each move,make the move
        for i in range(len(moves)-1,-1,-1):
            self.make_move(moves[i])
        # 3- generate all oponent's moves
        # 4- for each of your opponent's moves, see if they attack your king
        # 5- if they do attack your king, not a valid move
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove   
            self.undo_move()
        ''' Checkmate and stalemate'''
        if len(moves) == 0:
            if self.inCheck():self.checkMate = True
            else:self.staleMate = True

        self.enpassantPossible = tempEnpassantPossible
        self.currentCastlingRights = tempCastleRights
        return moves
        
    
    ''' ADVANCED ALGORITHM''' #! not completed/used
    def checkPinsandChecks(self):
        pins = []
        checks = []
        inCheck = False
        if self.whiteToMove:
            enemyColor = 'b'
            allyColor = 'w'
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = 'w'
            allyColor = 'b'
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        directions = ((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)) 
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = () # reset possible pins
            for i in range(1,7):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: # on board
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor:
                        if possiblePin == (): # 1st allied piece could be pinned
                            possiblePin = (endRow,endCol,d[0],d[1])
                        else: # 2nd allied piece, so no pin or check possible in this direction
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]    
    
    ''' NAIVE METHOD '''
    ''' determine if the current player is in check''' 
    def inCheck(self):
        if self.whiteToMove:return self.underAttack(self.whiteKingLocation[0],self.whiteKingLocation[1])
        else:return self.underAttack(self.blackKingLocation[0],self.blackKingLocation[1])    
    
    ''' determine if the enemy can attack the square (r,c)'''
    def underAttack(self,r,c):
        self.whiteToMove = not self.whiteToMove # switch to opponent's turn
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove # switch turns back to the original player
        for move in oppMoves:
            if move.endRow == r and move.endCol == c: # sqaure is under attack
                return True
        return False
    
    ''' All moves without considering checks'''
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                    turn = self.board[r][c][0] # w or b
                    if (turn == 'w' and self.whiteToMove) or (turn =='b' and not self.whiteToMove):
                        piece = self.board[r][c][1]
                        self.moveFunctions[piece](r,c,moves) # calls the appropriate function based on the piece type
        return moves
        
    ''' Pieces Moves '''
    def getPawnMoves(self,r,c,moves):
        if self.whiteToMove: # white pawn moves
            if self.board[r-1][c] == '--': # 1 square move
                moves.append(Move((r,c),(r-1,c),self.board))
                if r == 6 and self.board[r-2][c] == '--': # 2 squares move
                    moves.append(Move((r,c),(r-2,c),self.board))
            if c - 1 >= 0: # left capture
                if self.board[r-1][c-1][0] == 'b': # enemy piece
                    moves.append(Move((r,c),(r-1,c-1),self.board))
                elif (r-1,c-1) == self.enpassantPossible:
                    moves.append(Move((r,c),(r-1,c-1),self.board,isEnpassantMove=True))
            if c + 1 <= 7: # right capture
                if self.board[r-1][c+1][0] == 'b':
                    moves.append(Move((r,c),(r-1,c+1),self.board))
                elif (r-1,c+1) == self.enpassantPossible:
                    moves.append(Move((r,c),(r-1,c+1),self.board,isEnpassantMove=True))            
                        
        else: # black pawn moves
            if self.board[r+1][c] == '--': # 1 square move
                moves.append(Move((r,c),(r+1,c),self.board))
                if r == 1 and self.board[r+2][c] == '--': # 2 squares move
                    moves.append(Move((r,c),(r+2,c),self.board))
            if c - 1 >= 0: # left capture
                if self.board[r+1][c-1][0] == 'w': # enemy piece
                    moves.append(Move((r,c),(r+1,c-1),self.board))
                elif (r+1,c-1) == self.enpassantPossible:
                    moves.append(Move((r,c),(r+1,c-1),self.board,isEnpassantMove=True))                    
            if c + 1 <= 7: # right capture
                if self.board[r+1][c+1][0] == 'w':
                    moves.append(Move((r,c),(r+1,c+1),self.board))   
                elif (r+1,c+1) == self.enpassantPossible:
                    moves.append(Move((r,c),(r+1,c+1),self.board,isEnpassantMove=True))                             
                
                    
    def getRookMoves(self,r,c,moves):
        directions = ((-1,0),(0,-1),(1,0),(0,1)) # up, left, down, right
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1,8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i # it'll only move in one direction because of the 0's in the directions tupple
                if 0 <= endRow < 8 and 0 <= endCol < 8: # if it's on board
                    endPiece = self.board[endRow][endCol]
                    if endPiece == '--': #empty space valid
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                    elif endPiece[0] == enemyColor: # enemy piece valid
                        moves.append(Move((r,c),(endRow,endCol),self.board))        
                        break
                    else: # friendly piece invalid
                        break                
                else:break # off board
    
    def getBishopMoves(self,r,c,moves):
        directions = ((-1,-1),(-1,1),(1,-1),(1,1)) # diaganols
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1,8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i 
                if 0 <= endRow < 8 and 0 <= endCol < 8: # if it's on board
                    endPiece = self.board[endRow][endCol]
                    if endPiece == '--': #empty space valid
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                    elif endPiece[0] == enemyColor: # enemy piece valid
                        moves.append(Move((r,c),(endRow,endCol),self.board))        
                        break
                    else: # friendly piece invalid
                        break                
                else:break # off board            
    
    def getKnightMoves(self,r,c,moves):
        directions = ((-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)) # all L movements
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            endRow = r + d[0]
            endCol = c + d[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor or endPiece == '--':
                    moves.append(Move((r,c),(endRow,endCol),self.board))

    def getQueenMoves(self,r,c,moves): # Rook and bishop combined
        self.getBishopMoves(r,c,moves)
        self.getRookMoves(r,c,moves)
    
    def getKingMoves(self,r,c,moves):
        kingMoves = ((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1))  
        enemyColor = 'b' if self.whiteToMove else 'w'
        allyColor = 'w' if enemyColor == 'b' else 'b'
        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor or endPiece == '--':
                    moves.append(Move((r,c),(endRow,endCol),self.board))   
                     
    ''' Castling related'''
    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK': # white lost castling rights on both sides
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.pieceMoved == 'bK': # black lost castling rights on both sides
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        # if a rook is moved (w or b) lose their castling rights on that rook side,
        # (could be done by giving each rook an Id and check if they moved)
        elif move.pieceMoved == 'wR': 
            if move.startRow == 7:
                if move.startCol == 0: # left rook
                    self.currentCastlingRights.wqs = False
                elif move.startCol == 7: # right rook
                    self.currentCastlingRights.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0: # left rook
                    self.currentCastlingRights.bqs = False
                elif move.startCol == 7: # right rook
                    self.currentCastlingRights.bks = False    
                    
                    
    # generale all valid castle moves for the king at (r,c) and add them to the list of moves
    def getCastleMoves(self,r,c,moves):
         # can't castle while we're in check
        if self.underAttack(r,c):
            return
        # king side
        if (self.whiteToMove and self.currentCastlingRights.wks) or (not self.whiteToMove and self.currentCastlingRights.bks):
            self.getKingSideCastleMoves(r,c,moves)
        # queen side
        if (self.whiteToMove and self.currentCastlingRights.wqs) or (not self.whiteToMove and self.currentCastlingRights.bqs):
            self.getQueenSideCastleMoves(r,c,moves)
        
        
    def getKingSideCastleMoves(self,r,c,moves): # check 2 squares
        # we don't need to check if it's on board because we'll only check it if they still have castling rights
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.underAttack(r,c+1) and not self.underAttack(r,c+2):
                moves.append(Move((r,c),(r,c+2),self.board,isCastleMove=True))
            
    
    def getQueenSideCastleMoves(self,r,c,moves): # check 3 squares
        # we don't need to check if it's on board because we'll only check it if they still have castling rights
        if self.board[r][c-1] == '--' and self.board[r][c-2] and self.board[r][c-3] == '--':
            if not self.underAttack(r,c-1) and not self.underAttack(r,c-2):
                moves.append(Move((r,c),(r,c-2),self.board,isCastleMove=True))
         
class CastleRights:
    def __init__(self,wks,bks,wqs,bqs): #  (w or b) + (king or queen) + side
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs
        
   
class Move:
    # maps keys to values
    # key : values
    # Ranks and files == Rows and columns in chess
    ranksToRows = {'1':7,'2':6,'3':5,'4':4,
                   '5':3,'6':2,'7':1,'8':0}    
    rowToRanks = {v: k for k,v in ranksToRows.items()}
    
    filestoCols = {'a':0,'b':1,'c':2,'d':3,
                   'e':4,'f':5,'g':6,'h':7}
    colsToFiles = {v: k for k,v in filestoCols.items()}
    
    def __init__(self,startSq,endSq,board,isEnpassantMove=False,isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
    
        # pawn promotion
        self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7)
        # Enpassant
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'
        # self.isEnpassantMove =  (self.pieceMoved[1] == 'p' and (self.endRow,self.endCol) == enpassantPossible)
        
        # castle move
        self.isCastleMove = isCastleMove
        
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
    
    ''' Overriding the equals method ''' # TODO: come back to it to understand it
    def __eq__(self,other):
        if isinstance(other,Move):
            return self.moveID == other.moveID
        return False
    
    def getChessNotation(self):
        return self.getRankFile(self.startRow,self.startCol) + self.getRankFile(self.endRow,self.endCol)
    def getRankFile(self,r,c):
        return self.colsToFiles[c]+self.rowToRanks[r]