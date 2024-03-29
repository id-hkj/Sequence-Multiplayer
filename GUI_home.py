import pygame
from GUI_game import GameScreen
import time
import socket
from server import server_start, server_startup
from _thread import *
import os
from tkinter import messagebox
from tkinter import Tk

pygame.init()
pygame.display.init()
pygame.font.init()
pygame.display.set_caption("Sequence Game")


class InputBox:

    def __init__(self, rect_dims, max_chr, text, min_asc, max_asc, font):
        self.rect = pygame.Rect(rect_dims)
        self.color = pygame.Color('lightskyblue3')
        self.text = ''
        self.font = font
        self.txt_surface = self.font.render(text, True, self.color)
        self.active = False
        self.char_on = 0
        self.x = rect_dims[0]
        self.cursor = pygame.Rect((self.x, rect_dims[1] + 5), (2, rect_dims[3] - 10))
        self.max = max_chr
        self.min_asc = min_asc
        self.max_asc = max_asc
        self.char_w = font.render('.', True, (0, 0, 0)).get_width()

    def handle_event(self, click, key_info, mouse_pos):
        if click:
            if self.rect.collidepoint(mouse_pos):
                self.active = True
                self.char_on = mouse_pos[0] - self.x - 3
                self.char_on = int(self.char_on / 14) + 1 if self.char_on % 14 > 7 else int(self.char_on / 14)
                if self.char_on > len(self.text):
                    self.char_on = len(self.text)
                self.color = pygame.Color('dodgerblue2')
                self.txt_surface = self.font.render(self.text, True, self.color)
            else:
                self.active = False
                self.color = pygame.Color('lightskyblue3')
        elif key_info and self.active:
            if key_info.key == pygame.K_BACKSPACE:
                self.text = self.text[:self.char_on - 1] + self.text[self.char_on:]
                if self.char_on != 0:
                    self.char_on -= 1
            elif key_info.key == pygame.K_LEFT:
                if self.char_on != 0:
                    self.char_on -= 1
            elif key_info.key == pygame.K_RIGHT:
                if self.char_on != self.max and self.char_on != len(self.text):
                    self.char_on += 1
            elif key_info.key == pygame.K_DELETE:
                self.text = self.text[:self.char_on] + self.text[self.char_on + 1:]
            elif key_info.key == pygame.K_HOME:
                self.char_on = 0
            elif key_info.key == pygame.K_END:
                self.char_on = len(self.text)
            elif key_info.unicode:
                if (self.min_asc <= ord(key_info.unicode) <= self.max_asc) and (len(self.text) < self.max):
                    self.text = list(self.text)
                    self.text.insert(self.char_on, key_info.unicode)
                    self.text = ''.join(self.text)
                    self.char_on += 1
            # Re-render the text.
            self.txt_surface = self.font.render(self.text, True, self.color)

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 4))
        pygame.draw.rect(screen, self.color, (self.rect[0], self.rect[1], self.rect[2], self.rect[3]), 2)
        if time.time() % 1 > 0.5 and self.active:
            self.cursor.x = self.x + 3 + self.char_w * self.char_on
            pygame.draw.rect(screen, self.color, self.cursor)


class OptionBox:

    def __init__(self, rect_dimensions, color, highlight_color, font, option_list, selected=0):
        self.color = color
        self.highlight_color = highlight_color
        self.rect = pygame.Rect(rect_dimensions[:2], rect_dimensions[2:])
        self.font = font
        self.option_list = option_list
        self.selected = selected
        self.draw_menu = False
        self.menu_active = False
        self.active_option = -1

    def draw(self, surf):
        pygame.draw.rect(surf, self.highlight_color if self.menu_active else self.color, self.rect)
        pygame.draw.rect(surf, (0, 0, 0), self.rect, 2)
        msg = self.font.render(self.option_list[self.selected], 1, (0, 0, 0))
        surf.blit(msg, msg.get_rect(center=self.rect.center))

        if self.draw_menu:
            for i, text in enumerate(self.option_list):
                rect = self.rect.copy()
                rect.y += (i + 1) * self.rect.height
                pygame.draw.rect(surf, self.highlight_color if i == self.active_option else self.color, rect)
                msg = self.font.render(text, 1, (0, 0, 0))
                surf.blit(msg, msg.get_rect(center=rect.center))
            outer_rect = (
                self.rect.x, self.rect.y + self.rect.height, self.rect.width, self.rect.height * len(self.option_list))
            pygame.draw.rect(surf, (0, 0, 0), outer_rect, 2)

    def update(self, click, mouse):
        my_pos = mouse
        self.menu_active = self.rect.collidepoint(my_pos)

        self.active_option = -1
        for i in range(len(self.option_list)):
            rect = self.rect.copy()
            rect.y += (i + 1) * self.rect.height
            if rect.collidepoint(my_pos):
                self.active_option = i
                break

        if not self.menu_active and self.active_option == -1:
            self.draw_menu = False

        if click:
            if self.menu_active:
                self.draw_menu = not self.draw_menu
            elif self.draw_menu and self.active_option >= 0:
                self.selected = self.active_option
                self.draw_menu = False
                return self.active_option
        return -1


class Button:

    def __init__(self, dimensions, text, win, font, border_col=(0, 0, 0), back_col=(0, 30, 0), rad=0):
        self.rect_dimensions = dimensions
        self.border_dimensions = (dimensions[0] - 2, dimensions[1] - 2, dimensions[2] + 4, dimensions[3] + 4)
        self.text = text
        self.font = font
        self.text_img = self.font.render(self.text, True, (255, 255, 255))
        self.border_col = border_col
        self.back_col = back_col
        self.rad = rad
        # self.text_pos = text_pos
        self.text_pos = (int((dimensions[2] - self.text_img.get_width()) / 2) + dimensions[0],
                         int((dimensions[3] - self.text_img.get_height()) / 2) + dimensions[1])
        self.win = win
        self.rect = pygame.Rect(dimensions[:2], dimensions[2:])

    def render(self):
        pygame.draw.rect(self.win, self.border_col, self.border_dimensions, border_radius=self.rad)
        pygame.draw.rect(self.win, self.back_col, self.rect_dimensions, border_radius=self.rad)
        self.win.blit(self.text_img, self.text_pos)

    def is_clicked(self, c, mouse_pos):
        if c and self.rect.collidepoint(mouse_pos):
            return True
        return False


class Nav:

    def __init__(self):
        # SETUP
        self.taken = False
        self.mon_width = pygame.display.Info().current_w
        self.mon_height = pygame.display.Info().current_h
        self.zr = 1920 / self.mon_width
        if 900 / 1025 > self.mon_height / self.mon_width:
            x = self.mon_height / 900
            self.win_width = int(1025 * x)
            self.win_height = self.mon_height
            self.scalar = (int((self.mon_width - self.win_width) / 2), 0, self.win_width, self.mon_height)
        else:
            x = self.mon_width / 1025
            self.win_height = int(900 * x)
            self.win_width = self.mon_width
            self.scalar = (0, int((self.mon_height - self.win_height) / 2), self.mon_width, self.win_height)
        self.w_zr = 1025 / self.win_width
        self.h_zr = 900 / self.win_height
        self.run = True
        self.events = []
        self.win = pygame.Surface((1025, 900))
        self.real_win = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        self.scene = 'h'
        self.c = False
        self.key = False
        self.Font = pygame.font.Font(None, 150)
        self.Heading = pygame.font.Font(None, 50)
        self.Text = pygame.font.Font(None, 40)
        self.mouse_pos = pygame.mouse.get_pos()
        self.Team_Count = 2
        self.Player_Count = 1
        self.PPT_lst = ["1", "2", "3", "4", "5", "6"]
        self.game_opacity = -1
        self.transparent_stage = 'g'
        self.out_t_no = 151

        # BUTTONS/DROPDOWNS
        self.play = Button((224, 410, 578, 125), 'PLAY', self.win, self.Font)
        self.how_to = Button((224, 550, 578, 50), 'HOW TO PLAY', self.win, self.Heading)
        self.back = Button((20, 830, 115, 50), 'BACK', self.win, self.Heading)
        self.create_b = Button((224, 310, 578, 125), 'CREATE', self.win, self.Font)
        self.join_b = Button((224, 450, 578, 125), 'JOIN', self.win, self.Font)
        self.join_go = Button((800, 150, 115, 75), 'GO', self.win, self.Heading)
        self.create_go = Button((775, 200, 200, 75), 'CREATE', self.win, self.Heading)
        self.return_home = Button((828, 12, 170, 50), 'EXIT GAME', self.win, self.Text, rad=5)
        self.confirm_y = Button((290, 465, 220, 45), 'Yes', self.win, self.Text, rad=5)
        self.confirm_n = Button((525, 465, 220, 45), 'No', self.win, self.Text, rad=5)
        self.team_no = OptionBox((50, 200, 25, 32), (150, 150, 150), (100, 200, 255), self.Text, ["2", "3"])
        self.player_no = OptionBox((50, 240, 25, 32), (150, 150, 150), (100, 200, 255), self.Text,
                                   self.PPT_lst)
        for i in range(20):
            self.special_update()

        # JOIN/CREATE
        self.mono_font = pygame.font.SysFont('consolas', 25)
        self.name_enter = InputBox((210, 150, 220, 30), 15, 'Name', 33, 126, self.mono_font)
        self.ip_enter = InputBox((210, 200, 220, 30), 15, 'IP Address', 46, 57, self.mono_font)
        self.ip_error = False
        self.name_error = False

        # MAIN GAME
        self.game = GameScreen(self.win)

        # Other Instance Check!
        if not os.path.exists('SEQUENCE_GAME_LRP2024'):
            self.fd = os.open('SEQUENCE_GAME_LRP2024', os.O_CREAT | os.O_EXCL | os.O_RDWR)
            server_startup()
        else:
            self.run = False
            pygame.quit()
            Tk().wm_withdraw()
            messagebox.showerror('error', 'You cannot run multiple instances of this application at any one time.')
            print('OTHER RUNNING!!!')

    def draw_home(self):
        self.win.blit(self.Font.render('SEQUENCE', True, (255, 255, 255)), (224, 300))
        # Buttons
        self.play.render()
        self.how_to.render()
        if self.out_t_no < 151:
            self.win.blit(self.Text.render('Game ended because someone disconnected from server.', True, (255, 0, 0)),
                          (124, 20))
            self.out_t_no += 1
        if self.play.is_clicked(self.c, self.mouse_pos):
            self.scene = 'p'
        elif self.how_to.is_clicked(self.c, self.mouse_pos):
            self.scene = 't'

    def tutorial(self):
        self.win.blit(self.Font.render('GAME RULES', True, (255, 255, 255)), (175, 15))
        # AIM section
        pygame.draw.rect(self.win, (251, 180, 41), (14, 129, 422, 192))
        pygame.draw.rect(self.win, (15, 50, 15), (15, 130, 420, 190))
        self.win.blit(self.Heading.render('AIM:', True, (255, 255, 255)), (166, 140))
        self.win.blit(self.Text.render('Get a sequence of 5 in a row.', True, (255, 255, 255)), (22, 180))
        self.win.blit(self.Text.render('2 TEAMS: 2 sequences to win', True, (255, 255, 255)), (22, 225))
        self.win.blit(self.Text.render('3 TEAMS: 1 sequence to win.', True, (255, 255, 255)), (22, 270))
        # On Your Turn
        pygame.draw.rect(self.win, (251, 180, 41), (444, 129, 572, 192))
        pygame.draw.rect(self.win, (15, 50, 15), (445, 130, 570, 190))
        self.win.blit(self.Heading.render('ON YOUR TURN:', True, (255, 255, 255)), (584, 140))
        self.win.blit(self.Text.render('1. Select a card to play (You can change', True, (255, 255, 255)),
                      (452, 180))
        self.win.blit(self.Text.render('your selection by clicking another card)', True, (255, 255, 255)),
                      (460, 215))
        self.win.blit(self.Text.render('2. Click a square on the gameboard', True, (255, 255, 255)),
                      (452, 260))
        # JACKS
        pygame.draw.rect(self.win, (251, 180, 41), (14, 329, 482, 192))
        pygame.draw.rect(self.win, (15, 50, 15), (15, 330, 480, 190))
        self.win.blit(self.Heading.render('JACKS:', True, (255, 255, 255)), (154, 340))
        self.win.blit(self.Text.render('2-EYED JACKS: Wild', True, (255, 255, 255)), (22, 380))
        self.win.blit(self.Text.render('1-EYED JACKS: Remove counter', True, (255, 255, 255)), (22, 425))
        self.win.blit(self.Text.render('UNLESS counter part of sequence', True, (255, 255, 255)),
                      (30, 470))
        # THE GAMEBOARD
        pygame.draw.rect(self.win, (251, 180, 41), (509, 329, 507, 192))
        pygame.draw.rect(self.win, (15, 50, 15), (510, 330, 505, 190))
        self.win.blit(self.Heading.render('THE GAMEBOARD:', True, (255, 255, 255)), (609, 340))
        self.win.blit(self.Text.render('Each Card (except the jacks) are', True, (255, 255, 255)),
                      (517, 380))
        self.win.blit(self.Text.render('pictured twice.', True, (255, 255, 255)), (517, 425))
        self.win.blit(self.Text.render('The four corners are freebies.', True, (255, 255, 255)),
                      (517, 470))
        # Buttons
        self.back.render()
        if self.back.is_clicked(self.c, self.mouse_pos):
            self.scene = 'h'

    def pregame(self):
        # Buttons
        self.create_b.render()
        self.join_b.render()
        self.back.render()
        if self.join_b.is_clicked(self.c, self.mouse_pos):
            self.scene = 'j'
            self.name_enter.text = ''
            self.ip_enter.text = ''
            self.name_error = False
            self.ip_error = False
            self.name_enter.txt_surface = self.name_enter.font.render('Name', True, pygame.Color('lightskyblue3'))
            self.ip_enter.txt_surface = self.name_enter.font.render('IP Address', True, pygame.Color('lightskyblue3'))
        elif self.create_b.is_clicked(self.c, self.mouse_pos):
            self.scene = 'c'
            self.name_enter.text = ''
            self.name_error = False
            self.name_enter.txt_surface = self.name_enter.font.render('Name', True, self.name_enter.color)
        elif self.back.is_clicked(self.c, self.mouse_pos):
            self.scene = 'h'

    def join(self):
        self.ip_enter.handle_event(self.c, self.key, self.mouse_pos)
        self.name_enter.handle_event(self.c, self.key, self.mouse_pos)
        if self.ip_enter.rect.collidepoint(self.mouse_pos) or self.name_enter.rect.collidepoint(self.mouse_pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        self.ip_enter.draw(self.win)
        self.name_enter.draw(self.win)
        self.win.blit(self.Font.render('JOIN A GAME', True, (255, 255, 255)), (175, 15))
        if self.name_error:
            self.win.blit(self.Text.render('No name entered', True, (236, 62, 19)), (520, 153))
        elif self.taken:
            self.win.blit(self.Text.render('Name Taken', True, (236, 62, 19)), (520, 153))
        if self.ip_error:
            self.win.blit(self.Text.render('Invalid IP address', True, (236, 62, 19)), (520, 203))
        self.win.blit(self.Text.render('Your Name: ', True, (255, 255, 255)), (50, 153))
        self.win.blit(self.Text.render('IP Address:', True, (255, 255, 255)), (50, 203))
        self.back.render()
        self.join_go.render()
        if self.join_go.is_clicked(self.c, self.mouse_pos):
            pygame.draw.rect(self.win, (9, 66, 19), (515, 150, 250, 80))
            pygame.display.flip()
            if self.name_enter.text and self.ip_enter.text and self.name_enter.text != 'YOU':
                self.game.connect(self.ip_enter.text, self.name_enter.text)
                if self.game.scene == 'g':
                    self.scene = 'g'
                elif self.game.scene == 'name':
                    self.taken = True
                else:
                    self.ip_error = True
            else:
                self.ip_error = not self.ip_enter.text
                self.name_error = True if self.name_enter.text == 'YOU' else not self.name_enter.text
        elif self.back.is_clicked(self.c, self.mouse_pos):
            self.scene = 'p'

    def create(self):
        self.name_enter.handle_event(self.c, self.key, self.mouse_pos)
        if self.name_enter.rect.collidepoint(self.mouse_pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        self.name_enter.draw(self.win)
        selected_p = int(self.player_no.update(self.c, self.mouse_pos)) if not self.team_no.draw_menu else -1
        selected_t = int(self.team_no.update(self.c, self.mouse_pos))
        if selected_t != -1:
            self.Team_Count = selected_t + 2
            self.player_no.option_list = self.PPT_lst[:6 - 2 * selected_t]
            if self.Player_Count > 4:
                self.player_no.selected = 0
                self.Player_Count = 1
        if selected_p != -1:
            self.Player_Count = selected_p + 1
        self.win.blit(self.Font.render('CREATE A GAME', True, (255, 255, 255)), (70, 15))
        self.win.blit(self.Text.render('Your Name: ', True, (255, 255, 255)), (50, 153))
        if self.name_error:
            self.win.blit(self.Text.render('No name entered', True, (236, 62, 19)), (520, 153))
        self.back.render()
        self.create_go.render()
        self.player_no.draw(self.win)
        self.team_no.draw(self.win)
        self.win.blit(self.Text.render('TEAMS', True, (255, 255, 255)), (80, 205))
        self.win.blit(self.Text.render('PLAYERS PER TEAM', True, (255, 255, 255)), (80, 245))
        if self.create_go.is_clicked(self.c, self.mouse_pos):
            if self.name_enter.text and self.name_enter.text != 'YOU':
                start_new_thread(server_start, (self.Team_Count * self.Player_Count, self.Team_Count))
                time.sleep(0.5)
                while True:
                    self.game.connect(socket.gethostbyname(socket.gethostname()), self.name_enter.text)
                    while self.game.scene == "load":
                        time.sleep(0.1)
                    if self.game.scene == 'g':
                        break
                self.scene = 'g'
            else:
                self.name_error = True
        elif self.back.is_clicked(self.c, self.mouse_pos):
            self.scene = 'p'

    def special_update(self, direction='u'):
        if direction == 'd':
            temp = list(self.confirm_y.rect_dimensions)
            temp[1] += 26
            self.confirm_y.rect_dimensions = tuple(temp)
            temp = list(self.confirm_n.rect_dimensions)
            temp[1] += 26
            self.confirm_n.rect_dimensions = tuple(temp)
            temp = list(self.confirm_y.border_dimensions)
            temp[1] += 26
            self.confirm_y.border_dimensions = tuple(temp)
            temp = list(self.confirm_n.border_dimensions)
            temp[1] += 26
            self.confirm_n.border_dimensions = tuple(temp)
            temp = list(self.confirm_y.text_pos)
            temp[1] += 26
            self.confirm_y.text_pos = tuple(temp)
            temp = list(self.confirm_n.text_pos)
            temp[1] += 26
            self.confirm_n.text_pos = tuple(temp)
        elif direction == 'u':
            temp = list(self.confirm_y.rect_dimensions)
            temp[1] -= 26
            self.confirm_y.rect_dimensions = tuple(temp)
            temp = list(self.confirm_n.rect_dimensions)
            temp[1] -= 26
            self.confirm_n.rect_dimensions = tuple(temp)
            temp = list(self.confirm_y.border_dimensions)
            temp[1] -= 26
            self.confirm_y.border_dimensions = tuple(temp)
            temp = list(self.confirm_n.border_dimensions)
            temp[1] -= 26
            self.confirm_n.border_dimensions = tuple(temp)
            temp = list(self.confirm_y.text_pos)
            temp[1] -= 26
            self.confirm_y.text_pos = tuple(temp)
            temp = list(self.confirm_n.text_pos)
            temp[1] -= 26
            self.confirm_n.text_pos = tuple(temp)

    def mid_g_leave(self):
        # Darken game screen
        shape_surf = pygame.Surface(pygame.Rect(0, 0, self.win_width, self.win_height).size, pygame.SRCALPHA)
        pygame.draw.rect(shape_surf, (0, 0, 0, self.game_opacity * 5), shape_surf.get_rect())
        self.win.blit(shape_surf, (0, 0, self.win_width, self.win_height))

        # Prompt Box
        pygame.draw.rect(self.win, (251, 180, 41), (264, 26 * self.game_opacity - 199, 507, 197),
                         border_radius=5)
        pygame.draw.rect(self.win, (15, 50, 15), (265, 26 * self.game_opacity - 198, 505, 195),
                         border_radius=5)
        self.win.blit(self.Text.render('ARE YOU SURE YOU WANT TO', True, (255, 255, 255)),
                      (310, self.game_opacity * 26 - 185))
        self.win.blit(self.Text.render('EXIT THE GAME?', True, (255, 255, 255)),
                      (397, self.game_opacity * 26 - 155))
        self.win.blit(self.Text.render('This will also end the game for', True, (255, 255, 255)),
                      (308, self.game_opacity * 26 - 120))
        self.win.blit(self.Text.render('everyone else playing.', True, (255, 255, 255)),
                      (368, self.game_opacity * 26 - 90))
        self.confirm_y.render()
        self.confirm_n.render()
        if self.confirm_y.is_clicked(self.c, self.mouse_pos):
            del self.game.n
            self.scene = 'h'
            for i in range(21):
                self.special_update()
            self.game_opacity = -2
        elif self.confirm_n.is_clicked(self.c, self.mouse_pos):
            self.transparent_stage = 's'

        # Opacity deal
        if self.game_opacity < 20 and self.transparent_stage == 'g':
            self.game_opacity += 1
            self.special_update('d')
        elif self.transparent_stage == 's':
            if self.game_opacity > 0:
                self.game_opacity -= 1
                self.special_update()
            else:
                self.transparent_stage = 'g'
                self.game_opacity = -1

    def main_loop(self):
        while self.run:
            self.c = False
            self.key = False
            self.mouse_pos = list(pygame.mouse.get_pos())
            self.mouse_pos[0] = int((self.mouse_pos[0] - self.scalar[0]) * self.w_zr)
            self.mouse_pos[1] = int((self.mouse_pos[1] - self.scalar[1]) * self.h_zr)
            self.mouse_pos = tuple(self.mouse_pos)
            self.events = pygame.event.get()
            for event in self.events:
                if event.type == pygame.QUIT:
                    self.run = False
                    break
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.c = True
                elif event.type == pygame.KEYDOWN:
                    self.key = event
                    if event.key == pygame.K_ESCAPE:
                        self.run = False
            self.win.fill((9, 66, 19))
            if self.scene == 'h':  # Home
                self.draw_home()
            elif self.scene == 't':  # Tutorial
                self.tutorial()
            elif self.scene == 'p':
                self.pregame()
            elif self.scene == 'c':  # Create new game
                self.create()
            elif self.scene == 'j':  # Join new game
                self.join()
            elif self.scene == 'g':  # Running the Game
                x = self.game.main_loop(self.c, self.mouse_pos)
                self.return_home.render()
                if self.return_home.is_clicked(self.c, self.mouse_pos):
                    if not self.game.gameEnded:
                        self.game_opacity = 0
                    else:
                        self.scene = 'h'
                if self.game_opacity != -1:
                    self.mid_g_leave()
                if x == 'BROKEN':
                    self.out_t_no = 0
                    self.scene = 'h'
                    self.game.__init__(self.win)
            transformed_screen = pygame.transform.scale(self.win, (self.win_width, self.win_height))
            self.real_win.blit(transformed_screen, self.scalar[:2])
            pygame.display.flip()
            self.clock.tick(30)
        os.close(self.fd)
        os.unlink('SEQUENCE_GAME_LRP2024')
        if self.scene == 'g':
            self.game.quit()
        pygame.quit()


home = Nav()
if home.run:
    home.main_loop()
