from django.shortcuts import render_to_response
from game.models import Board, Deck

from game import git

def index(request, branch):
    card_row = git.get_deck(branch)[:13]
    civ = git.get_civ(branch)

    for index in range(len(card_row), 13):
        card_row.append({'file': "Blank.png"})
    card_row = [ x and x or {'file': "Blank.png"} for x in card_row ]
    print civ

    return render_to_response('game/index.html', {
            'card_row': [ x['file'] for x in card_row ],
            'branch': branch,
            'civ': civ,
            'military': git.get_military(branch),
            'blue': dict([ (str(x+1),1) for x in range(min(civ['blue_tokens'], 18)) ]),
            'blue_leftover': max(civ['blue_tokens'] - 18, 0),
            'yellow': dict([ (str(x+1),1) for x in range(min(civ['yellow_tokens'], 18)) ]),
            })

def slide(request, branch):
    deck = git.get_deck(branch)
    first = deck[0]
    if first:
        deck.pop(0)
    
    deck = [ x for x in deck if x ]
    git.write_deck(branch, deck, "slide")

    return index(request, branch)

def add_to_hand(request, branch, index_no):
    index_no = int(index_no) - 1
    deck = git.get_deck(branch)

    if deck[index_no]:
        cell = deck[index_no]['cell']
        civ = git.get_civ(branch)
        if cell == 'wonder':
            civ[cell] = deck[index_no]['file']
        else:
            civ['hand'].append(deck[index_no])

        deck[index_no] = None

    git.write_game(branch, {'deck': deck, 'civ': civ, 'military': git.get_military(branch)}, "add card to hand")
    return index(request, branch)

def undo(request, branch):
    git.undo(branch)
    return index(request, branch)

def begin(request, branch):
    git.create_branch_at_master_head(branch)
    return index(request, branch)

def save(request, branch):
    git.replace_master_with_branch(branch)
    return index(request, 'master')

def reset(request, branch):
    git.delete_branch(branch)
    return index(request, 'master')

def play(request, branch, index_no):
    index_no = int(index_no) - 1
    civ = git.get_civ(branch)

    card = civ['hand'][index_no]
    civ[card['cell']] = {}
    civ[card['cell']]['file'] = card['file']
    civ[card['cell']]['blue'] = 0
    civ[card['cell']]['yellow'] = 0

    civ['hand'].pop(index_no)
    git.write_civ(branch, civ, str("Play card " + card['cell']))

    return index(request, branch)

def play_event(request, branch, index_no):
    index_no = int(index_no) - 1
    civ = git.get_civ(branch)
    military = git.get_military(branch)

    card = civ['hand'][index_no]
    civ['hand'].pop(index_no)

    military['future'][card['deck']].append(card)

    git.write_game(branch, {'deck': git.get_deck(branch), 'civ': civ, 'military': military}, str("Play event " + card['deck']))

    return index(request, branch)

def count_up(request, branch, type):
    civ = git.get_civ(branch)
    civ[type + '_tokens'] += 1
    git.write_civ(branch, civ, str(type + " up"))
    return index(request, branch)

def count_down(request, branch, type):
    civ = git.get_civ(branch)
    civ[type + '_tokens'] -= 1
    civ[type + '_tokens'] = max(civ[type + '_tokens'], 0)
    git.write_civ(branch, civ, str(type + " down"))
    return index(request, branch)

def points_up(request, branch, category):
    civ = git.get_civ(branch)
    civ[category] += 1
    git.write_civ(branch, civ, str(category + " up"))
    return index(request, branch)

def points_down(request, branch, category):
    civ = git.get_civ(branch)
    civ[category] -= 1
    civ[category] = max(civ[category], 0)
    git.write_civ(branch, civ, str(category + " down"))
    return index(request, branch)

def yellow_up(request, branch, cell):
    civ = git.get_civ(branch)
    civ[cell]['yellow'] += 1
    git.write_civ(branch, civ, str("yellow up " + cell))
    return index(request, branch)

def yellow_down(request, branch, cell):
    civ = git.get_civ(branch)
    civ[cell]['yellow'] -= 1
    civ[cell]['yellow'] = max(civ[cell]['yellow'], 0)
    git.write_civ(branch, civ, str("yellow down " + cell))
    return index(request, branch)

def blue_cell_up(request, branch, cell):
    civ = git.get_civ(branch)
    civ[cell]['blue'] += 1
    git.write_civ(branch, civ, str("blue up " + cell))
    return index(request, branch)

def blue_cell_down(request, branch, cell):
    civ = git.get_civ(branch)
    civ[cell]['blue'] -= 1
    civ[cell]['blue'] = max(civ[cell]['blue'], 0)
    git.write_civ(branch, civ, str("blue down " + cell))
    return index(request, branch)

def draw_military(request, branch, deck):
    military = git.get_military(branch)
    card = military[deck].pop()
    
    civ = git.get_civ(branch)
    civ['hand'].append(card)

    git.write_game(branch, {'deck': git.get_deck(branch), 'civ': civ, 'military': military}, "Drawing military")
    return index(request, branch)
    

# def remove_card(request, index_no):
#     index_no = int(index_no) - 1
#     layout = get_layout()
#     if layout[index_no]:
#         layout[index_no].delete()
#         layout[index_no] = None
#     return index(request)

# def get_layout():
#     board = Board.objects.all()
#     card_hash = {}
#     for card in board:
#         card_hash[card.spot] = card

#     layout = [ None for _ in range(13) ]
#     print card_hash.keys()
#     for index in card_hash.keys():
#         layout[index] = card_hash[index]

#     return layout

# def fill_board(layout):
#     first = layout[0]
#     if first:
#         first.delete()
#     layout[0] = None
#     layout = [ x for x in layout if x ]
#     for index in range(len(layout), 13):
#         layout.append(new_card(index))

#     for index, card in enumerate(layout):
#         if not card: continue
#         card.spot = index
#         card.save()

# def new_card(index):
#     deck = list(Deck.objects.all().order_by('rank'))
#     if not deck: return None

#     card = deck[0]
#     card_obj = card.card
#     card.delete()
#     board = Board(card=card_obj, spot=index)
#     board.save()
#     return board
