import pygame
import os
from network import Network

try:
    pygame.init()
    pygame.display.init()
    pygame.mixer.init()
    Mon_Width, Mon_Height = pygame.display.Info().current_w, pygame.display.Info().current_h
    print(Mon_Width, Mon_Height)
    ZR = 1920 / Mon_Width
    WIN_WIDTH = int(1025 // ZR)
    WIN_HEIGHT = int(900 // ZR)
    print(WIN_WIDTH, WIN_HEIGHT)
    ip_ad = input("Please enter Server IP. (Computer next to Printer: 192.168.1.20, Rahul's Laptop, 192.168.1.14):\n")
    n = Network(ip_ad)
    winCards = []
    winner = ''
    # 1030, 754
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    cards = ['HA', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'H8', 'H9', 'H1', 'HJ', 'HQ', 'HK',
             'DA', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'D1', 'DJ', 'DQ', 'DK',
             'CA', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C1', 'CJ', 'CQ', 'CK',
             'SA', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'S9', 'S1', 'SJ', 'SQ', 'SK']

    card_select = 'xy'
    clicked = ''
    card_selected = False
    BoardCards = pygame.image.load(os.path.join('Sequence!!!.png')).convert_alpha()
    USChip = pygame.image.load(os.path.join('Blue.png')).convert_alpha()
    AIChip = pygame.image.load(os.path.join('Red.png')).convert_alpha()
    turn_change = pygame.mixer.Sound(os.path.join('chip.wav'))
    cardIMGs = {}
    run = True
    played = True

    USChip = pygame.transform.smoothscale(USChip, (int(50 // ZR), int(50 // ZR)))
    AIChip = pygame.transform.smoothscale(AIChip, (int(50 // ZR), int(50 // ZR)))
    BoardCards = pygame.transform.smoothscale(BoardCards, (int(960 // ZR), int(689 // ZR)))
    for cardNo in range(52):
        cardIMGs[str(cards[cardNo])] = pygame.image.load(
            os.path.join('Cards', str(cards[cardNo]) + '.png')).convert_alpha()
        cardIMGs[str(cards[cardNo])] = pygame.transform.smoothscale(cardIMGs[str(cards[cardNo])], (int(80 // ZR), int(112 // ZR)))


    def draw_board(curr_board: list, mouse: bool = False, highlight: str = 'xx') -> str:
        pos = pygame.mouse.get_pos()
        pygame.draw.rect(win, (255, 255, 255), (int(34 // ZR), int(72 // ZR), int(967 // ZR), int(692 // ZR)),
                         border_radius=5)
        pygame.draw.rect(win, (15, 112, 25), (int(35 // ZR), int(73 // ZR), int(965 // ZR), int(690 // ZR)),
                         border_radius=5)
        return_txt = ''
        for i in range(10):
            for j in range(10):
                if curr_board[i][j] == highlight:
                    pygame.draw.rect(win, (255, 255, 0), (
                        int(((43 + (j * 96)) - j // 5) // ZR), int(((81 + (i * 68)) - i // 2) // ZR), int(88 // ZR),
                        int(65 // ZR)), border_radius=5)
                elif highlight[1] == 'J':
                    if highlight[0] == 'H' or 'S' == highlight[0]:
                        if curr_board[i][j][2:] == 'AI' or curr_board[i][j][2:] == 'US':
                            pygame.draw.rect(win, (255, 255, 0), (
                                int(((43 + (j * 96)) - j // 5) // ZR), int(((81 + (i * 68)) - i // 2) // ZR), int(88 // ZR),
                                int(65 // ZR)), border_radius=5)
                    elif not (curr_board[i][j] == 'xx') and not (
                            curr_board[i][j][2:] == 'AI' or curr_board[i][j][2:] == 'US'):
                        pygame.draw.rect(win, (255, 255, 0), (
                            int(((43 + (j * 96)) - j // 5) // ZR), int(((81 + (i * 68)) - i // 2) // ZR), int(88 // ZR),
                            int(65 // ZR)), border_radius=5)
                card = pygame.Rect(
                    (int((45 + (j * 96)) // ZR), int((83 + (i * 68)) // ZR), int(84 // ZR), int(61 // ZR)))
                if mouse and card.collidepoint(pos):
                    return_txt = 'CARD' + str(i) + str(j)
                if winCards:
                    for card in winCards:
                        if int(card[0]) == i and j == int(card[1]):
                            pygame.draw.rect(win, (255, 255, 0), (
                                int(((43 + (j * 96)) - j // 5) // ZR), int(((81 + (i * 68)) - i // 2) // ZR), int(88 // ZR),
                                int(65 // ZR)), border_radius=5)
                            break
        win.blit(BoardCards, (int(37 // ZR), int(72 // ZR)))
        for i in range(10):
            for j in range(10):
                if curr_board[i][j][len(curr_board[i][j]) - 2:] == 'US':
                    pygame.draw.circle(win, (0, 0, 0), (int((87 + (j * 96)) // ZR), int((110 + (i * 68)) // ZR)),
                                       int(27 // ZR))
                    win.blit(USChip, (int((62 + (j * 96)) // ZR), int((85 + (i * 68)) // ZR)))
                elif curr_board[i][j][len(curr_board[i][j]) - 2:] == 'AI':
                    pygame.draw.circle(win, (0, 0, 0), (int((87 + (j * 96)) // ZR), int((110 + (i * 68)) // ZR)),
                                       int(27 // ZR))
                    win.blit(AIChip, (int((62 + (j * 96)) // ZR), int((85 + (i * 68)) // ZR)))
        return return_txt


    def draw_cards(Cards: list, mouse: bool = False, highlight: str = 'xx') -> str:
        pos = pygame.mouse.get_pos()
        return_txt = ''
        for i in range(7):
            if Cards[i] == 'NO':
                break
            if Cards[i] == highlight:
                pygame.draw.rect(win, (255, 255, 0),
                                 (int((198 + (i * 100)) // ZR), int(768 // ZR), int(84 // ZR), int(116 // ZR)),
                                 border_radius=5)
            card = pygame.Rect((int((200 + (i * 100)) // ZR), int(770 // ZR), int(80 // ZR), int(112 // ZR)))
            win.blit(cardIMGs[str(Cards[i])], (int((200 + (i * 100)) // ZR), int(770 // ZR)))
            if mouse and card.collidepoint(pos):
                return_txt = 'USER' + str(i)
        return return_txt


    def main(recent_click: str, hand_cards: list):
        global card_selected, reply, card_select
        if len(recent_click) == 5 and recent_click[:4] == 'USER':
            card_clicked = hand_cards[int(recent_click[4])]
            card_selected = True
            reply = 'ping'
            return card_clicked
        elif len(recent_click) == 6 and recent_click[:4] == 'CARD' and card_selected:
            card_clicked = board[int(recent_click[4])][int(recent_click[5])]
            if not (card_select[1] == 'J'):
                if card_clicked == card_select:
                    reply = str(int(recent_click[4])) + str(int(recent_click[5]))
                else:
                    reply = 'ping'
                    return card_select
            elif (card_select[0] == 'H') or (card_select[0] == 'S'):
                if (card_clicked[2:] == 'US') or (card_clicked[2:] == 'AI'):
                    reply = str(int(recent_click[4])) + str(int(recent_click[5]))
                else:
                    reply = 'ping'
                    return card_select
            else:
                if not ((card_clicked[2:] == 'US') or (card_clicked[2:] == 'AI') or card_clicked == 'xx'):
                    reply = str(int(recent_click[4])) + str(int(recent_click[5]))
                else:
                    reply = 'ping'
                    return card_select
            reply += str(card_select)
            card_selected = False
            return 'xy'
        reply = 'ping'
        return card_select


    def shift(grid):
        return [
            padding(r) + row + padding(len(row) - r - 1)
            for r, row in enumerate(grid)
        ]


    def padding(No):
        return ['None' for _ in range(No)]


    def transpose(grid):
        return [list(tup) for tup in zip(*grid)]


    def is_five(gameBoard):
        global winCards, winner
        state = ''
        # ONES CHECK
        counter = 0
        for i in range(len(gameBoard)):
            for j in range(len(gameBoard[i])):
                if gameBoard[i][j][-2:] == 'US' or gameBoard[i][j][-2:] == 'xx':
                    counter += 1
                    if counter == 5:
                        winner = 'US'
                        state = '01' + str(i) + str(j - 4)
                else:
                    counter = 0
        for i in range(len(gameBoard)):
            for j in range(len(gameBoard[i])):
                if gameBoard[i][j][-2:] == 'AI' or gameBoard[i][j][-2:] == 'xx':
                    counter += 1
                    if counter == 5:
                        winner = 'AI'
                        state = '01' + str(i) + str(j - 4)
                else:
                    counter = 0
        # TENS CHECK v2
        ten_board = transpose(gameBoard)
        counter = 0
        for i in range(len(ten_board)):
            for j in range(len(ten_board[i])):
                if ten_board[i][j][-2:] == 'US' or ten_board[i][j][-2:] == 'xx':
                    counter += 1
                    if counter == 5:
                        winner = 'US'
                        state = '10' + str(j - 4) + str(i)
                else:
                    counter = 0
        for i in range(len(ten_board)):
            for j in range(len(ten_board[i])):
                if ten_board[i][j][-2:] == 'AI' or ten_board[i][j][-2:] == 'xx':
                    counter += 1
                    if counter == 5:
                        winner = 'AI'
                        state = '10' + str(j - 4) + str(i)
                else:
                    counter = 0
        # FORWARD DIAGONALS CHECK
        ten_board = transpose(shift(reversed(gameBoard)))
        counter = 0
        for i in range(len(ten_board)):
            for j in range(len(ten_board[i])):
                if ten_board[i][j][-2:] == 'US' or ten_board[i][j][-2:] == 'xx':
                    counter += 1
                    if counter == 5:
                        winner = 'US'
                        state = '11' + str(9 - j) + str(i - j)
                else:
                    counter = 0
        for i in range(len(ten_board)):
            for j in range(len(ten_board[i])):
                if ten_board[i][j][-2:] == 'AI' or ten_board[i][j][-2:] == 'xx':
                    counter += 1
                    if counter == 5:
                        winner = 'AI'
                        state = '11' + str(9 - j) + str(i - j)
                else:
                    counter = 0
        # BACKWARDS DIAGONAL CHECK
        ten_board = transpose(shift(gameBoard))
        counter = 0
        for i in range(len(ten_board)):
            for j in range(len(ten_board[i])):
                if ten_board[i][j][-2:] == 'US' or ten_board[i][j][-2:] == 'xx':
                    counter += 1
                    if counter == 5:
                        winner = 'US'
                        state = '09' + str(j - 4) + str(i - j + 4)
                else:
                    counter = 0
        for i in range(len(ten_board)):
            for j in range(len(ten_board[i])):
                if ten_board[i][j][-2:] == 'AI' or ten_board[i][j][-2:] == 'xx':
                    counter += 1
                    if counter == 5:
                        winner = 'AI'
                        state = '9' + str(j - 4) + str(i)
                else:
                    counter = 0
        if winner:
            winCards.append(str(state[2:]))
            print(state)
            winCards.append(str(int(state[2:]) + int(state[:2])))
            winCards.append(str(int(state[2:]) + (2 * int(state[:2]))))
            winCards.append(str(int(state[2:]) + (3 * int(state[:2]))))
            winCards.append(str(int(state[2:]) + (4 * int(state[:2]))))
            for i in range(len(winCards)):
                if len(winCards[i]) == 1:
                    winCards[i] = '0' + winCards[i]
            return str(winner + state)
        else:
            return ''


    def animate(old_crd):
        global cards, board
        # Old Fly Out
        for i in range(15):
            win.fill((9, 66, 19))
            top_text('OPPONENT\'S TURN')
            draw_board(board, False, 'xy')
            for j in range(7):
                if cards.index(old_crd) != j:
                    win.blit(cardIMGs[str(cards[j])], (int((200 + (j * 100)) // ZR), int(770 // ZR)))
                else:
                    win.blit(cardIMGs[str(cards[j])], (int((200 + (j * 100)) // ZR), int((770 + (i * 8.667)) // ZR)))
            clock.tick(30)
            pygame.display.flip()
            data0 = n.send('ping')

        # Cards Move Left
        for i in range(15):
            win.fill((9, 66, 19))
            top_text('OPPONENT\'S TURN')
            draw_board(board, False, 'xy')
            for j in range(7):
                if j < cards.index(old_crd):
                    win.blit(cardIMGs[str(cards[j])], (int((200 + (j * 100)) // ZR), int(770 // ZR)))
                elif j > cards.index(old_crd):
                    win.blit(cardIMGs[str(cards[j])], (int((200 + (j * 100) - (i * 6.667)) // ZR), int(770 // ZR)))
            clock.tick(30)
            pygame.display.flip()
            data0 = n.send('ping')

        # New Fly Up
        for i in range(15):
            win.fill((9, 66, 19))
            top_text('OPPONENT\'S TURN')
            draw_board(board, False, 'xy')
            for j in range(7):
                if j < cards.index(old_crd):
                    win.blit(cardIMGs[str(cards[j])], (int((200 + (j * 100)) // ZR), int(770 // ZR)))
                elif j < 6:
                    win.blit(cardIMGs[str(cards[j + 1])], (int((200 + (j * 100)) // ZR), int(770 // ZR)))
                else:
                    win.blit(cardIMGs[str(cards[7])], (int((200 + (j * 100)) // ZR), int(900 - (i * 8.667) // ZR)))
            clock.tick(30)
            pygame.display.flip()
            data0 = n.send('ping')


    def brd_unpack(render):
        big_board = []
        render = render.split(' ')
        for i in range(10):
            mini_board = []
            for j in range(10):
                mini_board.append(render[0])
                del render[0]
            big_board.append(mini_board)
        return big_board


    def top_text(render):
        text = Font.render(render, True, (255, 255, 255))
        x_val = int(WIN_WIDTH // 2 - text.get_width() // 2)
        win.blit(text, (x_val, int(25 // ZR)))


    pygame.font.init()
    clock = pygame.time.Clock()
    Font = pygame.font.Font(None, 40)
    dataO = n.get_dat()
    while run:
        go = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.MOUSEBUTTONUP:
                go = True
        data = dataO.split('abc!')
        board = brd_unpack(data[0])
        turn = bool(data[1])
        cards = data[2].split(' ')
        top_txt = data[3]
        reply = ''

        win.fill((9, 66, 19))
        if is_five(board):
            if not turn:
                top_text('YOU WON')
            else:
                top_text('YOU LOOSE')
            draw_board(board, False, 'xy')
            reply = 'ping'
        else:
            top_text(top_txt)
            x = draw_board(board, go, card_select)
            clicked = draw_cards(cards[:7], go, card_select)

            if x:
                clicked = x
            if not turn:
                reply = 'ping'
            else:
                card_select = main(clicked, cards[:7])
                if played:
                    turn_change.play()
                    played = False
                if reply != 'ping':
                    dataO = n.send(reply)
                    data = dataO.split('abc!')
                    board = brd_unpack(data[0])
                    turn_change.play()
                    played = True
                    animate(reply[2:])
                    continue
        clock.tick(30)
        pygame.display.flip()
        dataO = n.send(reply)
    pygame.quit()
except Exception as e:
    print(e)
    with open('ERROR Devlog.txt', 'w') as f:
        f.write(str(e))
        f.write('\n\n')
        f.write(str(board))
        f.write('\n\n')
        f.write(str(cards))
