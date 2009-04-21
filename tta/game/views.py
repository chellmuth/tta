from django.shortcuts import render_to_response
from game.models import Board, Deck
from django.http import HttpResponseRedirect

from game import git

def index(request, branch, player):
    card_row = git.get_deck(branch)[:13]
    civ = git.get_civ(branch)
    my_civ = civ[player]

    for index in range(len(card_row), 13):
        card_row.append({'file': "Blank.png"})
    card_row = [ x and x or {'file': "Blank.png"} for x in card_row ]

    scores = []
    for name in sorted(civ.keys()):
        score = {}
        score['name'] = name
        score['culture'] = civ[name]['culture']
        score['culture_plus'] = civ[name]['culture_plus']
        score['tech'] = civ[name]['tech']
        score['tech_plus'] = civ[name]['tech_plus']
        score['strength'] = civ[name]['strength']
        scores.append(score)

    military = git.get_military(branch)
    military['future_event_size'] = sum([len(military['future'][x]) for x in military['future'].keys()])
    return render_to_response('game/index.html', {
            'player': player,
            'card_row': [ x['file'] for x in card_row ],
            'branch': branch,
            'civ': my_civ,
            'scores': scores,
            'military': military,
            'blue': dict([ (str(x+1),1) for x in range(min(my_civ['blue_tokens'], 18)) ]),
            'blue_leftover': max(my_civ['blue_tokens'] - 18, 0),
            'yellow': dict([ (str(x+1),1) for x in range(min(my_civ['yellow_tokens'], 18)) ]),
            })

def slide(request, branch, player):
    deck = git.get_deck(branch)
    first = deck[0]
    if first:
        deck.pop(0)
    
    deck = [ x for x in deck if x ]
    git.write_deck(branch, deck, "slide")

    return HttpResponseRedirect("/" + branch + "/" + player + "/card_row")

def add_to_hand(request, branch, player, index_no):
    index_no = int(index_no) - 1
    deck = git.get_deck(branch)

    if deck[index_no]:
        cell = deck[index_no]['cell']
        civ = git.get_civ(branch)
        my_civ = civ[player]
        if cell == 'wonder':
            my_civ['wonder'] = { 'file': deck[index_no]['file'], 'blue': 0 }
        else:
            my_civ['hand'].append(deck[index_no])
        civ[player] = my_civ    

        deck[index_no] = None

    git.write_game(branch, {'deck': deck, 'civ': civ, 'military': git.get_military(branch)}, "add card to hand")
    return HttpResponseRedirect("/" + branch + "/" + player + "/card_row")

def undo(request, branch, player):
    git.undo(branch)
    return HttpResponseRedirect("/" + branch + "/" + player + "/card_row")

def begin(request, branch, player):
    git.create_branch_at_master_head(branch)
    return HttpResponseRedirect("/" + branch + "/" + player + "/card_row")

def save(request, branch, player):
    git.replace_master_with_branch(branch)
    return HttpResponseRedirect("/master/" + player + "/card_row")

def reset(request, branch, player):
    git.delete_branch(branch)
    return HttpResponseRedirect("/master/" + player + "/card_row")

def play(request, branch, player, index_no):
    index_no = int(index_no) - 1
    civ = git.get_civ(branch)
    my_civ = civ[player]

    card = my_civ['hand'][index_no]
    my_civ[card['cell']] = {}
    my_civ[card['cell']]['file'] = card['file']
    my_civ[card['cell']]['blue'] = 0
    my_civ[card['cell']]['yellow'] = 0

    my_civ['hand'].pop(index_no)

    civ[player] = my_civ
    git.write_civ(branch, civ, str("Play card " + card['cell']))

    return HttpResponseRedirect("/" + branch + "/" + player + "/card_row")

def play_event(request, branch, player, index_no):
    index_no = int(index_no) - 1
    civ = git.get_civ(branch)
    my_civ = civ[player]
    military = git.get_military(branch)

    card = my_civ['hand'][index_no]
    my_civ['hand'].pop(index_no)

    military['future'][card['deck']].append(card)

    civ[player] = my_civ
    git.write_game(branch, {'deck': git.get_deck(branch), 'civ': civ, 'military': military}, str("Play event " + card['deck']))

    return HttpResponseRedirect("/" + branch + "/" + player + "/card_row")

def play_aggression(request, branch, player, index_no):
    index_no = int(index_no) - 1
    civ = git.get_civ(branch)
    my_civ = civ[player]
    military = git.get_military(branch)

    card = my_civ['hand'][index_no]
    my_civ['hand'].pop(index_no)

    military['aggressions'].append(card)

    civ[player] = my_civ
    git.write_game(branch, {'deck': git.get_deck(branch), 'civ': civ, 'military': military}, str("Play event " + card['deck']))

    return HttpResponseRedirect("/" + branch + "/" + player + "/card_row")

def remove_aggression(request, branch, player, index_no):
    index_no = int(index_no)
    military = git.get_military(branch)
    military['aggressions'].pop(index_no)

    git.write_game(branch, {'deck': git.get_deck(branch), 'civ': git.get_civ(branch), 'military': military}, "Remove aggression")
    return HttpResponseRedirect("/" + branch + "/" + player + "/card_row")

def count_up(request, branch, player, type):
    civ = git.get_civ(branch)
    civ[player][type + '_tokens'] += 1
    git.write_civ(branch, civ, str(type + " up"))
    return HttpResponseRedirect("/" + branch + "/" + player + "/card_row")

def count_down(request, branch, player, type):
    civ = git.get_civ(branch)
    civ[player][type + '_tokens'] -= 1
    civ[player][type + '_tokens'] = max(civ[player][type + '_tokens'], 0)
    git.write_civ(branch, civ, str(type + " down"))
    return HttpResponseRedirect("/" + branch + "/" + player + "/card_row")

def points_up(request, branch, player, category):
    civ = git.get_civ(branch)
    civ[player][category] += 1
    git.write_civ(branch, civ, str(category + " up"))
    return HttpResponseRedirect("/" + branch + "/" + player + "/card_row")

def points_down(request, branch, player, category):
    civ = git.get_civ(branch)
    civ[player][category] -= 1
    civ[player][category] = max(civ[player][category], 0)
    git.write_civ(branch, civ, str(category + " down"))
    return HttpResponseRedirect("/" + branch + "/" + player + "/card_row")

def yellow_up(request, branch, player, cell):
    civ = git.get_civ(branch)
    civ[player][cell]['yellow'] += 1
    git.write_civ(branch, civ, str("yellow up " + cell))
    return HttpResponseRedirect("/" + branch + "/" + player + "/card_row")

def yellow_down(request, branch, player, cell):
    civ = git.get_civ(branch)
    civ[player][cell]['yellow'] -= 1
    civ[player][cell]['yellow'] = max(civ[player][cell]['yellow'], 0)
    git.write_civ(branch, civ, str("yellow down " + cell))
    return HttpResponseRedirect("/" + branch + "/" + player + "/card_row")

def blue_cell_up(request, branch, player, cell):
    civ = git.get_civ(branch)
    civ[player][cell]['blue'] += 1
    git.write_civ(branch, civ, str("blue up " + cell))
    return HttpResponseRedirect("/" + branch + "/" + player + "/card_row")

def blue_cell_down(request, branch, player, cell):
    civ = git.get_civ(branch)
    civ[player][cell]['blue'] -= 1
    civ[player][cell]['blue'] = max(civ[player][cell]['blue'], 0)
    git.write_civ(branch, civ, str("blue down " + cell))
    return HttpResponseRedirect("/" + branch + "/" + player + "/card_row")

def draw_military(request, branch, player, deck):
    military = git.get_military(branch)
    card = military[deck].pop()
    
    civ = git.get_civ(branch)
    civ[player]['hand'].append(card)

    git.write_game(branch, {'deck': git.get_deck(branch), 'civ': civ, 'military': military}, "Drawing military")
    return HttpResponseRedirect("/" + branch + "/" + player + "/card_row")

def pop_current_event(request, branch, player):
    military = git.get_military(branch)
    if len(military['current']) == 0:
        return shuffle_future_events(request, branch, player)

    card = military['current'].pop()
    military['current_event'] = card['file']

    git.write_game(branch, {'deck': git.get_deck(branch), 'civ': git.get_civ(branch), 'military': military}, "Current Event!")
    return HttpResponseRedirect("/" + branch + "/" + player + "/card_row")

def finish_wonder(request, branch, player):
    civ = git.get_civ(branch)
    my_civ = civ[player]
    wonder = my_civ['wonder']
    my_civ['wonder'] = None
    my_civ['completed_wonders'].append(wonder['file'])
    civ[player] = my_civ
    git.write_game(branch, {'deck': git.get_deck(branch), 'civ': civ, 'military': git.get_military(branch)}, "finish wonder")
    return HttpResponseRedirect("/" + branch + "/" + player + "/card_row")

def shuffle_future_events(request, branch, player):
    military = git.get_military(branch)

    shuffled = git.shuffle(military['future']['III']) + git.shuffle(military['future']['II']) + git.shuffle(military['future']['I']) + git.shuffle(military['future']['A'])
    military['future']['A'] = []
    military['future']['I'] = []
    military['future']['II'] = []
    military['future']['III'] = []
    military['current'] = shuffled

    git.write_game(branch, {'deck': git.get_deck(branch), 'civ': git.get_civ(branch), 'military': military}, "Shuffle Future Events")
    return HttpResponseRedirect("/" + branch + "/" + player + "/card_row")
