
# Copyright (c) 2026 Mohamed-Amine Ben Njima
# Licensed under the MIT License.
# See LICENSE for details.

import copy

class GameState():
    def __init__(self):
        self.board = [
            [Square((0, 0), "wR"), Square((0, 1), "wp"), Square((0, 2), "--"), Square((0, 3), "--"), Square((0, 4), "--"), Square((0, 5), "--"), Square((0, 6), "bp"), Square((0, 7), "bR")],
            [Square((1, 0), "wN"), Square((1, 1), "wp"), Square((1, 2), "--"), Square((1, 3), "--"), Square((1, 4), "--"), Square((1, 5), "--"), Square((1, 6), "bp"), Square((1, 7), "bN")],
            [Square((2, 0), "wB"), Square((2, 1), "wp"), Square((2, 2), "--"), Square((2, 3), "--"), Square((2, 4), "--"), Square((2, 5), "--"), Square((2, 6), "bp"), Square((2, 7), "bB")],
            [Square((3, 0), "wQ"), Square((3, 1), "wp"), Square((3, 2), "--"), Square((3, 3), "--"), Square((3, 4), "--"), Square((3, 5), "--"), Square((3, 6), "bp"), Square((3, 7), "bQ")],
            [Square((4, 0), "wK"), Square((4, 1), "wp"), Square((4, 2), "--"), Square((4, 3), "--"), Square((4, 4), "--"), Square((4, 5), "--"), Square((4, 6), "bp"), Square((4, 7), "bK")],
            [Square((5, 0), "wB"), Square((5, 1), "wp"), Square((5, 2), "--"), Square((5, 3), "--"), Square((5, 4), "--"), Square((5, 5), "--"), Square((5, 6), "bp"), Square((5, 7), "bB")],
            [Square((6, 0), "wN"), Square((6, 1), "wp"), Square((6, 2), "--"), Square((6, 3), "--"), Square((6, 4), "--"), Square((6, 5), "--"), Square((6, 6), "bp"), Square((6, 7), "bN")],
            [Square((7, 0), "wR"), Square((7, 1), "wp"), Square((7, 2), "--"), Square((7, 3), "--"), Square((7, 4), "--"), Square((7, 5), "--"), Square((7, 6), "bp"), Square((7, 7), "bR")],
        ]

        self.turn = 'w'
        self.turnCount = 1

        self.concluded = False
        self.winner = '-'

        self.whitePieces:list[tuple[int, int]] = []
        self.blackPieces:list[tuple[int, int]] = []

        self.moveLog:list[str] = []
        self.prevBoards:list[list[list[Square]]] = []
        self.prevEnPassant:list[dict] = []

        self.enPassantPieces:dict = {}

        self.updatePieceDataAndPiecelists()
        self.determineWinCondition()

    def undoMove(self):
        if self.winner != "-":
            return
        if self.turnCount <= 1 or self.board == self.prevBoards[len(self.prevBoards)-1]:
            return
        self.turn = 'w' if self.turn == 'b' else 'b'
        self.turnCount -= 1
        self.board = self.prevBoards[len(self.prevBoards)-1]
        self.enPassantPieces = self.prevEnPassant[len(self.prevEnPassant)-1]
        del self.prevEnPassant[len(self.prevEnPassant)-1]
        del self.prevBoards[len(self.prevBoards)-1]
        del self.moveLog[len(self.moveLog)-1]
        self.updatePieceDataAndPiecelists()
        self.determineWinCondition()

    def newTurn(self):
        self.turn = 'b' if self.turn == 'w' else 'w'
        for x in list(self.enPassantPieces.keys()):
            if int(x) != self.turnCount:
                del self.enPassantPieces[x]
        self.turnCount += 1

    def recordMoveHistory(self):
        self.prevBoards.append(copy.deepcopy(self.board))
        self.prevEnPassant.append(copy.deepcopy(self.enPassantPieces))

    def recordChessNotation(self, pieceMoved:Square, pieceCaptured:Square, move:Move):
        self.moveLog.append(self.getChessNotation(pieceMoved, pieceCaptured, move))
    
    def getChessNotation(self, pieceMoved:Square, pieceCaptured:Square, move:Move) -> str:
        if move.initSquare.isKingCastle(move, self):
            match pieceMoved.side:
                case 'w':
                    if move.endCol - move.startCol == 2:
                        return "0-0"
                    elif move.endCol - move.startCol == -2:
                        return "0-0-0"
                case 'b':
                    if move.endCol - move.startCol == -2:
                        return "0-0"
                    elif move.endCol - move.startCol == 2:
                        return "0-0-0"

        pieceAbbreviation = "" if pieceMoved.type in ("p", "-") else pieceMoved.type
        isCapture:str = ""
        try:
            isCapture = "x" if pieceCaptured.type != "-" and pieceMoved != pieceCaptured else ""
        except:
            isCapture = ""
        isCapture = move.ColsAndFiles(pieceMoved.col) + isCapture if pieceMoved.type == 'p' and isCapture == 'x' else isCapture
        endPosition = move.ColsAndFiles(move.endCol) + str(move.endRow+1)
        return pieceAbbreviation+isCapture+endPosition

    def executeMove(self, playerClicks:list[tuple[int, int]]) -> list:
        if len(playerClicks) != 2:
            return []
        
        startSq = playerClicks[0]
        endSq = playerClicks[1]
        movedPiece = self.board[startSq[0]][startSq[1]]
        movePieceSide = movedPiece.side
        legal = endSq in movedPiece.legalMoves

        if not legal:
            return []
        
        move = Move(playerClicks[0], playerClicks[1], self.board)
        isPromotion = move.initSquare.isPawnPromotion(move)
        self.recordMoveHistory()
        self.recordChessNotation(self.board[move.startCol][move.startRow], self.board[move.capturedCol][move.capturedRow], move)

        if move.initSquare.isEnPassantSetup(move):
            self.enPassantPieces[str(self.turnCount)] = (move.endCol, move.endRow)
        if move.initSquare.isEnPassantCapture(move, self):
            move.capturedCol = move.endCol
            move.capturedRow = move.startRow
        if move.initSquare.isKingCastle(move, self):
            self.board[3 if move.endCol - move.startCol == -2 else 5][move.endRow].updateId(move.initSquare.side+'R')
            self.board[0 if move.endCol - move.startCol == -2 else 7][move.endRow].updateId("--")
        
        self.board[move.capturedCol][move.capturedRow].updateId('--')
        self.board[move.endCol][move.endRow].updateId(move.initSquare.id)
        self.board[move.endCol][move.endRow].hasMoved = True
        self.board[move.startCol][move.startRow].updateId('--')

        if isPromotion:
            return ["promotion", playerClicks]

        self.updatePieceDataAndPiecelists()
        self.determineWinCondition()
        if self.concluded:
            if self.winner != '1/2':
                self.moveLog[-1]+="#"
            else:
                self.moveLog.append("1/2-1/2")
        match movePieceSide:
            case 'b':
                for pos in self.blackPieces:
                    if self.board[pos[0]][pos[1]].attackingKing:
                        self.moveLog[-1] += "+" if self.moveLog[-1][-1] != "#" else ""
            case 'w':
                for pos in self.whitePieces:
                    if self.board[pos[0]][pos[1]].attackingKing:
                        self.moveLog[-1] += "+" if self.moveLog[-1][-1] != "#" else ""
        self.newTurn()
        return []

    def finishMoveAfterPromotion(self, playerClicks:list[tuple[int, int]], piece:str):
        move = Move(playerClicks[0], playerClicks[1], self.board)
        self.board[move.endCol][move.endRow].updateId(self.board[move.endCol][move.endRow].side+piece)
        self.updatePieceDataAndPiecelists()
        self.determineWinCondition()
        self.newTurn()
        if self.concluded:
            if self.winner != '1/2':
                self.moveLog[-1]+="="+piece+"#"
                return
            else:
                self.moveLog.append("1/2-1/2")
                return
        match self.board[playerClicks[1][0]][playerClicks[1][1]]:
            case 'b':
                for pos in self.blackPieces:
                    if self.board[pos[0]][pos[1]].attackingKing:
                        self.moveLog[-1] += "="+piece+"+" if self.moveLog[-1][-1] != "#" else ""
                        return
            case 'w':
                for pos in self.whitePieces:
                    if self.board[pos[0]][pos[1]].attackingKing:
                        self.moveLog[-1] += "="+piece+"+" if self.moveLog[-1][-1] != "#" else ""
                        return
        self.moveLog[-1]+="="+piece

    def isPieceFree(self, position:tuple[int, int]) -> bool:
        return self.board[position[0]][position[1]].id == "--"

    def isCheckMate(self, side:str) -> bool: #answers the question "did i win?" not "did i lose?"
        totalMovesForOpp = []
        OppKing:tuple[int, int] = (-1, -1)
        match side:
            case 'w':
                for position in self.blackPieces:
                    piece = self.board[position[0]][position[1]]
                    totalMovesForOpp += piece.legalMoves
                    if piece.type == 'K':
                        OppKing = position
            case 'b':
                for position in self.whitePieces:
                    piece = self.board[position[0]][position[1]]
                    totalMovesForOpp += piece.legalMoves
                    if piece.type == 'K':
                        OppKing = position
        if OppKing == (-1, -1):
            raise ValueError("Couldnt find enemy king to determine checkmate")
        OppKingPiece = self.board[OppKing[0]][OppKing[1]]
        if len(totalMovesForOpp) <= 0 and OppKingPiece.underAttack == True:
            return True
        return False

    def isStalemate(self, side:str) -> bool: #answers the question "did i blunder into stalemate?"
        totalMovesForOpp = []
        OppKing:tuple[int, int] = (-1, -1)
        match side:
            case 'w':
                for position in self.blackPieces:
                    piece = self.board[position[0]][position[1]]
                    totalMovesForOpp += piece.legalMoves
                    if piece.type == 'K':
                        OppKing = position
            case 'b':
                for position in self.whitePieces:
                    piece = self.board[position[0]][position[1]]
                    totalMovesForOpp += piece.legalMoves
                    if piece.type == 'K':
                        OppKing = position
        if OppKing == (-1, -1):
            raise ValueError("Couldnt find enemy king to determine checkmate")
        OppKingPiece = self.board[OppKing[0]][OppKing[1]]
        if len(totalMovesForOpp) <= 0 and OppKingPiece.underAttack == False:
            return True
        return False

    def determineWinCondition(self):
        didBlackWin:bool = self.isCheckMate('b')
        didWhiteWin:bool = self.isCheckMate('w')
        isStale:bool = self.isStalemate('w') or self.isStalemate('b')

        if didBlackWin:
            self.concluded = True
            self.winner = 'b'
        elif didWhiteWin:
            self.concluded = True
            self.winner = 'w'
        elif isStale:
            self.concluded = True
            self.winner = '1/2'
        else:
            return

    def updatePieceDataAndPiecelists(self):
        self.blackPieces.clear()
        self.whitePieces.clear()
        for x in self.board:
            for piece in x:
                if piece.side == 'b':
                    self.blackPieces.append(piece.position)
                elif piece.side == 'w':
                    self.whitePieces.append(piece.position)
                piece.updateLegalMovesData(self)
        for x in self.board:
            for piece in x:
                piece.updateUnderAttack(self)

class Square:
    def __init__(self, coords:tuple[int, int], contents:str):
        if len(contents) != 2:
            raise ValueError("the contents of the piece should be of two letters being the side and the type, example: wK (white King)")
        
        self.col = coords[0]
        self.row = coords[1]
        self.position = coords

        self.side = contents[0].lower() if contents != "--" else "-"
        self.oppositeSide = 'b' if self.side == 'w' else 'w'

        self.type = contents[1]
        self.id = contents

        self.legalMoves:list[tuple[int, int]] = []
        self.attackingKing:bool = False
        self.underAttack:bool = False
        self.hasMoved:bool = False

    def updateId(self, newID:str):
        self.id = newID
        self.side = newID[0].lower() if newID != "--" else "-"
        self.oppositeSide = 'b' if newID[0] == 'w' else 'w'
        self.type = newID[1]

    def updateLegalMovesData(self, gs:GameState):
        self.legalMoves = self.getLegalMoves(gs)
        self.attackingKing = self.isAttackingKing(gs.board)

    def updateUnderAttack(self, gs:GameState):
        self.underAttack = self.isUnderAttack(gs)

    def isUnderAttack(self, gs:GameState) -> bool:
        for col in gs.board:
            for piece in col:
                if self.position in piece.legalMoves and self != piece:
                    return True
        return False

    def isPawnPromotion(self, move:Move) -> bool:
        isOurPawn = move.initSquare.position == self.position and move.initSquare.type == 'p'
        destination = 7 if self.side == 'w' else 0
        isEnd = move.endRow == destination
        return (isOurPawn and isEnd)

    def isEnPassantSetup(self, move:Move) -> bool:
        isOurPawn = move.initSquare.position == self.position and move.initSquare.type == 'p'
        direction = 1 if self.side == 'w' else -1
        isSecond = move.endRow == move.startRow+(direction*2)
        return (isOurPawn and isSecond)

    def isKingCastle(self, move:Move, gs:GameState) -> bool:
        if self.type != 'K':
            return False 
        isCastleRightAvailable = None
        isCastleLeftAvailable = None
        match self.side:
            case 'b':
                isCastleRightAvailable = gs.isPieceFree((5, 7)) and gs.isPieceFree((6, 7))
                isCastleLeftAvailable = gs.isPieceFree((1, 7)) and gs.isPieceFree((2, 7)) and gs.isPieceFree((3, 7))
            case 'w':
                isCastleRightAvailable = gs.isPieceFree((5, 0)) and gs.isPieceFree((6, 0))
                isCastleLeftAvailable = gs.isPieceFree((1, 0)) and gs.isPieceFree((2, 0)) and gs.isPieceFree((3, 0))
        isCastleRightAvailable = False if isCastleRightAvailable is None else isCastleRightAvailable
        isCastleLeftAvailable = False if isCastleLeftAvailable is None else isCastleLeftAvailable
        if not self.hasMoved and (move.endCol - move.startCol) in (2, -2):
            return (isCastleLeftAvailable and move.endCol - move.startCol == -2) or (isCastleRightAvailable and move.endCol - move.startCol == 2)
        return False

    def isEnPassantCapture(self, move:Move, gs:GameState) -> bool:
        isOurPawn = move.initSquare.position == self.position and move.initSquare.type == 'p'
        direction = 1 if self.side == 'w' else -1
        isCapturePos = (move.endCol - move.startCol) in (-1, 1) and move.endRow == move.startRow+direction
        enPassantCapturePoint = (move.endCol, move.startRow)
        enPassantPiece = gs.board[enPassantCapturePoint[0]][enPassantCapturePoint[1]]

        if str(gs.turnCount-1) in gs.enPassantPieces:
            return isOurPawn and isCapturePos and enPassantPiece.type == 'p' and enPassantPiece.side == self.oppositeSide and gs.enPassantPieces[str(gs.turnCount-1)] == enPassantPiece.position
        return False

    def isKingStillUnderAttack(self, simMove:Move, gs:GameState) -> bool:
        clGameState:GameState = copy.deepcopy(gs)

        clGameState.board[simMove.capturedCol][simMove.capturedRow].updateId('--')
        clGameState.board[simMove.endCol][simMove.endRow].updateId(simMove.initSquare.id)
        clGameState.board[simMove.startCol][simMove.startRow].updateId('--')

        clGameState.blackPieces.clear()
        clGameState.whitePieces.clear()
        for col in clGameState.board:
            for piece in col:
                if piece.side == 'b':
                    clGameState.blackPieces.append(piece.position)
                elif piece.side == 'w':
                    clGameState.whitePieces.append(piece.position)
                piece.legalMoves = piece.getLegalMoves(clGameState, True)
                piece.attackingKing = piece.isAttackingKing(clGameState.board)
        for x in clGameState.board:
            for piece in x:
                piece.updateUnderAttack(clGameState)

        match self.side:
            case 'w':
                for position in clGameState.blackPieces:
                    piece = clGameState.board[position[0]][position[1]]
                    if piece.attackingKing == True:
                        return True
            case 'b':
                for position in clGameState.whitePieces:
                    piece = clGameState.board[position[0]][position[1]]
                    if piece.attackingKing == True:
                        return True
 
        return False

    def getLegalMoves(self, gs:GameState, isSimulation:bool=False) -> list[tuple[int, int]]:
        if self.id == "--":
            return []
        potentialMoves:list[tuple[int, int]] = []
        legalMoves = []

        match self.type:
            case 'p':
                direction = 1 if self.side == 'w' else -1
                potentialMoves.append((self.col, self.row+direction))
                potentialMoves.append((self.col, self.row+(direction*2)))
                potentialMoves.append((self.col+1, self.row+direction))
                potentialMoves.append((self.col-1, self.row+direction))
            case 'N':
                directions = [(2, 1), (-2, 1), (2, -1), (-2, -1), (1, 2), (-1, 2), (1, -2), (-1, -2)]
                for x in directions:
                    potentialMoves.append((self.col+x[0], self.row+x[1]))
            case 'R':
                for x in range(8):
                    potentialMoves.append((self.col+x, self.row))
                    potentialMoves.append((self.col-x, self.row))
                    potentialMoves.append((self.col, self.row+x))
                    potentialMoves.append((self.col, self.row-x))
            case 'B':
                for x in range(8):
                    potentialMoves.append((self.col+x, self.row+x))
                    potentialMoves.append((self.col-x, self.row-x))
                    potentialMoves.append((self.col-x, self.row+x))
                    potentialMoves.append((self.col+x, self.row-x))
            case 'Q':
                for x in range(8):
                    potentialMoves.append((self.col+x, self.row))
                    potentialMoves.append((self.col-x, self.row))
                    potentialMoves.append((self.col, self.row+x))
                    potentialMoves.append((self.col, self.row-x))
                    potentialMoves.append((self.col+x, self.row+x))
                    potentialMoves.append((self.col-x, self.row-x))
                    potentialMoves.append((self.col-x, self.row+x))
                    potentialMoves.append((self.col+x, self.row-x))
            case 'K':
                directions = [(1, 0), (-1, 0), (0, -1), (0, 1), (1, 1), (-1, 1), (1, -1), (-1, -1), (2, 0), (-2, 0)]
                for x in directions:
                    potentialMoves.append((self.col+x[0], self.row+x[1]))
            case _:
                return []

        for x in potentialMoves:
            legal = self.isLegal(x, gs, isSimulation)
            if legal:
                legalMoves.append(x)

        return legalMoves

    def isLegal(self, coords:tuple[int, int], gs:GameState, fromSimulation:bool = False) -> bool:
        move = Move(self.position, coords, gs.board)
        initSquare = move.initSquare
        board = gs.board
        result = None

        if move.pieceCaptured == None or not (0 <= move.endCol < 8 and 0 <= move.endRow < 8):
            return False

        if move.pieceCaptured.side == initSquare.side:
            return False

        match initSquare.type:
            case 'p':
                isFromStart:bool = False
                isSecondRow:bool = False
                isNextRow:bool = False
                isNextFree:bool = False
                isSecondFree:bool = False
                isNextCollumn = (move.endCol - move.startCol) in (1, -1)

                if initSquare.side == 'b':
                    isFromStart = move.startRow == 6
                    isNextRow = move.endRow == move.startRow-1
                    isSecondRow = move.endRow == move.startRow-2
                    isNextFree = board[move.startCol][move.startRow-1].id == "--"
                    isSecondFree = board[move.startCol][move.startRow-2].id == "--"
                elif initSquare.side == 'w':
                    isFromStart = move.startRow == 1
                    isNextRow = move.endRow == move.startRow+1
                    isSecondRow = move.endRow == move.startRow+2
                    try:
                        isNextFree = board[move.startCol][move.startRow+1].id == "--"
                    except:
                        isNextFree = False
                    try:
                        isSecondFree = board[move.startCol][move.startRow+2].id == "--"
                    except:
                        isSecondFree = False

                if isNextCollumn:
                    if isNextRow and move.pieceCaptured.id != "--":
                        result = True if result is None else result
                    if str(gs.turnCount) in gs.enPassantPieces:
                        if isNextRow and move.pieceCaptured.id == "--" and gs.enPassantPieces[str(gs.turnCount)] == (move.endCol, move.startRow):
                            result = True if result is None else result
                    result = False if result is None else result
                else:
                    if isFromStart and isSecondRow and isSecondFree and isNextFree:
                        result = True if result is None else result
                    elif not isFromStart and isSecondRow:
                        result = False if result is None else result
                    elif isNextRow and isNextFree:
                        result = True if result is None else result
                    elif isNextRow and not isNextFree:
                        result = False if result is None else result
            case "N":
                row_diff = abs(move.endRow - move.startRow)
                col_diff = abs(move.endCol - move.startCol)
                result = sorted([row_diff, col_diff]) == [1, 2]
            case 'B':
                row_diff = move.endRow - move.startRow
                col_diff = move.endCol - move.startCol
                row_dir = sorted([-1, row_diff, 1])[1]
                col_dir = sorted([-1, col_diff, 1])[1]

                isDiagonalMove = abs(col_diff) == abs(row_diff)

                if isDiagonalMove:
                    for x in range(abs(row_diff)):
                        if x == 0:
                            continue
                        xCol = (col_dir*x)+move.startCol
                        xRow = (row_dir*x)+move.startRow
                        targetPiece = board[xCol][xRow]
                        if targetPiece.id != "--":
                            if (xCol,xRow) != (move.endCol,move.endRow):
                                result = False if result is None else result
                                break
                            else:
                                result = True if result is None else result
                                break
                    result = True if result is None else result
            case 'R':
                row_diff = move.endRow - move.startRow
                col_diff = move.endCol - move.startCol
                row_dir = sorted([-1, row_diff, 1])[1]
                col_dir = sorted([-1, col_diff, 1])[1]

                isHorizontalMove = sorted([abs(row_dir), abs(col_dir)]) == [0, 1]

                if isHorizontalMove:
                    slRange = (range(abs(row_diff)) if row_dir != 0 else range(abs(col_diff)))
                    for x in slRange:
                        if x == 0:
                            continue
                        xCol = (col_dir*x)+move.startCol
                        xRow = (row_dir*x)+move.startRow
                        targetPiece = board[xCol][xRow]
                        if targetPiece.id != "--":
                            if (xCol,xRow) != (move.endCol,move.endRow):
                                result = False if result is None else result
                            else:
                                result = True if result is None else result
                    result = True if result is None else result
            case 'Q':
                row_diff = move.endRow - move.startRow
                col_diff = move.endCol - move.startCol
                row_dir = sorted([-1, row_diff, 1])[1]
                col_dir = sorted([-1, col_diff, 1])[1]

                isDiagonalMove = abs(col_diff) == abs(row_diff)
                isHorizontalMove = sorted([abs(row_dir), abs(col_dir)]) == [0, 1]

                if isHorizontalMove or isDiagonalMove:
                    slRange = []
                    if isHorizontalMove:
                        slRange = (range(abs(row_diff)) if row_dir != 0 else range(abs(col_diff)))
                    elif isDiagonalMove:
                        slRange = range(abs(row_diff))
                    else:
                        result = False if result is None else result
                    
                    for x in slRange:
                        if x == 0:
                            continue
                        xCol = (col_dir*x)+move.startCol
                        xRow = (row_dir*x)+move.startRow
                        targetPiece = board[xCol][xRow]
                        if targetPiece.id != "--":
                            if (xCol,xRow) != (move.endCol,move.endRow):
                                result = False if result is None else result
                            else:
                                result = True if result is None else result
                    result = True if result is None else result
            case 'K':
                row_diff = abs(move.endRow - move.startRow)
                col_diff = abs(move.endCol - move.startCol)
                result = sorted([row_diff, col_diff]) in ([1, 1], [0, 1]) if result is None else result
                isCastleRightAvailable = None
                isCastleLeftAvailable = None
                match self.side:
                    case 'b':
                        isCastleRightAvailable = gs.isPieceFree((5, 7)) and gs.isPieceFree((6, 7))
                        isCastleLeftAvailable = gs.isPieceFree((1, 7)) and gs.isPieceFree((2, 7)) and gs.isPieceFree((3, 7))
                    case 'w':
                        isCastleRightAvailable = gs.isPieceFree((5, 0)) and gs.isPieceFree((6, 0))
                        isCastleLeftAvailable = gs.isPieceFree((1, 0)) and gs.isPieceFree((2, 0)) and gs.isPieceFree((3, 0))
                isCastleRightAvailable = False if isCastleRightAvailable is None else isCastleRightAvailable
                isCastleLeftAvailable = False if isCastleLeftAvailable is None else isCastleLeftAvailable
                if not self.hasMoved and (move.endCol - move.startCol) in (2, -2):
                    result = True if (isCastleLeftAvailable and move.endCol - move.startCol == -2) or (isCastleRightAvailable and move.endCol - move.startCol == 2) else result
        result = False if result is None else result

        if result == False or fromSimulation == True:
            return result

        if self.isKingStillUnderAttack(move, gs) == True:
            result = False
        
        return result

    def isAttackingKing(self, board:list[list[Square]]) -> bool:
        if self.id == "--":
            return False
        oppositeKingPos:tuple[int, int] = (-1, -1)
        for col in board:
            for piece in col:
                if piece.id == self.oppositeSide+'K':
                    oppositeKingPos = piece.position
        return oppositeKingPos in self.legalMoves


class Move:
    def __init__(self, startSq:tuple[int, int], endSq:tuple[int, int], board:list[list[Square]]):
        self.startCol = startSq[0]
        self.startRow = startSq[1]
        self.endCol = endSq[0]
        self.endRow = endSq[1]
        self.initSquare = board[self.startCol][self.startRow]
        self.pieceType = self.initSquare.type

        self.capturedCol = self.endCol
        self.capturedRow = self.endRow

        self.pieceCaptured = None

        try:
            self.pieceCaptured = board[self.endCol][self.endRow]
        except:
            self.pieceCaptured = None
    
    def ColsAndFiles(self, x: int|str) -> str:
        if type(x) is str:
            return str("abcdefgh".index(x))
        elif type(x) is int:
            return "abcdefgh"[x]
        return ""