#!/usr/bin/python

from graphics import *
from random import randint
import math
import copy
import time
import os
import multiprocessing
from multiprocessing import Process, Pipe

output = multiprocessing.Queue()
width = 1000
height = 800
smaller = height
offset = 5
offsetInner = 5
images = 0

boxLength = (height - offset) / 8


pieceArr = [[0 for x in range(0, 8)] for x in range(0, 8)]
pieceObjs = []
drawnMoves = []

if __name__ == '__main__':
    win = GraphWin("Chess", width, height)

def main():
    win.setBackground("tan2")

    global images
    player = 0
    pieceClicked = 0
    pieceMove = None
    pieceMoveType = 0
    pieceClickedLast = None
    piecesAval = []
    avalMoves = []
    avalMovesC = []

    if os.path.exists("./pieces"):
        images = 1


    for i in range(0,8):
        for j in range(0, 8):
            c = Rectangle(Point(boxLength * i + offset, boxLength * j + offset),
                          Point(boxLength * (i+1) + offset, boxLength * (j+1) + offset))
            c.draw(win)

            piece = startPos(i, j)
            pieceArr[i][j] = piece
    renderPieces(win, pieceArr)


    while 1:
        mp = win.getMouse()


        delDispMoves()
        if mp.getX() > offset and mp.getX() < smaller - offset and \
                        mp.getY() > offset and mp.getY() < smaller - offset:
            pieceX = math.floor(mp.getX() / boxLength)
            pieceY = math.floor(mp.getY() / boxLength)
            p = Piece(pieceX, pieceY, getPiece(pieceX, pieceY))

            if pieceClicked == 1:
                for h in avalMoves:
                    if p.getX() == h.getX() and p.getY() == h.getY():
                        # print("CLICKED AT: " + str(p.getX()) + ", " + str(p.getY()))
                        movePiece(pieceArr, pieceClickedLast, p.getX(), p.getY())
                        clearBoard()
                        renderPieces(win, pieceArr)
                        player = 1
                pieceClicked = 0

            else:
                del avalMoves[:]
                avalMoves = getSafeMovesPiece(pieceArr, p, -1)

                if p.getP() != 0:
                    if len(avalMoves) != 0:
                        dispMoves(avalMoves, win)
                        pieceClicked = 1
                        pieceClickedLast = p

        else:
            pieceClicked = 0


        if player == 1:
            del avalMovesC[:]
            avalMovesC = getSafeMoves(pieceArr, player)

            if len(avalMovesC) == 0:
                if checkCheck(pieceArr, player) == 1:
                    print("CHECKMATE")
                    return
                else:
                    print("STALEMATE")
                return

            # New process
            if __name__ == '__main__':
                multiprocessing.freeze_support()
                parent_conn, child_conn = Pipe()
                p = Process(target=beginDecision, args=(pieceArr, avalMovesC, parent_conn))
                p.start()
                # try:
                #     print("Waiting 10 seconds")
                #     time.sleep(10)
                #
                # except KeyboardInterrupt:
                #     print("Caught KeyboardInterrupt, terminating workers")
                #     p.terminate()
                #     p.join()
                # print("done")
                p.join()
                print("lmao")
                x = parent_conn.recv()
                print(type(x))

                move = parent_conn.recv()
                move = beginDecision(pieceArr, avalMovesC)
                movePiece(pieceArr, move.getPiece(), move.getX(), move.getY())

            clearBoard()
            renderPieces(win, pieceArr)

            player = -1


        player = -1

    win.close()


def beginDecision(arr, avalMoves, conn):
    move = None
    highest = -1000
    time = 1

    if len(avalMoves) == 0:
        print("this should literally never happen")
        return
    for j in avalMoves:
        #for g in range(1, 10):
        # win.getMouse()
        newArr = copy.deepcopy(arr)
        movePiece(newArr, j.getPiece(), j.getX(), j.getY())

        # clearBoard()
        # renderPieces(win, newArr)

        # print("Begining calculations for piece: " + i.getInfo())
        calcValue = newNode(newArr, 1, -100000, 100000, -1)
        # print("End calc" + str(calcValue))
        if highest < calcValue:
            # print("Found better move")
            # move = Move(Piece(j.getP().getX(), j.getP().getY(), j.getP().getP()), j.getX(), j.getY())
            move = j
            highest = calcValue

    if move == None:
        move = avalMoves[0]


    # max = newNode(arr, 3, -100000, 1000000, 1)
    print("finished")
    conn.send(4)
    conn.close()
    # return move


def newNode(arr, depth, a, b, player):
    # eval board state
    # win.getMouse()

    avalPieces = getPiecesAval(arr, player)

    if depth == 0 or len(avalPieces) == 0:
        board = getBoardState(arr)
        # print(board)
        return board

    if player == 1:
        v = -100000
        for i in avalPieces:
            avalMoves = getMoves(arr, i)
            if avalMoves == -10 or len(avalMoves) == 0:
                continue
            for j in avalMoves:
                newArr = copy.deepcopy(arr)
                movePiece(newArr, i, j.getX(), j.getY())

                # clearBoard()
                # renderPieces(win, newArr)

                v = max(v, newNode(newArr, depth - 1, a, b, -1))
                a = max(a, v)
                if b <= a:
                    break
        return v

    else:
        v = 100000
        for i in avalPieces:
            avalMoves = getMoves(arr, i)
            if avalMoves == -10 or len(avalMoves) == 0:
                continue
            for j in avalMoves:
                newArr = copy.deepcopy(arr)
                movePiece(newArr, i, j.getX(), j.getY())

                # clearBoard()
                # renderPieces(win, newArr)

                v = min(v, newNode(newArr, depth - 1, a, b, 1))
                b = min(b, v)
                if b <= a:
                    break
        return v


    # move


def getBoardState(arr):
    temp = 0.0
    neg = 1
    for i in range(0, 8):
        for j in range(0, 8):
            pVal = arr[i][j]

            if pVal == 0:
                continue

            if pVal <= 6:
                neg = -1
            else:
                neg = 1


            if pVal == 1 or pVal == 7:
                if (i == 3 or i == 4) and (j == 3 or j == 4):
                     temp += (neg * .3)
                temp += (neg * 1)
            elif pVal == 2 or pVal == 8:
                temp += (neg * 5)
            elif pVal == 3 or pVal == 9:
                if (i == 3 or i == 4) and (j == 3 or j == 4):
                    temp += (neg * .4)
                temp += (neg * 3)
            elif pVal == 4 or pVal == 10:
                if (i == 3 or i == 4) and (j == 3 or j == 4):
                    temp += (neg * .2)
                temp += (neg * 3)
            elif pVal == 5 or pVal == 11:
                temp += (neg * 9)
            elif pVal == 6 or pVal == 12:
                temp += (neg * 1000)
    return temp


def getPiecesAval(arr, player):
    piecesAval = []

    for i in range(0, 8):
        for j in range(0, 8):
            if player == 1 and arr[i][j] >= 7:
                piecesAval.append(Piece(i, j, arr[i][j]))
            elif player == -1 and arr[i][j] < 7:
                piecesAval.append(Piece(i, j, arr[i][j]))
    return piecesAval


def movePiece(arr, p, newx, newy):

    arr[newx][newy] = p.getP()
    arr[p.getX()][p.getY()] = 0


def dispMoves(avalMoves, w):
    for x in range(0, len(avalMoves)):
        posX = avalMoves[x].getX()
        posY = avalMoves[x].getY()

        c = Rectangle(Point(boxLength * posX + offset + offsetInner, boxLength * posY + offset + offsetInner),
                      Point(boxLength * (posX + 1) + offset - offsetInner, boxLength * (posY + 1) + offset - offsetInner))
        c.draw(w)
        drawnMoves.append(c)

    if len(avalMoves) != 0:
        return 1
    return 0


def getMoves(arr, piece):
    avalMoves = []

    i = piece.getX()
    j = piece.getY()
    pVal = piece.getP()

    neg = 1
    flip = 1
    flip2 = 1
    pawnStart = 2
    if pVal <= 6:
        neg = -1
        if j == 6:
            pawnStart = 3
    else:
        if j == 1:
            pawnStart = 3


    # PAWN

    if pVal == 1 or pVal == 7:
        # print("yoy")
        for k in range(1, pawnStart):
            if (k * neg) + j > 7 or (k * neg) + j < 0:
                break
            if arr[i][j + (k * neg)] == 0:
                avalMoves.append(Point(i, j + (k * neg)))
            else:
                break

        for x in range(0, 2):
            if x == 0:
                flip = 1
            else:
                flip = -1

            if (1 * neg) + j > 7 or (1 * neg) + j < 0 or (1 * flip) + i > 7 or (1 * flip) + i < 0:
                break
            pColor = getColor(arr, i + (1 * flip), j + (1 * neg))
            if neg != pColor and pColor != 0:
                avalMoves.append(Point(i + (1 * flip), j + (1 * neg)))


    # ROOK

    elif pVal == 2 or pVal == 8:
        for x in range(0, 2):
            for k in range(1, 8):
                if x == 0:
                    flip = 1
                else:
                    flip = -1

                if (k * flip) + j > 7 or (k * flip) + j < 0:
                    break
                if arr[i][j + (k * flip)] == 0:
                    avalMoves.append(Point(i, j + (k * flip)))
                else:
                    pColor = getColor(arr, i, j + (k * flip))
                    if neg != pColor:
                        avalMoves.append(Point(i, j + (k * flip)))
                    break

        for x in range(0, 2):
            for k in range(1, 8):
                if x == 0:
                    flip = 1
                else:
                    flip = -1

                if (k * flip) + i > 7 or (k * flip) + i < 0:
                    break
                if arr[i + (k * flip)][j] == 0:
                    avalMoves.append(Point(i + (k * flip), j))
                else:
                    pColor = getColor(arr, i + (k * flip), j)
                    if neg != pColor:
                        avalMoves.append(Point(i + (k * flip), j))
                    break

    # KNIGHT

    elif pVal == 3 or pVal == 9:
        for x in range(0, 2):
            for k in range(0, 2):
                if x == 0:
                    flip = 1
                else:
                    flip = -1

                if k == 0:
                    flip2 = 1
                else:
                    flip2 = -1

                if not ((2 * flip) + j > 7 or (2 * flip) + j < 0 or (1 * flip2) + i > 7 or (1 * flip2) + i < 0):
                    if arr[i + (1 * flip2)][j + (2 * flip)] == 0:
                        avalMoves.append(Point(i + (1 * flip2), j + (2 * flip)))
                    else:
                        pColor = getColor(arr, i + (1 * flip2), j + (2 * flip))
                        if neg != pColor:
                            avalMoves.append(Point(i + (1 * flip2), j + (2 * flip)))

        for x in range(0, 2):
            for k in range(0, 2):
                if x == 0:
                    flip = 1
                else:
                    flip = -1

                if k == 0:
                    flip2 = 1
                else:
                    flip2 = -1

                if not ((1 * flip) + j > 7 or (1 * flip) + j < 0 or (2 * flip2) + i > 7 or (2 * flip2) + i < 0):
                    if arr[i + (2 * flip2)][j + (1 * flip)] == 0:
                        avalMoves.append(Point(i + (2 * flip2), j + (1 * flip)))
                    else:
                        pColor = getColor(arr, i + (2 * flip2), j + (1 * flip))
                        if neg != pColor:
                            avalMoves.append(Point(i + (2 * flip2), j + (1 * flip)))


    # BISHOP

    elif pVal == 4 or pVal == 10:
        for x in range(0, 2):
            for k in range(0, 2):
                for h in range(1, 7):
                    if x == 0:
                        flip = 1
                    else:
                        flip = -1

                    if k == 0:
                        flip2 = 1
                    else:
                        flip2 = -1

                    if (h * flip) + j > 7 or (h * flip) + j < 0 or (h * flip2) + i > 7 or (h * flip2) + i < 0:
                        break
                    if arr[i + (h * flip2)][j + (h * flip)] == 0:
                        avalMoves.append(Point(i + (h * flip2), j + (h * flip)))
                    else:
                        pColor = getColor(arr, i + (h * flip2), j + (h * flip))
                        if neg != pColor:
                            avalMoves.append(Point(i + (h * flip2), j + (h * flip)))
                        break

    # QUEEN

    elif pVal == 5 or pVal == 11:
        for x in range(0, 2):
            for k in range(0, 2):
                for h in range(1, 7):
                    if x == 0:
                        flip = 1
                    else:
                        flip = -1

                    if k == 0:
                        flip2 = 1
                    else:
                        flip2 = -1

                    if (h * flip) + j > 7 or (h * flip) + j < 0 or (h * flip2) + i > 7 or (h * flip2) + i < 0:
                        break
                    if arr[i + (h * flip2)][j + (h * flip)] == 0:
                        avalMoves.append(Point(i + (h * flip2), j + (h * flip)))
                    else:
                        pColor = getColor(arr, i + (h * flip2), j + (h * flip))
                        if neg != pColor:
                            avalMoves.append(Point(i + (h * flip2), j + (h * flip)))
                        break
        for x in range(0, 2):
            for k in range(1, 8):
                if x == 0:
                    flip = 1
                else:
                    flip = -1

                if (k * flip) + j > 7 or (k * flip) + j < 0:
                    break
                if arr[i][j + (k * flip)] == 0:
                    avalMoves.append(Point(i, j + (k * flip)))
                else:
                    pColor = getColor(arr, i, j + (k * flip))
                    if neg != pColor:
                        avalMoves.append(Point(i, j + (k * flip)))
                    break

        for x in range(0, 2):
            for k in range(1, 8):
                if x == 0:
                    flip = 1
                else:
                    flip = -1

                if (k * flip) + i > 7 or (k * flip) + i < 0:
                    break
                if arr[i + (k * flip)][j] == 0:
                    avalMoves.append(Point(i + (k * flip), j))
                else:
                    pColor = getColor(arr, i + (k * flip), j)
                    if neg != pColor:
                        avalMoves.append(Point(i + (k * flip), j))
                    break

    # KING

    elif pVal == 6 or pVal == 12:
        for x in range(0, 2):
            if x == 0:
                flip = 1
            else:
                flip = -1

            if (1 * flip) + j > 7 or (1 * flip) + j < 0:
                continue
            if arr[i][j + (1 * flip)] == 0:
                avalMoves.append(Point(i, j + (1 * flip)))
            else:
                pColor = getColor(arr, i, j + (1 * flip))
                if neg != pColor:
                    avalMoves.append(Point(i, j + (1 * flip)))
                continue

        for x in range(0, 2):
            if x == 0:
                flip = 1
            else:
                flip = -1

            if (1 * flip) + i > 7 or (1 * flip) + i < 0:
                continue
            if arr[i + (1 * flip)][j] == 0:
                avalMoves.append(Point(i + (1 * flip), j))
            else:
                pColor = getColor(arr, i + (1 * flip), j)
                if neg != pColor:
                    avalMoves.append(Point(i + (1 * flip), j))

        for x in range(0, 2):
            for k in range(0, 2):
                if x == 0:
                    flip = 1
                else:
                    flip = -1

                if k == 0:
                    flip2 = 1
                else:
                    flip2 = -1

                if (1 * flip2) + i > 7 or (1 * flip2) + i < 0 or (1 * flip) + j > 7 or (1 * flip) + j < 0:
                    continue
                if arr[i + (1 * flip2)][j + (1 * flip)] == 0:
                    avalMoves.append(Point(i + (1 * flip2), j + (1 * flip)))
                else:
                    pColor = getColor(arr, i + (1 * flip2), j + (1 * flip))
                    if neg != pColor:
                        avalMoves.append(Point(i + (1 * flip2), j + (1 * flip)))

    return avalMoves


def getSafeMoves(arr, player):
    piecesAval = getPiecesAval(pieceArr, player)
    avalMoves = []

    for k in piecesAval:
        avalMovesBeforeCheck = getMoves(pieceArr, k)
        for g in avalMovesBeforeCheck:
            if checkThreat(pieceArr, k, g.getX(), g.getY(), player) != 1:
                avalMoves.append(Move(k, g.getX(), g.getY()))
    return avalMoves


def getSafeMovesPiece(arr, piece, player):
    avalMoves = []

    avalMovesBeforeCheck = getMoves(pieceArr, piece)
    for g in avalMovesBeforeCheck:
        if checkThreat(pieceArr, piece, g.getX(), g.getY(), player) != 1:
            avalMoves.append(Move(piece, g.getX(), g.getY()))
    return avalMoves


def checkThreat(arr, p, i, j, player):
    oneMoveArr = copy.deepcopy(arr)
    movePiece(oneMoveArr, p, i, j)

    check = checkCheck(oneMoveArr, player)
    return check


def checkCheck(arr, player):
    avalMoves = []
    king = 6
    tempx = 0
    tempy = 0

    if player == 1:
        king = 12

    for a in range(0, 8):
        for b in range(0, 8):
            if arr[a][b] == king:
                tempx = a
                tempy = b
                break
        else:
            continue
        break

    piece = Piece(tempx, tempy, king)

    i = piece.getX()
    j = piece.getY()
    pVal = piece.getP()

    neg = 1
    flip = 1
    flip2 = 1
    pawnStart = 2
    if pVal <= 6:
        neg = -1
        if j == 6:
            pawnStart = 3
    else:
        if j == 1:
            pawnStart = 3


    # CHECKING DIAGONALLY FIRST

    for x in range(0, 2):
        for k in range(0, 2):
            for h in range(1, 7):
                if x == 0:
                    flip = 1
                else:
                    flip = -1

                if k == 0:
                    flip2 = 1
                else:
                    flip2 = -1

                if (h * flip) + j > 7 or (h * flip) + j < 0 or (h * flip2) + i > 7 or (h * flip2) + i < 0:
                    break

                searchPiece = arr[i + (h * flip2)][j + (h * flip)]

                if searchPiece == 0:
                    continue

                pColor = getColor(arr, i + (h * flip2), j + (h * flip))

                if pColor == player:
                    break

                if searchPiece == 4 or searchPiece == 5 or searchPiece == 10 or searchPiece == 11:
                    return 1
                if (searchPiece == 1 or searchPiece == 7 or searchPiece == 6 or searchPiece == 12) and flip == neg and h == 1:
                    return 1

    # CHECKING STRAIGHT NEXT

    for x in range(0, 2):
        for k in range(1, 8):
            if x == 0:
                flip = 1
            else:
                flip = -1

            if (k * flip) + j > 7 or (k * flip) + j < 0:
                break


            searchPiece = arr[i][j + (k * flip)]

            if searchPiece == 0:
                continue

            pColor = getColor(arr, i, j + (k * flip))

            if pColor == player:
                break

            if searchPiece == 2 or searchPiece == 5 or searchPiece == 8 or searchPiece == 11:
                return 1
            elif (searchPiece == 6 or searchPiece == 12) and flip == neg and h == 1:
                return 1
            else:
                break

    for x in range(0, 2):
        for k in range(1, 8):
            if x == 0:
                flip = 1
            else:
                flip = -1

            if (k * flip) + i > 7 or (k * flip) + i < 0:
                break

            searchPiece = arr[i + (k * flip)][j]

            if searchPiece == 0:
                continue

            pColor = getColor(arr, i + (k * flip), j)

            if pColor == player:
                break

            if searchPiece == 2 or searchPiece == 5 or searchPiece == 8 or searchPiece == 11:
                return 1
            elif (searchPiece == 6 or searchPiece == 12) and flip == neg and k == 1:
                return 1
            else:
                break



    # SIGH KNIGHTS

    for x in range(0, 2):
        for k in range(0, 2):
            if x == 0:
                flip = 1
            else:
                flip = -1

            if k == 0:
                flip2 = 1
            else:
                flip2 = -1

            if not ((2 * flip) + j > 7 or (2 * flip) + j < 0 or (1 * flip2) + i > 7 or (1 * flip2) + i < 0):

                searchPiece = arr[i + (1 * flip2)][j + (2 * flip)]

                if searchPiece == 0:
                    continue
                pColor = getColor(arr, i + (1 * flip2), j + (2 * flip))

                if pColor == player:
                    break

                if searchPiece == 3 or searchPiece == 9:
                    return 1

    for x in range(0, 2):
        for k in range(0, 2):
            if x == 0:
                flip = 1
            else:
                flip = -1

            if k == 0:
                flip2 = 1
            else:
                flip2 = -1

            if not ((1 * flip) + j > 7 or (1 * flip) + j < 0 or (2 * flip2) + i > 7 or (2 * flip2) + i < 0):

                searchPiece = arr[i + (2 * flip2)][j + (1 * flip)]

                if searchPiece == 0:
                    continue
                pColor = getColor(arr, i + (2 * flip2), j + (1 * flip))

                if pColor == player:
                    break

                if searchPiece == 3 or searchPiece == 9:
                    return 1


                if arr[i + (2 * flip2)][j + (1 * flip)] == 0:
                    avalMoves.append(Point(i + (2 * flip2), j + (1 * flip)))
                else:
                    pColor = getColor(arr, i + (2 * flip2), j + (1 * flip))
                    if neg != pColor:
                        avalMoves.append(Point(i + (2 * flip2), j + (1 * flip)))

    return 0


def getColor(arr, i, j):
    piece = arr[i][j]
    if piece == 0:
        return 0
    elif piece < 7:
        return -1
    elif piece > 6:
        return 1


def delDispMoves():
    for i in drawnMoves:
        i.undraw()
        del i


def clearBoard():
    for i in pieceObjs:
        i.undraw()
        del i


def renderPieces(w, arr):
    for i in range(0, 8):
        for j in range(0, 8):
            piece = arr[i][j]

            filename = ''
            filename2 = ''

            if piece != 0:
                newPiece = Text(Point(boxLength * i + offset + (boxLength / 2),
                                      boxLength * j + offset + (boxLength / 2)), "NOT")
                if piece == 1 or piece == 7:
                    newPiece.setText("p")
                    filename = "pawn"
                if piece == 2 or piece == 8:
                    newPiece.setText("r")
                    filename = "rook"
                if piece == 3 or piece == 9:
                    newPiece.setText("n")
                    filename = "knight"
                if piece == 4 or piece == 10:
                    newPiece.setText("b")
                    filename = "bishop"
                if piece == 5 or piece == 11:
                    newPiece.setText("q")
                    filename = "queen"
                if piece == 6 or piece == 12:
                    newPiece.setText("k")
                    filename = "king"

                if piece < 7:
                    newPiece.setTextColor("white")
                    filename2 = "./pieces/" + "w" + filename + ".png"
                else:
                    newPiece.setTextColor("black")
                    filename2 = "./pieces/" + "b" + filename + ".png"

                if images == 1:
                    realImage = Image(Point(boxLength * i + offset + (boxLength / 2),
                                        boxLength * j + offset + (boxLength / 2)), filename2)
                    realImage.draw(w)
                    pieceObjs.append(realImage)
                else:
                    newPiece.draw(w)
                    pieceObjs.append(newPiece)


def startPos(i, j):
    if j == 1:
        return 7

    if j == 6:
        return 1

    if j == 0:
        if i == 0 or i == 7:
            return 8
        if i == 1 or i == 6:
            return 9
        if i == 2 or i == 5:
            return 10
        if i == 3:
            return 11
        if i == 4:
            return 12
    if j == 7:
        if i == 0 or i == 7:
            return 2
        if i == 1 or i == 6:
            return 3
        if i == 2 or i == 5:
            return 4
        if i == 3:
            return 5
        if i == 4:
            return 6

    return 0


def getPiece(i, j):
    return pieceArr[i][j]




class Piece():
    def __init__(self, x, y, p):
        self.x = x
        self.y = y
        self.p = p

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def getP(self):
        return self.p

    def getInfo(self):
        return "I am piece: " + str(self.p) + ", located at: " + str(self.x) + ", " + str(self.y)





class Move():
    def __init__(self, p, x, y):
        self.p = p
        self.x = x
        self.y = y

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def getPiece(self):
        return self.p

    def getInfo(self):
        return "I am a move: " + str(self.p.getInfo()) + ", moving to: " + str(self.x), ", " + str(self.y)



if __name__ == '__main__':
    main()