# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 22:18:10 2020

@author: WIKI
"""
import pygame, sys, random
from pygame.locals import *
from copy import copy, deepcopy


class MINIMAX():
    def __init__(self):
        self.grid=[]
        self.dx=[1,1,-1,-1]
        self.dy=[1,-1,1,-1]
        self.MAX_DEPTH=5

    def init_grid(self,board):
        self.grid=[]
        for i in range (8):
            self.grid.append([])
            for j in range(8):
                self.grid[i].append('e')
        for piece in board.pieces:
            y = int((piece.x-10)//board.BOXWIDTH)
            x = int((piece.y-10)//board.BOXHEIGHT)
            self.grid[x][y] = piece.color[0]
            if piece.king:
                self.grid[x][y] = self.grid[x][y].upper()

    def inverse_player(self,player):
        if (player == 'w'):
            return 'b'
        else:
            return 'w'

    def valid(self,x,y):
        return x>=0 and x<8 and y>=0 and y<8

    def empty(self,x,y):
        return self.valid(x,y) and self.grid[x][y]=='e'

    def valid_piece(self,x,y):
        return self.valid(x,y) and self.grid[x][y]!='e'

    def opposite_pieces(self,x,y,xx,yy):
        return self.valid_piece(x,y) and self.valid_piece(xx,yy) and self.grid[x][y].upper() != self.grid[xx][yy].upper()

    def can_eat(self,from_x,from_y,between_x,between_y):
        to_x = from_x + 2 * (between_x - from_x)
        to_y = from_y + 2 * (between_y - from_y)
        return self.opposite_pieces(from_x,from_y,between_x,between_y) and self.empty(to_x,to_y)

    def make_move(self,from_x,from_y,to_x,to_y):
        if (abs(to_x-from_x)!=1):
            between_x = from_x + (to_x - from_x) // 2
            between_y = from_y + (to_y - from_y) // 2
            self.grid[to_x][to_y] = self.grid[from_x][from_y]
            self.grid[between_x][between_y] = 'e'
            self.grid[from_x][from_y]       = 'e'
        else: 
            self.grid[from_x][from_y],self.grid[to_x][to_y] = self.grid[to_x][to_y],self.grid[from_x][from_y]

    def eat(self,from_x,from_y,between_x,between_y,sequence,possible_moves):
        to_x = from_x + (between_x - from_x) * 2
        to_y = from_y + (between_y - from_y) * 2
            
        eaten_piece = self.grid[between_x][between_y]
        
        self.make_move(from_x,from_y,to_x,to_y)

        if (len(sequence) == 0):
            sequence.append((from_x,from_y))
        sequence.append((to_x,to_y))
        
        self.get_eat_moves(to_x,to_y,sequence,possible_moves)

        if (len(sequence) == 2):
            sequence.pop()
        sequence.pop()
        
        self.make_move(to_x,to_y,from_x,from_y)
        self.grid[between_x][between_y] = eaten_piece
            
    
    def get_eat_moves(self,from_x,from_y,sequence,possible_moves):
        # 0 -> 3 King moves
        s , e = 0 , 4
        # 2 -> 3 White moves
        if   self.grid[from_x][from_y]  == 'w':
            s=2
        # 0 -> 1 Black moves
        elif self.grid[from_x][from_y]  == 'b':
            e=2
        cannot_eat=True

        for d in range(s,e):
            to_x = from_x + self.dx[d]
            to_y = from_y + self.dy[d]
            if self.can_eat(from_x,from_y,to_x,to_y):
                cannot_eat=False
                self.eat(from_x,from_y,to_x,to_y,sequence,possible_moves)
        
        if (cannot_eat) and (len(sequence)!=0):
            possible_moves.append(list(sequence))

    def get_piece_moves(self,from_x,from_y):
        possible_moves=[]

        self.get_eat_moves(from_x,from_y,[],possible_moves)
        if len(possible_moves)!=0:
            return True,possible_moves

        s , e = 0 , 4
        if   self.grid[from_x][from_y] == 'w':
            s=2
        elif self.grid[from_x][from_y] == 'b':
            e=2
        
        for d in range(s,e):
            to_x = from_x + self.dx[d]
            to_y = from_y + self.dy[d]
            if self.empty(to_x,to_y):
                possible_moves.append([(from_x,from_y),(to_x,to_y)])

        return False,possible_moves

    def make_moves(self,moves,eaten_pieces):
        eaten = len(eaten_pieces)!=0
            
        for i in range(1,len(moves)):
            from_x,from_y = moves[i-1]
            to_x  ,  to_y = moves[i]
            between_x = from_x + (to_x - from_x) // 2
            between_y = from_y + (to_y - from_y) // 2
            if abs(to_x-from_x)==2:
                eaten_pieces.append(self.grid[between_x][between_y])
            else:
                eaten_pieces.append('e')
            self.make_move(from_x,from_y,to_x,to_y)
            if eaten and eaten_pieces[i-1]!='e':
                self.grid[between_x][between_y] = eaten_pieces[i-1]

        moves.reverse()
        eaten_pieces.reverse()

    def check_king(self,player,x,y):
        if (self.grid[x][y] ==  'w' and x == 0) or (self.grid[x][y] == 'b' and x == 7):
            self.grid[x][y] = player.upper()
            return True
        return False
        

    def get_move_score(self,player,depth,move,alpha,beta):
        eaten_pieces = []

        self.make_moves(move,eaten_pieces)
        x,y = move[0]
        
        king = self.check_king(player,x,y)
 
        score = self.search_best_move(self.inverse_player(player),depth+1,alpha,beta)[1]
                    
        if king:
            self.grid[x][y] = player

        self.make_moves(move,eaten_pieces)
        
        return score
        
            
    def get_possible_moves(self,player):
        possible_moves = []
        has_to_eat = False
        for x in range(8):
            for y in range(8):
                if self.grid[x][y].upper() ==  player.upper():
                    can_eat,piece_moves = self.get_piece_moves(x,y)
                    if len(piece_moves) == 0:
                        continue
                    if can_eat:
                        if not has_to_eat:
                            possible_moves = []
                            has_to_eat = True
                        possible_moves.append(piece_moves)
                    elif not has_to_eat:
                        possible_moves.append(piece_moves)
        return possible_moves          
        
    def get_heuristic(self):
        h = 0
        for x in range (8):
            for y in range(8):
                if   self.grid[x][y] == 'w':
                    h+= 12 - x
                elif self.grid[x][y] == 'b':
                    h-=  5 + x
                elif self.grid[x][y] == 'W':
                    h+= 15
                elif self.grid[x][y] == 'B':
                    h-= 15
        return h

    def quiet_search(self,player):
        possible_moves = []
        for x in range(8):
            for y in range(8):
                if self.grid[x][y].upper() == player.upper():
                    self.get_eat_moves(x,y,[],possible_moves) 
        
        best_score = 10000
        if player == 'w':
            best_score*=-1
            
        eaten_pieces = []
        for move in possible_moves:
            self.make_moves(move,eaten_pieces)
            x,y = move[0]
            king = self.check_king(player,x,y)
            score = self.quiet_search(self.inverse_player(player))
            if king:
                self.grid[x][y] = player
            self.make_moves(move,eaten_pieces)
            if player == 'w':
                best_score = max(best_score,score)
            else:
                best_score = min(best_score,score)

        if len(possible_moves) == 0:
            best_score = self.get_heuristic()
        return best_score

    def search_best_move(self,player,depth,alpha,beta):
        if (depth > self.MAX_DEPTH):
            return [],self.quiet_search(player)
        
        possible_moves = self.get_possible_moves(player)        
        best_move = []
        best_score = alpha
        if player == 'b':
            best_score = beta

        prune_search = False
        
        for piece_moves in possible_moves:
            for move in piece_moves:
                if prune_search:
                    continue
                score = self.get_move_score(player,depth,move,alpha,beta)
                if   player == 'w' and score>=best_score:
                    if score>best_score:
                        best_move=[]
                    best_score = score
                    best_move.append(move)
                    if beta<=best_score:
                        prune_search = True
        
                elif player == 'b' and score<=best_score:
                    if score<best_score:
                        best_move=[]
                    best_score = score
                    best_move.append(move)
                    if best_score<=alpha:
                        prune_search = True

        chosen_move = []
        if depth == 1 :
            chosen_move = random.choice(best_move)
        return chosen_move,best_score

    def get_move(self,player,board):
        self.init_grid(board)
        return self.search_best_move(player,1,-10000,10000)

