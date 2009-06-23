from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from tta.game.models import LoginForm, Game
from game.git import Git as g

def index(request, game, branch, player):
    git = g(Game.objects.get(id=game).directory)
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
            'request': request,
            'user_id': request.user.id,
            'player': player,
            'card_row': [ x['file'] for x in card_row ],
            'branch': branch,
            'civ': my_civ,
            'scores': scores,
            'military': military,
            'blue': dict([ (str(x+1),1) for x in range(min(my_civ['blue_tokens'], 18)) ]),
            'blue_leftover': max(my_civ['blue_tokens'] - 18, 0),
            'yellow': dict([ (str(x+1),1) for x in range(min(my_civ['yellow_tokens'], 18)) ]),
            'can_view_hand': request.user.username == player,
            'login_form': LoginForm(),
            'game': game
            })

def slide(request, game, branch, player):
    git = g(Game.objects.get(id=game).directory)
    deck = git.get_deck(branch)
    first = deck[0]
    if first:
        deck.pop(0)
    
    deck = [ x for x in deck if x ]
    git.write_deck(branch, deck, "slide")

    return HttpResponseRedirect("/" + game + "/" + branch + "/" + player + "/card_row")

def add_to_hand(request, game, branch, player, index_no):
    git = g(Game.objects.get(id=game).directory)
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
    return HttpResponseRedirect("/" + game + "/" + branch + "/" + player + "/card_row")

def undo(request, game, branch, player):
    git = g(Game.objects.get(id=game).directory)
    git.undo(branch)
    return HttpResponseRedirect("/" + game + "/" + branch + "/" + player + "/card_row")

def begin(request, game, branch, player):
    git = g(Game.objects.get(id=game).directory)
    git.create_branch_at_master_head(branch)
    return HttpResponseRedirect("/" + game + "/" + branch + "/" + player + "/card_row")

def save(request, game, branch, player):
    git = g(Game.objects.get(id=game).directory)
    git.replace_master_with_branch(branch)
    return HttpResponseRedirect("/" + game + "/master/" + player + "/card_row")

def reset(request, game, branch, player):
    git = g(Game.objects.get(id=game).directory)
    git.delete_branch(branch)
    return HttpResponseRedirect("/" + game + "/master/" + player + "/card_row")

def play(request, game, branch, player, index_no):
    git = g(Game.objects.get(id=game).directory)
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

    return HttpResponseRedirect("/" + game + "/" + branch + "/" + player + "/card_row")

def discard(request, game, branch, player, index_no):
    git = g(Game.objects.get(id=game).directory)
    index_no = int(index_no) - 1
    civ = git.get_civ(branch)
    card = civ[player]['hand'].pop(index_no)

    git.write_civ(branch, civ, str("Discard card " + card['cell']))

    return HttpResponseRedirect("/" + game + "/" + branch + "/" + player + "/card_row")

def discard_leader(request, game, branch, player):
    git = g(Game.objects.get(id=game).directory)
    civ = git.get_civ(branch)
    card = civ[player]['leader'] = None

    git.write_civ(branch, civ, "Discard Leader")

    return HttpResponseRedirect("/" + game + "/" + branch + "/" + player + "/card_row")

def play_event(request, game, branch, player, index_no):
    git = g(Game.objects.get(id=game).directory)
    index_no = int(index_no) - 1
    civ = git.get_civ(branch)
    my_civ = civ[player]
    military = git.get_military(branch)

    card = my_civ['hand'][index_no]
    my_civ['hand'].pop(index_no)

    military['future'][card['deck']].append(card)

    civ[player] = my_civ
    git.write_game(branch, {'deck': git.get_deck(branch), 'civ': civ, 'military': military}, str("Play event " + card['deck']))

    return HttpResponseRedirect("/" + game + "/" + branch + "/" + player + "/card_row")

def play_aggression(request, game, branch, player, index_no):
    git = g(Game.objects.get(id=game).directory)
    index_no = int(index_no) - 1
    civ = git.get_civ(branch)
    my_civ = civ[player]
    military = git.get_military(branch)

    card = my_civ['hand'][index_no]
    my_civ['hand'].pop(index_no)

    military['aggressions'].append(card)

    civ[player] = my_civ
    git.write_game(branch, {'deck': git.get_deck(branch), 'civ': civ, 'military': military}, str("Play aggression " + card['deck']))

    return HttpResponseRedirect("/" + game + "/" + branch + "/" + player + "/card_row")

def play_pact(request, game, branch, player, index_no):
    git = g(Game.objects.get(id=game).directory)
    index_no = int(index_no) - 1
    civ = git.get_civ(branch)
    my_civ = civ[player]
    military = git.get_military(branch)

    card = my_civ['hand'][index_no]
    my_civ['hand'].pop(index_no)

    military['pacts'].append(card)

    civ[player] = my_civ
    git.write_game(branch, {'deck': git.get_deck(branch), 'civ': civ, 'military': military}, str("Play pact " + card['deck']))

    return HttpResponseRedirect("/" + game + "/" + branch + "/" + player + "/card_row")

def remove_aggression(request, game, branch, player, index_no):
    git = g(Game.objects.get(id=game).directory)
    index_no = int(index_no)
    military = git.get_military(branch)
    military['aggressions'].pop(index_no)

    git.write_game(branch, {'deck': git.get_deck(branch), 'civ': git.get_civ(branch), 'military': military}, "Remove aggression")
    return HttpResponseRedirect("/" + game + "/" + branch + "/" + player + "/card_row")

def remove_pact(request, game, branch, player, index_no):
    git = g(Game.objects.get(id=game).directory)
    index_no = int(index_no)
    military = git.get_military(branch)
    military['pacts'].pop(index_no)

    git.write_game(branch, {'deck': git.get_deck(branch), 'civ': git.get_civ(branch), 'military': military}, "Remove pact")
    return HttpResponseRedirect("/" + game + "/" + branch + "/" + player + "/card_row")

def take_territory(request, game, branch, player):
    git = g(Game.objects.get(id=game).directory)
    military = git.get_military(branch)
    card = military['current_event']
    military['current_event'] = None

    civ = git.get_civ(branch)
    civ[player]['territories'].append(card['file'])

    git.write_game(branch, {'deck': git.get_deck(branch), 'civ': civ, 'military': military}, "Take territory")
    return HttpResponseRedirect("/" + game + "/" + branch + "/" + player + "/card_row")

def count_up(request, game, branch, player, type):
    git = g(Game.objects.get(id=game).directory)
    civ = git.get_civ(branch)
    civ[player][type + '_tokens'] += 1
    git.write_civ(branch, civ, str(type + " up"))
    return HttpResponseRedirect("/" + game + "/" + branch + "/" + player + "/card_row")

def count_down(request, game, branch, player, type):
    git = g(Game.objects.get(id=game).directory)
    civ = git.get_civ(branch)
    civ[player][type + '_tokens'] -= 1
    civ[player][type + '_tokens'] = max(civ[player][type + '_tokens'], 0)
    git.write_civ(branch, civ, str(type + " down"))
    return HttpResponseRedirect("/" + game + "/" + branch + "/" + player + "/card_row")

def points_up(request, game, branch, player, category):
    git = g(Game.objects.get(id=game).directory)
    civ = git.get_civ(branch)
    civ[player][category] += 1
    git.write_civ(branch, civ, str(category + " up"))
    return HttpResponseRedirect("/" + game + "/" + branch + "/" + player + "/card_row")

def points_down(request, game, branch, player, category):
    git = g(Game.objects.get(id=game).directory)
    civ = git.get_civ(branch)
    civ[player][category] -= 1
    civ[player][category] = max(civ[player][category], 0)
    git.write_civ(branch, civ, str(category + " down"))
    return HttpResponseRedirect("/" + game + "/" + branch + "/" + player + "/card_row")

def yellow_up(request, game, branch, player, cell):
    git = g(Game.objects.get(id=game).directory)
    civ = git.get_civ(branch)
    civ[player][cell]['yellow'] += 1
    git.write_civ(branch, civ, str("yellow up " + cell))
    return points_down(request, game, branch, player, 'unused_workers')

def yellow_down(request, game, branch, player, cell):
    git = g(Game.objects.get(id=game).directory)
    civ = git.get_civ(branch)
    civ[player][cell]['yellow'] -= 1
    civ[player][cell]['yellow'] = max(civ[player][cell]['yellow'], 0)
    git.write_civ(branch, civ, str("yellow down " + cell))
    return points_up(request, game, branch, player, 'unused_workers')

def blue_cell_up(request, game, branch, player, cell):
    git = g(Game.objects.get(id=game).directory)
    civ = git.get_civ(branch)
    civ[player][cell]['blue'] += 1
    git.write_civ(branch, civ, str("blue up " + cell))
    return count_down(request, game, branch, player, 'blue')

def blue_cell_down(request, game, branch, player, cell):
    git = g(Game.objects.get(id=game).directory)
    civ = git.get_civ(branch)
    civ[player][cell]['blue'] -= 1
    civ[player][cell]['blue'] = max(civ[player][cell]['blue'], 0)
    git.write_civ(branch, civ, str("blue down " + cell))
    return count_up(request, game, branch, player, 'blue')

def draw_military(request, game, branch, player, deck):
    git = g(Game.objects.get(id=game).directory)
    military = git.get_military(branch)
    card = military[deck].pop()
    
    civ = git.get_civ(branch)
    civ[player]['hand'].append(card)

    git.write_game(branch, {'deck': git.get_deck(branch), 'civ': civ, 'military': military}, str("Drawing military (deck: " + deck + ")"))
    return HttpResponseRedirect("/" + game + "/" + branch + "/" + player + "/card_row")

def pop_current_event(request, game, branch, player):
    git = g(Game.objects.get(id=game).directory)
    military = git.get_military(branch)
    if len(military['current']) == 0:
        return shuffle_future_events(request, branch, player)

    card = military['current'].pop()
    military['current_event'] = card

    git.write_game(branch, {'deck': git.get_deck(branch), 'civ': git.get_civ(branch), 'military': military}, "Current Event!")
    return HttpResponseRedirect("/" + game + "/" + branch + "/" + player + "/card_row")

def finish_wonder(request, game, branch, player):
    git = g(Game.objects.get(id=game).directory)
    civ = git.get_civ(branch)
    my_civ = civ[player]
    wonder = my_civ['wonder']
    my_civ['wonder'] = None
    my_civ['completed_wonders'].append(wonder['file'])
    civ[player] = my_civ
    git.write_game(branch, {'deck': git.get_deck(branch), 'civ': civ, 'military': git.get_military(branch)}, "finish wonder")
    return HttpResponseRedirect("/" + game + "/" + branch + "/" + player + "/card_row")

def shuffle_future_events(request, game, branch, player):
    git = g(Game.objects.get(id=game).directory)
    military = git.get_military(branch)

    shuffled = git.shuffle(military['future']['III']) + git.shuffle(military['future']['II']) + git.shuffle(military['future']['I']) + git.shuffle(military['future']['A'])
    military['future']['A'] = []
    military['future']['I'] = []
    military['future']['II'] = []
    military['future']['III'] = []
    military['current'] = shuffled

    git.write_game(branch, {'deck': git.get_deck(branch), 'civ': git.get_civ(branch), 'military': military}, "Shuffle Future Events")
    return HttpResponseRedirect("/" + game + "/" + branch + "/" + player + "/card_row")

from tta.game.models import Heartbeat
from django.utils import simplejson
import datetime

def heartbeat(request, game, branch, user_id):
    beat = Heartbeat(user_id=user_id)
    beat.save()
    active_users = [ x.user.username for x in Heartbeat.objects.filter(last_login__gt=datetime.datetime.now() - datetime.timedelta(0,60)) ]

    json = simplejson.dumps(active_users)
    return HttpResponse(json, mimetype='application/json')

from django.contrib.auth import authenticate, login as login_user
from django.shortcuts import render_to_response
def login(request, game, branch, player):
    def errorHandle(error):
        form = LoginForm()
        return render_to_response('login.html', {
                'error' : error,
                'form' : form,
                })
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    # Redirect to a success page.
                    login_user(request, user)
                    return HttpResponseRedirect("/" + game + "/" + branch + "/" + player + "/card_row")
                else:
                    # Return a 'disabled account' error message
                    error = u'account disabled'
                    return errorHandle(error)
            else:
                # Return an 'invalid login' error message.
                error = u'invalid login'
                return errorHandle(error)
        else:
            error = u'form is invalid'
            return errorHandle(error)
    else:
        form = LoginForm() # An unbound form
        return render_to_response('login.html', {
                'form': form,
                })

from django.contrib.auth import logout as logout_user
def logout(request, game, branch, player):
    logout_user(request)
    return HttpResponseRedirect("/" + game + "/" + branch + "/" + player + "/card_row")

from django.contrib.auth.models import User
import urllib, hashlib
def profile(request, user_id):
    user = User.objects.get(id=user_id)
    email = user.email
    size = 80

    gravatar_url = "http://www.gravatar.com/avatar.php?"
    gravatar_url += urllib.urlencode({'gravatar_id':hashlib.md5(email).hexdigest(),
                                      'size':str(size)})
    return render_to_response('game/profile.html', {
            'request': request,
            'user': user,
            'gravatar_url': gravatar_url,
            'login_form': LoginForm(),
            'games': [],
            });
