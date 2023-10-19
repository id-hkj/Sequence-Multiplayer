import copy
import pygame
import os
from network import Network
import socket

pygame.init()
pygame.display.init()
pygame.font.init()


class GameScreen:

    def __init__(self, zr, win):
        self.ending = True
        self.name = ""
        self.card_remover = 0
        self.card_change_count = 1
        self.card_change_stage = 0
        self.card_x = []
        self.card_y = []
        self.player_names = {'r': "", 'g': "", 'b': ""}
        self.reply = 'ping'
        self.top_txt = 'Waiting for '
        self.turn = False
        self.go = False
        self.board = []
        self.n = None
        self.gameEnded = False
        self.zr = zr
        self.win = win
        self.scene = 'g'
        self.width = int(1025 // self.zr)
        self.card_select = 'xy'
        self.clicked = ''
        self.card_selected = False
        self.winCards = []
        self.highlighter = []
        self.detail = {'AI': 0, 'US': 0, 'GR': 0}
        self.sequence_no = {}
        self.winner = ''
        self.Font = pygame.font.Font(None, 40)
        self.mini_f = pygame.font.Font(None, 15)
        self.cards = ['HA', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'H8', 'H9', 'H1', 'HJ', 'HQ', 'HK',
                      'DA', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'D1', 'DJ', 'DQ', 'DK',
                      'CA', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C1', 'CJ', 'CQ', 'CK',
                      'SA', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'S9', 'S1', 'SJ', 'SQ', 'SK']
        # IMAGES
        self.BoardCards = pygame.image.load(os.path.join('Sequence!!!.png')).convert_alpha()
        self.USChip = pygame.image.load(os.path.join('Blue.png')).convert_alpha()
        self.AIChip = pygame.image.load(os.path.join('Red.png')).convert_alpha()
        self.GRChip = pygame.image.load(os.path.join('Green.png')).convert_alpha()
        self.USChip = pygame.transform.smoothscale(self.USChip, (int(50 // self.zr), int(50 // self.zr)))
        self.AIChip = pygame.transform.smoothscale(self.AIChip, (int(50 // self.zr), int(50 // self.zr)))
        self.GRChip = pygame.transform.smoothscale(self.GRChip, (int(50 // self.zr), int(50 // self.zr)))
        self.mini_USChip = pygame.transform.smoothscale(self.USChip, (int(15 // self.zr), int(15 // self.zr)))
        self.mini_AIChip = pygame.transform.smoothscale(self.AIChip, (int(15 // self.zr), int(15 // self.zr)))
        self.mini_GRChip = pygame.transform.smoothscale(self.GRChip, (int(15 // self.zr), int(15 // self.zr)))
        self.BoardCards = pygame.transform.smoothscale(self.BoardCards, (int(960 // self.zr), int(689 // self.zr)))
        self.cardIMGs = {}
        self.legend_prep = []
        self.data = None
        for cardNo in range(52):
            self.cardIMGs[str(self.cards[cardNo])] = pygame.image.load(
                os.path.join('Cards', str(self.cards[cardNo]) + '.png')).convert_alpha()
            self.cardIMGs[str(self.cards[cardNo])] = pygame.transform.smoothscale(
                self.cardIMGs[str(self.cards[cardNo])], (int(80 // self.zr), int(112 // self.zr)))

    def zoom(self, *args):
        return_tup = ()
        for el in args:
            return_tup += (int(el // self.zr),)
        return return_tup

    def connect(self, ip, name):
        try:
            self.scene = 'load'
            self.n = Network(ip)
            self.scene = 'g'
            self.data = self.n.get_dat()
            self.update_data()
            self.name = name
        except (socket.gaierror, TimeoutError):
            self.scene = 'invalidIP'

    def shift(self, grid):
        return [self.padding(r) + row + self.padding(len(row) - r - 1)
                for r, row in enumerate(grid)]

    @staticmethod
    def padding(No):
        return ['None' for _ in range(No)]

    @staticmethod
    def transpose(grid):
        return [list(tup) for tup in zip(*grid)]

    def is_five(self, gameBoard):
        self.sequence_no = {'US': 0, 'AI': 0}
        self.winCards = []
        names = ['US', 'AI']
        if self.player_names['g']:
            names.append('GR')
        check_boards = {1: gameBoard, 2: self.transpose(self.shift(gameBoard)), 3: self.transpose(gameBoard),
                        4: self.transpose(self.shift(reversed(gameBoard)))}
        # USER CHECK
        for name in names:
            state = []
            for index_count, board_test in check_boards.items():
                counter = 0
                for i in range(len(board_test)):
                    for j in range(len(board_test[i])):
                        if board_test[i][j][-2:] == name or board_test[i][j] == 'xx':
                            counter += 1
                            if counter >= 5:
                                self.sequence_no[name] = 1
                                if index_count == 1:
                                    state.append('01' + str(i) + str(j - 4))
                                elif index_count == 2:
                                    state.append('09' + str(j - 4) + str(i - j + 4))
                                elif index_count == 3:
                                    state.append('10' + str(j - 4) + str(i))
                                elif index_count == 4:
                                    state.append('11' + str(9 - j) + str(i - j))
                        else:
                            counter = 0
                    counter = 0
            if 'GR' in names and state:
                self.winCards = []
                for i in range(5):
                    self.winCards.append(str(int(state[0][2:]) + (i * int(state[0][:2]))))
                    if len(self.winCards[i]) == 1:
                        self.winCards[i] = '0' + self.winCards[i]
                self.winner = name
                return self.winner
            # WinCheck
            current_check = []
            for i in range(len(state)):
                win_add = []
                for j in range(5):
                    win_add.append(str(int(state[i][2:]) + (j * int(state[i][:2]))))
                current_check.append(win_add)
            self.highlighter = []
            for i in range(len(current_check)):
                for j in range(len(current_check) - i - 1):
                    same_count = 0
                    for k in current_check[i]:
                        if k in current_check[len(current_check) - j - 1]:
                            same_count += 1
                            if same_count > 1:
                                break
                    if same_count <= 1:
                        self.winner = name
                        for card in current_check[i]:
                            self.highlighter.append(card)
                        for card in current_check[len(current_check) - j - 1]:
                            self.highlighter.append(card)
                        break
                if self.highlighter:
                    break
            for el in current_check:
                for indexer in el:
                    self.winCards.append(indexer)
            if self.highlighter:
                break
        if self.winCards:
            for i in range(len(self.winCards)):
                if len(self.winCards[i]) == 1:
                    self.winCards[i] = '0' + str(self.winCards[i])
            for i in range(len(self.highlighter)):
                if len(self.highlighter[i]) == 1:
                    self.highlighter[i] = '0' + self.highlighter[i]
            return str(self.winner)
        else:
            return ''

    def draw_board(self, mouse: bool = False, highlight: str = 'xy') -> str:
        pos = pygame.mouse.get_pos()
        pygame.draw.rect(self.win, (255, 255, 255), self.zoom(34, 72, 967, 692), border_radius=5)
        pygame.draw.rect(self.win, (15, 112, 25), self.zoom(35, 73, 965, 690), border_radius=5)
        return_txt = ''
        for i in range(10):
            for j in range(10):
                if self.winCards:
                    if (str(i) + str(j) in self.highlighter) or (str(i) + str(j) in self.winCards):
                        pygame.draw.rect(self.win, (0, 0, 255),
                                         self.zoom(((43 + (j * 96)) - j // 5), ((81 + (i * 68)) - i // 2), 88, 65),
                                         border_radius=5)
                if self.board[i][j] == highlight:
                    pygame.draw.rect(self.win, (255, 255, 0),
                                     self.zoom(((43 + (j * 96)) - j // 5), ((81 + (i * 68)) - i // 2), 88, 65),
                                     border_radius=5)
                elif highlight[1] == 'J':
                    if highlight[0] == 'H' or 'S' == highlight[0]:
                        tester_board = copy.deepcopy(self.board)
                        tester_board[i][j] = tester_board[i][j][:2]
                        self.is_five(tester_board)
                        if (len(self.board[i][j]) == 4) and (self.sequence_no == self.detail):
                            pygame.draw.rect(self.win, (255, 255, 0),
                                             self.zoom(((43 + (j * 96)) - j // 5), ((81 + (i * 68)) - i // 2), 88, 65),
                                             border_radius=5)
                    elif not (self.board[i][j] == 'xx') and len(self.board[i][j]) == 2:
                        pygame.draw.rect(self.win, (255, 255, 0),
                                         self.zoom(((43 + (j * 96)) - j // 5), ((81 + (i * 68)) - i // 2), 88, 65),
                                         border_radius=5)
                card = pygame.Rect(self.zoom((45 + (j * 96)), (83 + (i * 68)), 84, 61))
                if mouse and card.collidepoint(pos):
                    return_txt = 'CARD' + str(i) + str(j)
        self.win.blit(self.BoardCards, self.zoom(37, 72))
        for i in range(10):
            for j in range(10):
                if self.board[i][j][-2:] == 'US':
                    pygame.draw.circle(self.win, (0, 0, 0), self.zoom((87 + (j * 96)), (110 + (i * 68))),
                                       int(27 // self.zr))
                    self.win.blit(self.USChip, self.zoom((62 + (j * 96)), (85 + (i * 68))))
                elif self.board[i][j][-2:] == 'AI':
                    pygame.draw.circle(self.win, (0, 0, 0), self.zoom((87 + (j * 96)), (110 + (i * 68))),
                                       int(27 // self.zr))
                    self.win.blit(self.AIChip, self.zoom((62 + (j * 96)), (85 + (i * 68))))
                elif self.board[i][j][-2:] == 'GR':
                    pygame.draw.circle(self.win, (0, 0, 0), self.zoom((87 + (j * 96)), (110 + (i * 68))),
                                       int(27 // self.zr))
                    self.win.blit(self.GRChip, self.zoom((62 + (j * 96)), (85 + (i * 68))))
        return return_txt

    def draw_cards(self) -> str:
        pos = pygame.mouse.get_pos()
        return_txt = ''
        for i in range(len(self.cards)):
            if self.cards[i] == 'NO':
                break
            if self.cards[i] == self.card_select:
                pygame.draw.rect(self.win, (255, 255, 0), self.zoom(self.card_x[i] - 2, self.card_y[i] - 2,
                                                                    84, 116), border_radius=5)
            card = pygame.Rect(self.zoom(self.card_x[i], self.card_y[i], 80, 112))
            self.win.blit(self.cardIMGs[str(self.cards[i])], self.zoom(self.card_x[i], self.card_y[i]))
            if self.go and card.collidepoint(pos):
                return_txt = 'USER' + str(i)
        return return_txt

    def main(self, hand_cards: list):
        if len(self.clicked) == 5 and self.clicked[:4] == 'USER':
            card_clicked = hand_cards[int(self.clicked[4])]
            self.card_selected = True
            self.reply = 'ping'
            return card_clicked
        elif len(self.clicked) == 6 and self.clicked[:4] == 'CARD' and self.card_selected:
            card_clicked = self.board[int(self.clicked[4])][int(self.clicked[5])]
            if not (self.card_select[1] == 'J'):
                if card_clicked == self.card_select:
                    self.reply = str(int(self.clicked[4])) + str(int(self.clicked[5]))
                else:
                    self.reply = 'ping'
                    return self.card_select
            elif (self.card_select[0] == 'H') or (self.card_select[0] == 'S'):
                tester_board = self.board
                tester_board[int(self.clicked[4])][int(self.clicked[5])] = tester_board[int(self.clicked[4])][
                                                                               int(self.clicked[5])][:2]
                self.is_five(tester_board)
                if (len(card_clicked) == 4) and (self.sequence_no == self.detail):
                    self.reply = str(int(self.clicked[4])) + str(int(self.clicked[5]))
                else:
                    self.reply = 'ping'
                    return self.card_select
            else:
                if not ((len(card_clicked) == 4) or card_clicked == 'xx'):
                    self.reply = str(int(self.clicked[4])) + str(int(self.clicked[5]))
                else:
                    self.reply = 'ping'
                    return self.card_select
            self.reply += str(self.card_select)
            self.card_selected = False
            return 'xy'
        self.reply = 'ping'
        return self.card_select

    def update_data(self):
        data0 = self.data.split('abc!')
        if len(data0) > 1:
            self.board = []
            render = data0[0].split(' ')
            for i in range(10):
                mini_board = []
                for j in range(10):
                    mini_board.append(render[0])
                    del render[0]
                self.board.append(mini_board)
            self.turn = True if data0[1] == '0' else False
            if self.card_change_stage != 1:
                self.cards = data0[2].split(' ')
            self.top_txt = data0[3]
            self.reply = ''
        elif not self.player_names['r']:
            data0 = self.data.split('aaBaa')
            if data0[-1] == '3':
                self.player_names['b'] = ', '.join(data0[:-1][0::3])
                self.player_names['r'] = ', '.join(data0[:-1][1::3])
                self.player_names['g'] = ', '.join(data0[:-1][2::3])
            elif data0[-1] == '2':
                self.player_names['b'] = ', '.join(data0[:-1][0::2])
                self.player_names['r'] = ', '.join(data0[:-1][1::2])
            for key in self.player_names:
                if self.name in self.player_names[key]:
                    split = self.player_names[key].split(self.name)
                    self.player_names[key] = 'YOU'.join(split)
                    self.name = self.name.upper() + '\'S TURN'
                    break
            self.prepare_legend()
            self.top_txt = ''

    def top_text(self, text):
        text = self.Font.render(text, True, (255, 255, 255))
        x_val = int(self.width // 2 - text.get_width() // 2)
        self.win.blit(text, (x_val, int(25 // self.zr)))

    def card_positions(self):
        card_len = len(self.cards)
        if self.card_change_stage == 0:
            start = 550 - (int(card_len % 2) * 50) - (int(card_len / 2) * 100)
            self.card_x = [start + (i * 100) for i in range(card_len)]
            self.card_y = [770 for _ in range(card_len)]
        elif self.card_change_stage == 1:
            start = 550 - (int(card_len % 2) * 50) - (int(card_len / 2) * 100)
            self.card_x = [start + (i * 100) for i in range(card_len)]
            self.card_y = [770 for _ in range(card_len)]
            self.card_y[self.card_remover] = int(770 + (self.card_change_count * 8.667))
            self.card_change_count += 1
            if self.card_change_count == 15:
                self.card_change_count = 1
                self.card_change_stage = 2
        elif self.card_change_stage == 2:
            start = 550 - (int(card_len % 2) * 50) - (int(card_len / 2) * 100)
            self.card_x = [start + (i * 100) for i in range(self.card_remover)]
            for i in range(self.card_remover + 1, card_len + 1):
                self.card_x.append(int(start + (i * 100) - (self.card_change_count * 6.667)))
            self.card_y = [770 for _ in range(card_len - 1)]
            self.card_y.append(920)
            self.card_change_count += 1
            if self.card_change_count == 15:
                self.card_change_count = 1
                self.card_change_stage = 3
        elif self.card_change_stage == 3:
            start = 550 - (int(card_len % 2) * 50) - (int(card_len / 2) * 100)
            self.card_x = [start + (i * 100) for i in range(card_len)]
            self.card_y = [770 for _ in range(card_len - 1)]
            self.card_y.append(int(900 - (self.card_change_count * 8.667)))
            self.card_change_count += 1
            if self.card_change_count == 15:
                self.card_change_count = 1
                self.card_change_stage = 0
        elif self.card_change_stage == 4:
            start = 550 - (int(card_len % 2) * 50) - (int(card_len / 2) * 100)
            self.card_x = [start + (i * 100) for i in range(card_len)]
            self.card_y = [int(770 + (self.card_change_count * 8.667)) for _ in range(card_len)]
            self.card_change_count += 1
            if self.card_change_count >= 18:
                self.ending = False
                self.card_change_stage = 5

    def prepare_legend(self):
        # txt1, txt2, txt3, y1, y2, y3, box_y, box_h, box_w
        # self.player_names['g'] = 'testtest'
        self.legend_prep = [self.mini_f.render(self.player_names['b'], True, (255, 255, 255)),
                            self.mini_f.render(self.player_names['r'], True, (255, 255, 255)),
                            self.mini_f.render(self.player_names['g'], True, (255, 255, 255))]
        if self.player_names['g']:
            self.legend_prep.extend((13, 28, 43, 6, 53))
            if self.legend_prep[0].get_width() > self.legend_prep[1].get_width():
                if self.legend_prep[0].get_width() > self.legend_prep[2].get_width():
                    self.legend_prep.append(self.legend_prep[0].get_width() + 25)
                else:
                    self.legend_prep.append(self.legend_prep[2].get_width() + 25)
            else:
                if self.legend_prep[2].get_width() > self.legend_prep[1].get_width():
                    self.legend_prep.append(self.legend_prep[2].get_width() + 25)
                else:
                    self.legend_prep.append(self.legend_prep[1].get_width() + 25)
        else:
            self.legend_prep.extend((23, 38, -50, 16, 38))
            if self.legend_prep[0].get_width() > self.legend_prep[1].get_width():
                self.legend_prep.append(self.legend_prep[0].get_width() + 25)
            else:
                self.legend_prep.append(self.legend_prep[1].get_width() + 25)

    def render_legend(self):
        pygame.draw.rect(self.win, (251, 180, 41), self.zoom(34, self.legend_prep[6] - 1, self.legend_prep[8] + 2,
                                                             self.legend_prep[7] + 2), border_radius=5)
        pygame.draw.rect(self.win, (15, 112, 25), self.zoom(35, self.legend_prep[6], self.legend_prep[8],
                                                            self.legend_prep[7]), border_radius=5)
        chips = [self.mini_USChip, self.mini_AIChip, self.mini_GRChip]
        for i in range(3):
            self.win.blit(self.legend_prep[i], self.zoom(55, self.legend_prep[i + 3]))
            self.win.blit(chips[i], self.zoom(37, self.legend_prep[i + 3] - 4))

    def main_loop(self, go):
        self.go = go
        if self.gameEnded:
            self.card_positions()
            self.draw_cards()
            if self.name == self.winner:
                self.top_text('YOU WON')
            else:
                self.top_text('YOU LOST')
            self.draw_board()
        elif self.top_txt[:11] == "Waiting for":
            self.data = self.n.send(self.name)
            self.update_data()
            self.top_text(self.top_txt)
            self.draw_board(self.go, self.card_select)
        else:
            self.data = self.n.send(self.reply)
            self.update_data()
            self.card_positions()
            if self.top_txt == self.name:
                self.top_text('YOUR TURN')
            else:
                self.top_text(self.top_txt)
            self.render_legend()
            x = self.draw_board(self.go, self.card_select)
            self.clicked = self.draw_cards()
            if x:
                self.clicked = x
            if not self.turn:
                self.reply = 'ping'
                if self.is_five(self.board):
                    if 'YOU' in self.player_names['b']:
                        self.name = 'US'
                    elif 'YOU' in self.player_names['r']:
                        self.name = 'AI'
                    elif 'YOU' in self.player_names['g']:
                        self.name = 'GR'
                    self.gameEnded = True
                    del self.n
                    self.card_change_stage = 4
            else:
                self.detail = self.sequence_no
                self.card_select = self.main(self.cards)
                if self.reply != 'ping':
                    temp = self.n.send(self.reply).split('abc!')
                    self.board = []
                    render = temp[0].split(' ')
                    for i in range(10):
                        mini_board = []
                        for j in range(10):
                            mini_board.append(render[0])
                            del render[0]
                        self.board.append(mini_board)
                    if not (self.is_five(self.board)):
                        self.card_remover = self.cards.index(self.reply[2:])
                        self.card_change_stage = 1
                    else:
                        if 'YOU' in self.player_names['b']:
                            self.name = 'US'
                        elif 'YOU' in self.player_names['r']:
                            self.name = 'AI'
                        elif 'YOU' in self.player_names['g']:
                            self.name = 'GR'
                        self.gameEnded = True
                        del self.n
                        self.card_change_stage = 4
                    self.reply = 'ping'
                elif self.is_five(self.board):
                    if 'YOU' in self.player_names['b']:
                        self.name = 'US'
                    elif 'YOU' in self.player_names['r']:
                        self.name = 'AI'
                    elif 'YOU' in self.player_names['g']:
                        self.name = 'GR'
                    self.gameEnded = True
                    del self.n
                    self.card_change_stage = 4

    @staticmethod
    def quit():
        pygame.quit()
