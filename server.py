import socket
from _thread import *
from random import randint
import pickle


def server_start(players, teams):
    global board, cards, turn, curr_player, server, s, names, player_cards, board_marker, player_no, team_no, card_deals
    board = [['xx', 'S1', 'SQ', 'SK', 'SA', 'D2', 'D3', 'D4', 'D5', 'xx'],
             ['S9', 'H1', 'H9', 'H8', 'H7', 'H6', 'H5', 'H4', 'H3', 'D6'],
             ['S8', 'HQ', 'D7', 'D8', 'D9', 'D1', 'DQ', 'DK', 'H2', 'D7'],
             ['S7', 'HK', 'D6', 'C2', 'HA', 'HK', 'HQ', 'DA', 'S2', 'D8'],
             ['S6', 'HA', 'D5', 'C3', 'H4', 'H3', 'H1', 'CA', 'S3', 'D9'],
             ['S5', 'C2', 'D4', 'C4', 'H5', 'H2', 'H9', 'CK', 'S4', 'D1'],
             ['S4', 'C3', 'D3', 'C5', 'H6', 'H7', 'H8', 'CQ', 'S5', 'DQ'],
             ['S3', 'C4', 'D2', 'C6', 'C7', 'C8', 'C9', 'C1', 'S6', 'DK'],
             ['S2', 'C5', 'SA', 'SK', 'SQ', 'S1', 'S9', 'S8', 'S7', 'DA'],
             ['xx', 'C6', 'C7', 'C8', 'C9', 'C1', 'CQ', 'CK', 'CA', 'xx']]
    cards = ['HA', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'H8', 'H9', 'H1', 'HJ', 'HQ', 'HK',
             'DA', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'D1', 'DJ', 'DQ', 'DK',
             'CA', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C1', 'CJ', 'CQ', 'CK',
             'SA', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'S9', 'S1', 'SJ', 'SQ', 'SK',
             'HA', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'H8', 'H9', 'H1', 'HJ', 'HQ', 'HK',
             'DA', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'D1', 'DJ', 'DQ', 'DK',
             'CA', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C1', 'CJ', 'CQ', 'CK',
             'SA', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'S9', 'S1', 'SJ', 'SQ', 'SK']
    card_deals = {2: {2: 7, 4: 6, 6: 5, 8: 4, 10: 3, 12: 3},
                  3: {3: 6, 6: 5, 9: 4, 12: 3}}
    board_marker = {0: 'US', 1: 'AI', 2: 'GR'}
    player_no = players
    team_no = teams
    player_cards = {i: [] for i in range(player_no)}
    names = {}
    turn = 0
    new_deck = []
    for card in range(len(cards)):
        c_num = randint(0, len(cards) - 1)
        new_deck.append(cards[c_num])
        del cards[c_num]
    cards = new_deck

    # Server Setup
    server = str(socket.gethostbyname(socket.gethostname()))
    port = 5555
    curr_player = 0
    print(socket.gethostbyname(socket.gethostname()))

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.bind((server, port))
    except socket.error as e:
        print(str(e))

    s.listen(2)
    print("Server started.")
    print("Waiting for connection.")

    deal()
    while True:
        conns, addr = s.accept()
        print("Connected to:", addr)

        start_new_thread(threaded_client, (conns, curr_player))
        curr_player += 1


def deal():
    global cards, player_cards, player_no, card_deals, team_no
    for el in range(player_no):
        while len(player_cards[el]) < card_deals[team_no][player_no]:
            player_cards[el].append(cards[0])
            del cards[0]


def create_msg(boardMsg, crds, top_text, my_turn):
    final = ''
    for i in range(10):
        final += ' '.join(boardMsg[i])
        final += ' '
    final += 'abc!'
    final += my_turn
    final += 'abc!'
    if crds[0] == 'NO':
        final += 'NO NO'
    else:
        final += ' '.join(crds)
    final += 'abc!'
    final += top_text
    return final


def threaded_client(conn, player):
    try:
        global turn, board, names, player_cards, board_marker, player_no, team_no, curr_player
        sender = create_msg(board, ['NO', 'NO'], ('Waiting for ' + str(player_no - curr_player) + ' Player(s). Join at '
                                                  + str(server)), str(2))
        conn.sendall(pickle.dumps(sender))
        reply = pickle.loads(conn.recv(2048))
        if reply in names.values():
            sender = "NO NO NO"
            curr_player -= 1
            conn.sendall(pickle.dumps(sender))
            pickle.loads(conn.recv(2048))
            conn.sendall(pickle.dumps(sender))
            pickle.loads(conn.recv(2048))
        while len(names) < player_no:
            sender = create_msg(board, ['NO', 'NO'], ('Waiting for ' + str(player_no - curr_player) +
                                                      ' Player(s). Join at ' + str(server)), str(2))
            conn.sendall(pickle.dumps(sender))
            reply = pickle.loads(conn.recv(2048))
            names[player] = reply
            if not reply:
                print("Disconnected")
                break
        sender = 'aaBaa'.join(names.values())
        sender += 'aaBaa'
        sender += str(team_no)
        for _ in range(3):
            conn.sendall(pickle.dumps(sender))
            pickle.loads(conn.recv(2048))
        conn.sendall(pickle.dumps(sender))
        while True:
            try:
                reply = pickle.loads(conn.recv(2048))
                turn_send = (turn - player) % player_no
                if player >= player_no:
                    sender = create_msg(board, ['NO', 'NO'], str(names[turn].upper() + '\'S TURN'), str(2))
                elif reply == 'ping':
                    sender = create_msg(board, player_cards[player], str(names[turn].upper() + '\'S TURN'),
                                        str(turn_send))
                else:
                    turn = (turn + 1) % player_no
                    del player_cards[player][player_cards[player].index(reply[2:])]
                    deal()
                    if len(board[int(reply[0])][int(reply[1])]) == 2:
                        board[int(reply[0])][int(reply[1])] += board_marker[(player % team_no)]
                    else:
                        board[int(reply[0])][int(reply[1])] = board[int(reply[0])][int(reply[1])][:2]
                    for all_cards in player_cards[player]:
                        if all_cards[1] == 'J':
                            continue
                        else:
                            ded = True
                            for CardRow in board:
                                if all_cards in CardRow:
                                    ded = False
                                    break
                            if ded:
                                print('DEADDDDDD CARD')
                                del player_cards[player][player_cards[player].index(all_cards)]
                                deal()
                                break
                    sender = create_msg(board, player_cards[player], str(names[turn].upper() + '\'S TURN'), str(1))

                # COMMUNICATION
                if not reply:
                    print("Disconnected")
                    break
                else:
                    if reply != 'ping':
                        print("Player No.", player, "Received:", reply)
                        print("Player No.", player, "Sending:", sender)
                conn.sendall(pickle.dumps(sender))
            except Exception as e:
                print(e)
                break
        print('Lost connection.')
        conn.close()
    except EOFError:
        print('EOFError')
