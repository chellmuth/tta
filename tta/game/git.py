#!/usr/bin/env python

from django.utils import simplejson

import os
import re
from subprocess import Popen, PIPE
from tta.settings import REPO_ROOT
from game import cards

class Git:
    def __init__(self, dir, committer, init_data={}):
        self.git_dir = REPO_ROOT + dir
        self.committer = committer
        self.log = []

        if not os.path.exists(self.git_dir):
            proc = Popen(('git', 'clone', "--bare", REPO_ROOT + "/root_game", self.git_dir),
                     env = { "GIT_DIR":self.git_dir },
                     stdin = PIPE,
                     stdout = PIPE,
                     stderr = PIPE)

            out, err = proc.communicate()
            self.do_log('Beginning Game')

            self.write_game('master',{'deck':cards.make_shuffled_civil_deck(init_data['num_players']), 'civ':self.make_initial_civ(init_data['players']), 'military': self.make_military()}, 'default-log')

        self.branch = 'master'
        self.deck = self.get_game()['deck']
        self.civs = self.get_game()['civ']
        self.military = self.get_game()['military']

    def do_log(self, msg):
        self.log.append(msg)

    def slide(self):
        first = self.deck[0]
        if first:
            self.deck.pop(0)

        self.deck = [ x for x in self.deck if x ]
        self.do_log("Slide card row")

    def _civ_for_player(self, player):
        for i, civ in enumerate(self.civs):
            if civ['user'] == int(player):
                return (civ,i)

    def add_card_to_hand(self, player, index_no):
        if self.deck[index_no]:
            cell = self.deck[index_no]['cell']
            (my_civ,index) = self._civ_for_player(player)

            if cell == 'wonder':
                my_civ['wonder'] = { 'file': self.deck[index_no]['file'], 'blue': 0, 'name': self.deck[index_no]['name'] }
                self.do_log("Start construction on " + self.deck[index_no]['name'])
            else:
                my_civ['hand'].append(self.deck[index_no])
                self.do_log("Add " + self.deck[index_no]['name'] + " to hand")

            self.civs[index] = my_civ
            self.deck[index_no] = None

    def play_card_from_hand(self, player, index_no):
        (my_civ,index) = self._civ_for_player(player)

        card = my_civ['hand'][index_no]
        my_civ[card['cell']] = {}
        my_civ[card['cell']]['file'] = card['file']
        my_civ[card['cell']]['name'] = card['name']
        my_civ[card['cell']]['blue'] = 0
        my_civ[card['cell']]['yellow'] = 0

        my_civ['hand'].pop(index_no)

        self.civs[index] = my_civ
        self.do_log("Play " + card['name'])

    def discard_from_hand(self, player, index_no):
        (my_civ,index) = self._civ_for_player(player)
        self.civs[index]['hand'].pop(index_no)
        self.do_log("Discard")

    def discard_leader(self, player):
        (my_civ,index) = self._civ_for_player(player)
        self.do_log("Remove " + self.civs[index]['leader']['name'])
        self.civs[index]['leader'] = None

    def play_event(self, player, index_no):
        (my_civ,index) = self._civ_for_player(player)
        my_civ = self.civs[index]

        card = my_civ['hand'][index_no]
        my_civ['hand'].pop(index_no)

        self.military['future'][card['deck']].append(card)
        self.civs[index] = my_civ
        self.do_log("Place an Age " + card['deck'] + " card in the Future Events deck")

    def play_aggression(self, player, index_no):
        (my_civ,index) = self._civ_for_player(player)
        my_civ = self.civs[index]

        card = my_civ['hand'][index_no]
        my_civ['hand'].pop(index_no)

        self.military['aggressions'].append(card)
        self.civs[index] = my_civ
        self.do_log("Play " + card['name'] + "  aggression")

    def play_pact(self, player, index_no):
        (my_civ,index) = self._civ_for_player(player)
        my_civ = self.civs[index]

        card = my_civ['hand'][index_no]
        my_civ['hand'].pop(index_no)

        self.military['pacts'].append(card)
        self.civs[index] = my_civ
        self.do_log("Play " + card['name'] + "  pact")

    def remove_aggression(self, index_no):
        card = self.military['aggressions'].pop(index_no)
        self.do_log("Clear " + card['name'] + " aggression")

    def remove_pact(self, index_no):
        card = self.military['pacts'].pop(index_no)
        self.do_log("Clear " + card['name'] + " pact")

    def claim_territory(self, player):
        card = self.military['current_event']
        self.military['current_event'] = None

        (my_civ,index) = self._civ_for_player(player)
        self.civs[index]['territories'].append(card['file'])
        self.do_log("Claim " + card['name'])

    def tokens_up(self, player, type):
        (my_civ,index) = self._civ_for_player(player)
        self.civs[index][type + '_tokens'] += 1
        self.do_log("Increase " + type + " tokens from " + str(self.civs[index][type + '_tokens'] - 1) + " to " + str(self.civs[index][type + '_tokens'] ))

    def tokens_down(self, player, type):
        (my_civ,index) = self._civ_for_player(player)
        self.civs[index][type + '_tokens'] -= 1
        self.civs[index][type + '_tokens'] = max(self.civs[index][type + '_tokens'], 0)
        self.do_log("Decrease " + type + " bank from " + str(self.civs[index][type + '_tokens'] + 1) + " to " + str(self.civs[index][type + '_tokens'] ))

    def points_up(self, player, category):
        (my_civ,index) = self._civ_for_player(player)
        self.civs[index][category] += 1
        self.do_log("Increase " + category + " from " + str(self.civs[index][category] - 1) + " to " + str(self.civs[index][category]))

    def points_down(self, player, category):
        (my_civ,index) = self._civ_for_player(player)
        self.civs[index][category] -= 1
        self.civs[index][category] = max(self.civs[index][category], 0)
        self.do_log("Decrease " + category + " from " + str(self.civs[index][category] + 1) + " to " + str(self.civs[index][category]))

    def change_card_counter(self, player, cell, color, change):
        (my_civ,index) = self._civ_for_player(player)
        old = self.civs[index][cell][color]
        self.civs[index][cell][color] = change(self.civs[index][cell][color])
        self.civs[index][cell][color] = max(self.civs[index][cell][color], 0)
        new = self.civs[index][cell][color]
        print self.civs[index][cell]
        self.do_log("Update " + self.civs[index][cell]['name'] + "'s " + color + " tokens from " + str(old) + " to " + str(new))

    def draw_military(self, player, deck):
        card = self.military[deck].pop()

        (my_civ,index) = self._civ_for_player(player)
        self.civs[index]['hand'].append(card)
        self.do_log("Draw from Age " + deck + " military deck")

    def _shuffle_future_events(self):
        shuffled = cards.shuffle(self.military['future']['III']) + cards.shuffle(self.military['future']['II']) + cards.shuffle(self.military['future']['I']) + cards.shuffle(self.military['future']['A'])
        self.military['future']['A'] = []
        self.military['future']['I'] = []
        self.military['future']['II'] = []
        self.military['future']['III'] = []
        self.military['current'] = shuffled
        self.do_log("Shuffle Future Events deck into Current Events deck")

    def pop_current_event(self):
        if len(self.military['current']) == 0:
            return self._shuffle_future_events()

        card = self.military['current'].pop()
        self.military['current_event'] = card
        self.do_log("Current Event: " + card['name'])

    def finish_wonder(self, player):
        (my_civ,index) = self._civ_for_player(player)
        wonder = my_civ['wonder']
        my_civ['wonder'] = None
        my_civ['completed_wonders'].append(wonder['file'])
        self.civs[index] = my_civ
        self.do_log("Complete " + wonder['name'])

    def _log_class_for_player(self, player):
        for i, civ in enumerate(self.civs):
            if civ['user'] == int(player):
                return 'p' + str(i + 1) + '-log'
        return 'default-log'

    def save(self, msg):
        self.write_game(self.branch, {'deck': self.deck, 'military': self.military, 'civ': self.civs}, msg, self._log_class_for_player(self.committer))

    def make_military(self):
        age_a, age_I, age_II, age_III = cards.make_military_decks()
        return {
            'future': { 'A' : [], 'I': [], 'II': [], 'III': [] },
            'current': age_a,
            'current_event': None,
            'A':       [],
            'I':       age_I,
            'II':      age_II,
            'III':     age_III,
            'aggressions': [],
            'pacts': [],
            'log': []
            }

    def make_initial_civ(self, players):
        def add_and_return(d, item, value):
            copy = d.copy()
            copy[item] = value
            return copy

        civ = { 'government':  { 'name': 'Despotism', 'file': 'Despotism.png',   'blue': 0, 'yellow': 0 },
                'philosophy':  { 'name': 'Philosophy', 'file': 'Philosophy.png',  'blue': 0, 'yellow': 1 },
                'religion':    { 'name': 'Religion', 'file': 'Religion.png',    'blue': 0, 'yellow': 0 },
                'bronze':      { 'name': 'Bronze', 'file': 'Bronze.png',      'blue': 0, 'yellow': 2 },
                'agriculture': { 'name': 'Agriculture', 'file': 'Agriculture.png', 'blue': 0, 'yellow': 2 },
                'warriors':    { 'name': 'Warriors', 'file': 'Warriors.png',    'blue': 0, 'yellow': 1 },
                'hand': [],
                'completed_wonders': [],
                'territories': [],
                'unused_workers': 1,
                'yellow_tokens': 18,
                'culture': 0,
                'culture_plus': 0,
                'tech': 0,
                'tech_plus': 1,
                'strength': 1,
                'happiness': 0,
                'blue_tokens': 18}

        civs = []
        for user in players:
            their_civ = civ.copy()
            their_civ['user'] = user.id
            their_civ['name'] = user.username
            civs.append(their_civ)

        return civs

    def undo(self, branch):
        proc = Popen(('git', 'update-ref', "refs/heads/" + branch, branch + '~1'),
                     env = { "GIT_DIR":self.git_dir },
                     stdin = PIPE,
                     stdout = PIPE,
                     stderr = PIPE)

        out, err = proc.communicate()

    def serialize_object(self, object):
        serialized = simplejson.dumps(object, sort_keys=True, indent=3)
#         print serialized
        return serialized

    def write_game(self, branch, game, commit_msg="DEFAULT COMMIT MSG", msg_class="default-log"):
        game['military']['log'] = [{'class': msg_class, 'content': x} for x in self.log] + game['military']['log']
        serialized = self.serialize_object(game)
        proc = Popen(('git', 'hash-object', '-w', '--stdin'),
                     env = { "GIT_DIR":self.git_dir },
                     stdin = PIPE,
                     stdout = PIPE,
                     stderr = PIPE)

        out, err = proc.communicate(serialized)
#         print out.rstrip()
#         print err
        tree = "100644 blob " + out.rstrip() + "\t" + "deck"

        proc = Popen(('git', 'mktree'),
                     env = { "GIT_DIR":self.git_dir },
                     stdin = PIPE,
                     stdout = PIPE,
                     stderr = PIPE)

        out, err = proc.communicate(tree)
        tree_hash = out.rstrip()
#         print out.rstrip()
#         print err

        proc = Popen(('git', 'ls-tree', tree_hash),
                     env = { "GIT_DIR":self.git_dir },
                     stdin = PIPE,
                     stdout = PIPE,
                     stderr = PIPE)

        out, err = proc.communicate()
#         print out.rstrip()
#         print err

        proc = Popen(('git', 'commit-tree', tree_hash, '-p', branch),
                     env = { "GIT_DIR":self.git_dir },
                     stdin = PIPE,
                     stdout = PIPE,
                     stderr = PIPE)

        out, err = proc.communicate(commit_msg)
#         print out.rstrip()
#         print err

        proc = Popen(('git', 'update-ref', "refs/heads/" + branch, out.rstrip()),
                     env = { "GIT_DIR":self.git_dir },
                     stdin = PIPE,
                     stdout = PIPE,
                     stderr = PIPE)

    def get_game(self):
        proc = Popen(('git', 'ls-tree', '-z', self.branch),
                     env = { "GIT_DIR":self.git_dir },
                     stdin = PIPE,
                     stdout = PIPE,
                     stderr = PIPE)

        ls_tree_pattern = re.compile('((\d{6}) (tree|blob)) ([0-9a-f]{40})\t(.+)$')

        out, err = proc.communicate()
        lines = out.rstrip().split('\0')
#         print lines

        for line in lines:
            if not line: continue
            match = ls_tree_pattern.match(line)
            if not match: continue
            if not match.group(5) == 'deck': continue

            hash = match.group(4)
#             print hash


        proc = Popen(('git', 'cat-file', 'blob',  hash),
                     env = { "GIT_DIR":self.git_dir },
                     stdin = PIPE,
                     stdout = PIPE,
                     stderr = PIPE)
        out, err = proc.communicate()
        contents = out
        game = simplejson.loads(contents)
        return game

    def create_branch_at_master_head(self, branch):
        proc = Popen(('git', 'branch', branch, 'master'),
                     env = { "GIT_DIR":self.git_dir },
                     stdin = PIPE,
                     stdout = PIPE,
                     stderr = PIPE)

        out, err = proc.communicate()

    def replace_master_with_branch(self, branch):
        self.write_game('master', self.get_game(branch), str("replacing master with " + branch))

        self.delete_branch(branch)

    def delete_branch(self, branch):
        proc = Popen(('git', 'branch', '-D', branch),
                     env = { "GIT_DIR":self.git_dir },
                     stdin = PIPE,
                     stdout = PIPE,
                     stderr = PIPE)

        out, err = proc.communicate()
#         print out
#         print err
