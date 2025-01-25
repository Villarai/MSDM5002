import numpy as np
import os
import time
import pygame as pg

from blphago.utils.api5002 import check_winner, computer_move

os.environ['SDL_VIDEO_WINDOW_POS']="%d,%d"%(20,80)


####################################################################################################################
# create the initial empty chess board in the game window
def draw_board():
    global center, sep_r, sep_th, piece_radius

    center=w_size/2
    sep_r=int((center-pad)/(radial_span-1))  # separation between circles
    sep_th=2*np.pi/angular_span  # separation between radial lines
    piece_radius=sep_r/2*sep_th*0.8  # size of a chess piece

    surface=pg.display.set_mode((w_size,w_size))
    pg.display.set_caption("Gomuku (a.k.a Five-in-a-Row)")

    color_line=[153,153,153]
    color_board=[241,196,15]

    surface.fill(color_board)

    for i in range(1,radial_span):
        pg.draw.circle(surface,color_line,(center,center),sep_r*i,3)

    for i in range(angular_span//2):
        pg.draw.line(surface,color_line,(center+(center-pad)*np.cos(sep_th*i),center+(center-pad)*np.sin(sep_th*i)),
                     (center-(center-pad)*np.cos(sep_th*i),center-(center-pad)*np.sin(sep_th*i)),3)

    pg.display.update()

    return surface


####################################################################################################################
# translate clicking position on the window to array indices (th, r)
# pos = (x,y) is a tuple returned by pygame, telling where an event (i.e. player click) occurs on the game window
def click2index(pos):
    dist=np.sqrt((pos[0]-center)**2+(pos[1]-center)**2)
    if dist<w_size/2-pad+0.25*sep_r:  # check if the clicked position is on the circle

        # return corresponding indices (th,r) on the rectangular grid
        return (round(np.arctan2((pos[1]-center),(pos[0]-center))/sep_th),round(dist/sep_r))

    return False  # return False if the clicked position is outside the circle


####################################################################################################################
# Draw the stones on the board at pos = [th, r]
# r and th are the indices on the 16x10 board array (under rectangular grid representation)
# Draw a black circle at pos if color = 1, and white circle at pos if color =  -1

def draw_stone(surface,pos,color=0):
    color_black=[0,0,0]
    color_dark_gray=[75,75,75]
    color_white=[255,255,255]
    color_light_gray=[235,235,235]

    # translate (th, r) indices to xy coordinate on the game window
    x=center+pos[1]*sep_r*np.cos(pos[0]*sep_th)
    y=center+pos[1]*sep_r*np.sin(pos[0]*sep_th)

    if color==1:
        pg.draw.circle(surface,color_black,[x,y],piece_radius*(1+2*pos[1]/radial_span),0)
        pg.draw.circle(surface,color_dark_gray,[x,y],piece_radius*(1+2*pos[1]/radial_span),2)

    elif color==-1:
        pg.draw.circle(surface,color_white,[x,y],piece_radius*(1+2*pos[1]/radial_span),0)
        pg.draw.circle(surface,color_light_gray,[x,y],piece_radius*(1+2*pos[1]/radial_span),2)

    pg.display.update()


####################################################################################################################
def print_winner(surface,winner=0):
    if winner==2:
        msg="Draw! So White wins"
        color=[153,153,153]
    elif winner==1:
        msg="Black wins!"
        color=[0,0,0]
    elif winner==-1:
        msg='White wins!'
        color=[255,255,255]
    else:
        return

    font=pg.font.Font('freesansbold.ttf',32)
    text=font.render(msg,True,color)
    textRect=text.get_rect()
    textRect.topleft=(0,0)
    surface.blit(text,textRect)
    pg.display.update()


def main(player_is_black=True):
    global w_size,pad,radial_span,angular_span
    w_size=720  # window size
    pad=36  # padding size
    radial_span=10
    angular_span=16

    pg.init()
    surface=draw_board()

    board=np.zeros((angular_span,radial_span),dtype=int)
    running=True
    gameover=False


    while running:

        ####################################################################################################
        ######################## Normally your edit should be within the while loop ########################
        ####################################################################################################

        for event in pg.event.get():  # A for loop to process all the events initialized by the player

            # detect if player closes the game window
            if event.type==pg.QUIT:
                running=False

            # detect whether the player is clicking in the window
            # should lock the window after gameover
            if event.type==pg.MOUSEBUTTONDOWN and not gameover:

                idx=click2index(event.pos)  # translate clicking position to indices on board matrix idx = (th, r)

                if idx and board[idx]==0:  # update the board matrix if that position has not been occupied
                    print(f"people: {idx}")

                    color=1 if player_is_black else -1
                    if idx[1]==0:  # (0,0) is a special case
                        board[:,0]=color
                        draw_stone(surface,(0,0),color)
                    else:
                        board[idx]=color
                        draw_stone(surface,idx,color)

                    # JQZ: in this "if", check win/loss.
                    # print(f"board:\n{board}")
                    winner = check_winner(board, display=True)
                    print_winner(surface, winner)
                    # winner_q = test_quick_check(idx, color)
                    # assert winner_q==winner, f"please debug quick_check, \nwinner={winner}\nwinner_q={winner_q}"

                    # # JQZ: if game not over, next player will use another color
                    # if winner==0:
                    #     player_is_black = not player_is_black
                    # else:
                    #     gameover = True

                    # JQZ developing: ai move
                    # BasicPlayer: ai making random moves
                    if winner == 0:
                        color= -1 if player_is_black else 1
                        idx = computer_move(board, color)
                        if board[idx]==0:

                            if idx[1]==0:  # (0,0) is a special case
                                board[:,0]=color
                                draw_stone(surface,(0,0),color)
                            else:
                                board[idx]=color
                                draw_stone(surface,idx,color)

                            # board[idx]=-1
                            # draw_stone(surface,idx,color)
                            # gameover=check_winner(board)
                            # if gameover:
                            #     print_winner(surface,gameover)
                            #     print(board)
                        else:
                            print("This position is already occupied. Therefore your turn is skipped.")

                        winner = check_winner(board, display=True)
                        print_winner(surface,winner)
                        # winner_q = test_quick_check(idx, color)
                        # assert winner_q==winner, f"please debug quick_check"

                    if winner != 0:
                        gameover = True



        ####################################################################################################
        ######################## Normally Your edit should be within the while loop ########################
        ####################################################################################################

    pg.quit()

def main_pvp(player_is_black=True):
    global w_size,pad,radial_span,angular_span
    w_size=720  # window size
    pad=36  # padding size
    radial_span=10
    angular_span=16

    pg.init()
    surface=draw_board()

    board=np.zeros((angular_span,radial_span),dtype=int)
    running=True
    gameover=False


    while running:

        ####################################################################################################
        ######################## Normally your edit should be within the while loop ########################
        ####################################################################################################

        for event in pg.event.get():  # A for loop to process all the events initialized by the player

            # detect if player closes the game window
            if event.type==pg.QUIT:
                running=False

            # detect whether the player is clicking in the window
            # should lock the window after gameover
            if event.type==pg.MOUSEBUTTONDOWN and not gameover:

                idx=click2index(event.pos)  # translate clicking position to indices on board matrix idx = (th, r)

                if idx and board[idx]==0:  # update the board matrix if that position has not been occupied
                    color=1 if player_is_black else -1
                    if idx[1]==0:  # (0,0) is a special case
                        board[:,0]=color
                        draw_stone(surface,(0,0),color)
                    else:
                        board[idx]=color
                        draw_stone(surface,idx,color)

                    # JQZ: in this "if", check win/loss.
                    # print(f"board:\n{board}")
                    winner = check_winner(board, display=True)
                    print_winner(surface, winner)
                    # winner_q = test_quick_check(idx, color)
                    #
                    # if winner_q==winner:
                    #     pass
                    # else:
                    #     print(f"winner = {winner}")
                    #     print(f"winner_q = {winner_q}")
                    # # assert winner_q==winner, f"please debug quick_check"

                    # JQZ: if game not over, next player will use another color
                    if winner==0:
                        player_is_black = not player_is_black
                    else:
                        gameover = True




        ####################################################################################################
        ######################## Normally Your edit should be within the while loop ########################
        ####################################################################################################

    pg.quit()

if __name__=='__main__':
    # main(True)
    main_pvp(True)


































