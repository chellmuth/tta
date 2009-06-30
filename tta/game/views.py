from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from tta.game.models import LoginForm, Game
from game.git import Git as g

def home(request):
    return render_to_response('home.html', {
            'request': request,
            'login_form': LoginForm()
            })

def civ_for_player(civs, player):
    for i, civ in enumerate(civs):
        if civ['user'] == int(player):
            return (civ,i)

def index(request, game, branch, player):
    git = g(Game.objects.get(id=game).directory)
    card_row = git.get_deck(branch)[:13]
    civs = git.get_civ(branch)
    (my_civ,index) = civ_for_player(civs, player)

    for index in range(len(card_row), 13):
        card_row.append({'file': "Blank.png"})
    card_row = [ x and x or {'file': "Blank.png"} for x in card_row ]

    military = git.get_military(branch)
    military['future_event_size'] = sum([len(military['future'][x]) for x in military['future'].keys()])

    for civ in civs:
        civ['yellow'] = dict((str(x+1),1) for x in range(min(civ['yellow_tokens'], 18)))
        civ['blue'] = dict((str(x+1),1) for x in range(min(civ['blue_tokens'], 18)))
        civ['blue_leftover'] = max(civ['blue_tokens'] - 18, 0)

    return render_to_response('game/index.html', {
            'request': request,
            'user_id': request.user.id,
            'player': player,
            'card_row': [ x['file'] for x in card_row ],
            'branch': branch,
            'civs': civs,
            'military': military,
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
        civs = git.get_civ(branch)
        (my_civ,index) = civ_for_player(civs, player)

        if cell == 'wonder':
            my_civ['wonder'] = { 'file': deck[index_no]['file'], 'blue': 0 }
        else:
            my_civ['hand'].append(deck[index_no])
        civs[index] = my_civ    

        deck[index_no] = None

    git.write_game(branch, {'deck': deck, 'civ': civs, 'military': git.get_military(branch)}, "add card to hand")
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
    civs = git.get_civ(branch)
    (my_civ,index) = civ_for_player(civs, player)

    card = my_civ['hand'][index_no]
    my_civ[card['cell']] = {}
    my_civ[card['cell']]['file'] = card['file']
    my_civ[card['cell']]['blue'] = 0
    my_civ[card['cell']]['yellow'] = 0

    my_civ['hand'].pop(index_no)

    civs[index] = my_civ
    git.write_civ(branch, civs, str("Play card " + card['cell']))

    return HttpResponseRedirect("/" + game + "/" + branch + "/" + player + "/card_row")

def discard(request, game, branch, player, index_no):
    git = g(Game.objects.get(id=game).directory)
    index_no = int(index_no) - 1
    civs = git.get_civ(branch)
    (my_civ,index) = civ_for_player(civs, player)
    card = civs[index]['hand'].pop(index_no)

    git.write_civ(branch, civs, str("Discard card " + card['cell']))

    return HttpResponseRedirect("/" + game + "/" + branch + "/" + player + "/card_row")

def discard_leader(request, game, branch, player):
    git = g(Game.objects.get(id=game).directory)
    civs = git.get_civ(branch)
    (my_civ,index) = civ_for_player(civs, player)
    card = civs[index]['leader'] = None

    git.write_civ(branch, civs, "Discard Leader")

    return HttpResponseRedirect("/" + game + "/" + branch + "/" + player + "/card_row")

def play_event(request, game, branch, player, index_no):
    git = g(Game.objects.get(id=game).directory)
    index_no = int(index_no) - 1
    civs = git.get_civ(branch)
    (my_civ,index) = civ_for_player(civs, player)
    my_civ = civs[index]
    military = git.get_military(branch)

    card = my_civ['hand'][index_no]
    my_civ['hand'].pop(index_no)

    military['future'][card['deck']].append(card)

    civs[index] = my_civ
    git.write_game(branch, {'deck': git.get_deck(branch), 'civ': civs, 'military': military}, str("Play event " + card['deck']))

    return HttpResponseRedirect("/" + game + "/" + branch + "/" + player + "/card_row")

def play_aggression(request, game, branch, player, index_no):
    git = g(Game.objects.get(id=game).directory)
    index_no = int(index_no) - 1
    civs = git.get_civ(branch)
    (my_civ,index) = civ_for_player(civs, player)
    my_civ = civs[index]
    military = git.get_military(branch)

    card = my_civ['hand'][index_no]
    my_civ['hand'].pop(index_no)

    military['aggressions'].append(card)

    civs[index] = my_civ
    git.write_game(branch, {'deck': git.get_deck(branch), 'civ': civs, 'military': military}, str("Play aggression " + card['deck']))

    return HttpResponseRedirect("/" + game + "/" + branch + "/" + player + "/card_row")

def play_pact(request, game, branch, player, index_no):
    git = g(Game.objects.get(id=game).directory)
    index_no = int(index_no) - 1
    civs = git.get_civ(branch)
    (my_civ,index) = civ_for_player(civs, player)
    my_civ = civs[index]
    military = git.get_military(branch)

    card = my_civ['hand'][index_no]
    my_civ['hand'].pop(index_no)

    military['pacts'].append(card)

    civs[index] = my_civ
    git.write_game(branch, {'deck': git.get_deck(branch), 'civ': civs, 'military': military}, str("Play pact " + card['deck']))

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

    civs = git.get_civ(branch)
    (my_civ,index) = civ_for_player(civs, player)
    civs[index]['territories'].append(card['file'])

    git.write_game(branch, {'deck': git.get_deck(branch), 'civ': civs, 'military': military}, "Take territory")
    return HttpResponseRedirect("/" + game + "/" + branch + "/" + player + "/card_row")

def count_up(request, game, branch, player, type):
    git = g(Game.objects.get(id=game).directory)
    civs = git.get_civ(branch)
    (my_civ,index) = civ_for_player(civs, player)
    civs[index][type + '_tokens'] += 1
    git.write_civ(branch, civs, str(type + " up"))
    return HttpResponseRedirect("/" + game + "/" + branch + "/" + player + "/card_row")

def count_down(request, game, branch, player, type):
    git = g(Game.objects.get(id=game).directory)
    civs = git.get_civ(branch)
    (my_civ,index) = civ_for_player(civs, player)
    civs[index][type + '_tokens'] -= 1
    civs[index][type + '_tokens'] = max(civs[index][type + '_tokens'], 0)
    git.write_civ(branch, civs, str(type + " down"))
    return HttpResponseRedirect("/" + game + "/" + branch + "/" + player + "/card_row")

def points_up(request, game, branch, player, category):
    git = g(Game.objects.get(id=game).directory)
    civs = git.get_civ(branch)
    (my_civ,index) = civ_for_player(civs, player)
    civs[index][category] += 1
    git.write_civ(branch, civs, str(category + " up"))
    return HttpResponseRedirect("/" + game + "/" + branch + "/" + player + "/card_row")

def points_down(request, game, branch, player, category):
    git = g(Game.objects.get(id=game).directory)
    civs = git.get_civ(branch)
    (my_civ,index) = civ_for_player(civs, player)
    civs[index][category] -= 1
    civs[index][category] = max(civs[index][category], 0)
    git.write_civ(branch, civs, str(category + " down"))
    return HttpResponseRedirect("/" + game + "/" + branch + "/" + player + "/card_row")

def yellow_up(request, game, branch, player, cell):
    git = g(Game.objects.get(id=game).directory)
    civs = git.get_civ(branch)
    (my_civ,index) = civ_for_player(civs, player)
    civs[index][cell]['yellow'] += 1
    git.write_civ(branch, civs, str("yellow up " + cell))
    return points_down(request, game, branch, player, 'unused_workers')

def yellow_down(request, game, branch, player, cell):
    git = g(Game.objects.get(id=game).directory)
    civs = git.get_civ(branch)
    (my_civ,index) = civ_for_player(civs, player)
    civs[index][cell]['yellow'] -= 1
    civs[index][cell]['yellow'] = max(civs[index][cell]['yellow'], 0)
    git.write_civ(branch, civs, str("yellow down " + cell))
    return points_up(request, game, branch, player, 'unused_workers')

def blue_cell_up(request, game, branch, player, cell):
    git = g(Game.objects.get(id=game).directory)
    civs = git.get_civ(branch)
    (my_civ,index) = civ_for_player(civs, player)
    civs[index][cell]['blue'] += 1
    git.write_civ(branch, civs, str("blue up " + cell))
    return count_down(request, game, branch, player, 'blue')

def blue_cell_down(request, game, branch, player, cell):
    git = g(Game.objects.get(id=game).directory)
    civs = git.get_civ(branch)
    (my_civ,index) = civ_for_player(civs, player)
    civs[index][cell]['blue'] -= 1
    civs[index][cell]['blue'] = max(civs[index][cell]['blue'], 0)
    git.write_civ(branch, civs, str("blue down " + cell))
    return count_up(request, game, branch, player, 'blue')

def draw_military(request, game, branch, player, deck):
    git = g(Game.objects.get(id=game).directory)
    military = git.get_military(branch)
    card = military[deck].pop()
    
    civs = git.get_civ(branch)
    (my_civ,index) = civ_for_player(civs, player)
    civs[index]['hand'].append(card)

    git.write_game(branch, {'deck': git.get_deck(branch), 'civ': civs, 'military': military}, str("Drawing military (deck: " + deck + ")"))
    return HttpResponseRedirect("/" + game + "/" + branch + "/" + player + "/card_row")

def pop_current_event(request, game, branch, player):
    git = g(Game.objects.get(id=game).directory)
    military = git.get_military(branch)
    if len(military['current']) == 0:
        return shuffle_future_events(request, game, branch, player)

    card = military['current'].pop()
    military['current_event'] = card

    git.write_game(branch, {'deck': git.get_deck(branch), 'civ': git.get_civ(branch), 'military': military}, "Current Event!")
    return HttpResponseRedirect("/" + game + "/" + branch + "/" + player + "/card_row")

def finish_wonder(request, game, branch, player):
    git = g(Game.objects.get(id=game).directory)
    civs = git.get_civ(branch)
    (my_civ,index) = civ_for_player(civs, player)
    wonder = my_civ['wonder']
    my_civ['wonder'] = None
    my_civ['completed_wonders'].append(wonder['file'])
    civs[index] = my_civ
    git.write_game(branch, {'deck': git.get_deck(branch), 'civ': civs, 'military': git.get_military(branch)}, "finish wonder")
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
def login(request):
    def errorHandle(error):
        form = LoginForm()
        return render_to_response('account/login.html', {
                'error' : error,
                'next': request.POST.get('next', None),
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
                    next = request.POST.get('next', "/profile/" + str(user.id))
                    return HttpResponseRedirect(next)
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
        return render_to_response('account/login.html', {
                'login_form': form,
                'next': request.GET.get('next', None)
                })

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        if not User.objects.filter(username__iexact=username):
            user = User.objects.create_user(username, email, password)
            user.save()
            user = authenticate(username=username, password=password)
            login_user(request, user)
            next = request.POST.get('next', "/profile/" + str(user.id))
            return HttpResponseRedirect(next)
        return HttpResponseRedirect("/")
    else:
        return render_to_response('register.html', {
                'login_form': LoginForm(),
                'next': request.GET.get('next', None)
                })

from django.contrib.auth import logout as logout_user
def logout(request):
    logout_user(request)
    return HttpResponseRedirect("/")

from django.contrib.auth.models import User
from game.models import GamePlayer
from django.db.models import Q
import urllib, hashlib
def profile(request, user_id):
    user = User.objects.get(id=user_id)
    email = user.email or user.username
    size = 80

    current_games = GamePlayer.objects.filter(user=user.id)
    upcoming_games = OpenGame.objects.filter(Q(player_1=user.id) | Q(player_2=user.id) | Q(player_3=user.id) | Q(player_4=user.id)).exclude(date_started__isnull=False)

    gravatar_url = "http://www.gravatar.com/avatar.php?"
    gravatar_url += urllib.urlencode({'gravatar_id':hashlib.md5(email).hexdigest(),
                                      'size':str(size),
                                      'd':'identicon'})
    return render_to_response('game/profile.html', {
            'request': request,
            'user': user,
            'gravatar_url': gravatar_url,
            'login_form': LoginForm(),
            'current_games': [ g.game for g in current_games ],
            'upcoming_games': upcoming_games,
            'is_logged_in_user': int(user_id) == request.user.id,
            })

from django.contrib.auth.decorators import login_required
from game.models import OpenGameForm
@login_required
def create_game(request):
    if request.method == 'POST':
        form = OpenGameForm(request.POST)
        if form.is_valid():
            ogame = form.save()
            ogame.player_1 = request.user
            ogame.save()
            return HttpResponseRedirect('/open/show/' + str(ogame.id) + '/')
    else:
        form = OpenGameForm()
        return render_to_response('open/create.html', {
                'request': request,
                'login_form': LoginForm(),
                'open_form': form,
                })

@login_required
def start_game(request):
    ogame = OpenGame.objects.get(id=request.POST['game_id'])
    if ogame.date_started:
        return
    if ogame.current_players() not in [2,3,4]:
        return

    ogame.date_started = datetime.datetime.now()
    ogame.save()

    game = Game(directory=hashlib.md5(request.user.username + str(datetime.datetime.now())).hexdigest(),
                title=ogame.title,
                date_started=datetime.datetime.now())
    game.save()

    players = []
    for num in range(1, ogame.current_players() + 1):
        attr = 'player_' + str(num)
        player = getattr(ogame, attr)
        players.append(player)
        gp = GamePlayer(user=player, game=game)
        gp.save()

    git = g(game.directory, {
            'num_players': ogame.current_players(),
            'players': players
            })
    return HttpResponseRedirect("/" + str(game.id) + "/" + "master" + "/" + str(request.user.id) + "/card_row/")

from game.models import OpenGame
def show_game(request, game_id):
    game = OpenGame.objects.get(id=game_id)
    return render_to_response('open/show.html', {
            'request': request,
            'login_form': LoginForm(),
            'game': game
            })

def list_games(request):
    ogames = OpenGame.objects.exclude(date_started__isnull=False)
    return render_to_response('open/list.html', {
            'request': request,
            'login_form': LoginForm(),
            'games': ogames
            })

@login_required
def join_game(request, game_id):
    ogame = OpenGame.objects.get(id=game_id)
    if request.user in [ ogame.player_1, ogame.player_2, ogame.player_3, ogame.player_4]:
        return render_to_response('open/show.html', {
                'request': request,
                'login_form': LoginForm(),
                'game': ogame
                })
    else:
        for num in range(2,ogame.max_players + 1):
            attr =  'player_' + str(num)
            if not getattr(ogame, attr):
                setattr(ogame, attr, request.user)
                ogame.save()
                return render_to_response('open/show.html', {
                        'request': request,
                        'login_form': LoginForm(),
                        'game': ogame
                        })

    return render_to_response('open/show.html', {
            'request': request,
            'login_form': LoginForm(),
            'game': ogame
            })
