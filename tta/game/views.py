from django.shortcuts import render_to_response
from game.models import Board, Deck

from game import git

def index(request, branch):
    card_row = git.get_deck(branch)[:13]

    for index in range(len(card_row), 13):
        card_row.append("Blank.png")
    card_row = [ x and x or "Blank.png" for x in card_row ]
    print card_row
    return render_to_response('game/index.html', {'card_row': card_row, 'branch': branch})

def slide(request, branch):
    deck = git.get_deck(branch)
    first = deck[0]
    if first:
        deck.pop(0)
    
    deck = [ x for x in deck if x ]
    git.write_deck(branch, deck)

    return index(request, branch)

def remove(request, branch, index_no):
    index_no = int(index_no) - 1
    deck = git.get_deck(branch)
    if deck[index_no]:
        deck[index_no] = None
    git.write_deck(branch, deck)
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
