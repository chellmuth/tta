#!/usr/bin/env python

import random
from django.utils import simplejson

import os
import re
from subprocess import Popen, PIPE
from tta.settings import REPO_ROOT

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
            self.write_game('master',{'deck':self.make_shuffled_deck(init_data['num_players']), 'civ':self.make_initial_civ(init_data['players']), 'military': self.make_age_a_military()}, 'default-log')

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
        shuffled = self.shuffle(self.military['future']['III']) + self.shuffle(self.military['future']['II']) + self.shuffle(self.military['future']['I']) + self.shuffle(self.military['future']['A'])
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

    def make_age_a_military(self):
        age_a = self.shuffle([
                { 'name': 'Development of Agriculture', 'file': 'Development_of_Agriculture.png',  'cell': 'event', 'deck': 'A', 'back': 'Age_A_Military_-_Card_Back.png' },
                { 'name': 'Development of Crafts', 'file': 'Development_of_Crafts.png',       'cell': 'event', 'deck': 'A', 'back': 'Age_A_Military_-_Card_Back.png' },
                { 'name': 'Development of Markets', 'file': 'Development_of_Markets.png',      'cell': 'event', 'deck': 'A', 'back': 'Age_A_Military_-_Card_Back.png' },
                { 'name': 'Development of Politics', 'file': 'Development_of_Politics.png',     'cell': 'event', 'deck': 'A', 'back': 'Age_A_Military_-_Card_Back.png' },
                { 'name': 'Development of Religion', 'file': 'Development_of_Religion.png',     'cell': 'event', 'deck': 'A', 'back': 'Age_A_Military_-_Card_Back.png' },
                { 'name': 'Development of Science', 'file': 'Development_of_Science.png',      'cell': 'event', 'deck': 'A', 'back': 'Age_A_Military_-_Card_Back.png' },
                { 'name': 'Development of Settlement', 'file': 'Development_of_Settlement.png',   'cell': 'event', 'deck': 'A', 'back': 'Age_A_Military_-_Card_Back.png' },
                { 'name': 'Development of Trade Routes', 'file': 'Development_of_Trade_Routes.png', 'cell': 'event', 'deck': 'A', 'back': 'Age_A_Military_-_Card_Back.png' },
                { 'name': 'Development of Warefare', 'file': 'Development_of_Warfare.png',      'cell': 'event', 'deck': 'A', 'back': 'Age_A_Military_-_Card_Back.png' },
                { 'name': 'No Event', 'file': 'No_Event.png',                    'cell': 'event', 'deck': 'A', 'back': 'Age_A_Military_-_Card_Back.png' }
                ])

        age_I = self.shuffle([
                { 'name': 'Barbarians', 'file': 'age_1/Barbarians.png',              'cell': 'event',      'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'name': 'Border Conflict', 'file': 'age_1/Border_Conflict.png',         'cell': 'event',      'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'name': 'Crusades', 'file': 'age_1/Crusades.png',                'cell': 'event',      'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'name': 'Cultural Influence', 'file': 'age_1/Cultural_Influence.png',      'cell': 'event',      'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'name': 'Foray', 'file': 'age_1/Foray.png',                   'cell': 'event',      'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'name': 'Good Harvest', 'file': 'age_1/Good_Harvest.png',            'cell': 'event',      'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'name': 'Immigration', 'file': 'age_1/Immigration.png',             'cell': 'event',      'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'name': 'New Deposits', 'file': 'age_1/new_Deposits.png',            'cell': 'event',      'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'name': 'Pestilence', 'file': 'age_1/Pestilence.png',              'cell': 'event',      'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'name': 'Raiders', 'file': 'age_1/Raiders.png',                 'cell': 'event',      'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'name': 'Rats', 'file': 'age_1/Rats.png',                    'cell': 'event',      'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'name': 'Rebellion', 'file': 'age_1/Rebellion.png',               'cell': 'event',      'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'name': 'Reign of Terror', 'file': 'age_1/Reign_of_Terror.png',         'cell': 'event',      'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'name': 'Scientific Breakthrough', 'file': 'age_1/scientific_breakthrough.png', 'cell': 'event',      'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'name': 'Uncertain Borders', 'file': 'age_1/Uncertain_Borders.png',       'cell': 'event',      'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },

                { 'name': 'Bonus', 'file': 'age_1/Bonus.png',                   'cell': 'aggression', 'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'name': 'Bonus', 'file': 'age_1/Bonus.png',                   'cell': 'aggression', 'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'name': 'Bonus', 'file': 'age_1/Bonus.png',                   'cell': 'aggression', 'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'name': 'Bonus', 'file': 'age_1/Bonus.png',                   'cell': 'aggression', 'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'name': 'Bonus', 'file': 'age_1/Bonus.png',                   'cell': 'aggression', 'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'name': 'Bonus', 'file': 'age_1/Bonus.png',                   'cell': 'aggression', 'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },

                { 'name': 'Developed Territory', 'file': 'age_1/Developed_Territory.png',     'cell': 'territory',  'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'name': 'Fertile Territory', 'file': 'age_1/Fertile_Territory.png',       'cell': 'territory',  'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'name': 'Historic Territory', 'file': 'age_1/Historic_Territory.png',      'cell': 'territory',  'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'name': 'Inhabited Territory', 'file': 'age_1/Inhabited_Territory.png',     'cell': 'territory',  'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'name': 'Strategic Territory', 'file': 'age_1/strategic_territory.png',     'cell': 'territory',  'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'name': 'Wealty Territory', 'file': 'age_1/Wealthy_Territory.png',       'cell': 'territory',  'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },

                { 'name': 'Enslave', 'file': 'age_1/Enslave.png',                 'cell': 'aggression', 'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'name': 'Enslave', 'file': 'age_1/Enslave.png',                 'cell': 'aggression', 'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'name': 'Plunder', 'file': 'age_1/Plunder.png',                 'cell': 'aggression', 'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'name': 'Plunder', 'file': 'age_1/Plunder.png',                 'cell': 'aggression', 'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'name': 'Raid', 'file': 'age_1/Raid.png',                    'cell': 'aggression', 'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },

                { 'name': 'Open Borders Agreement', 'file': 'age_1/Open_Borders_Agreement.png',  'cell': 'pact',       'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'name': 'Trade Route Agreements', 'file': 'age_1/Trade_Route_Agreements.png',  'cell': 'pact',       'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },

                { 'name': 'Fighting Band', 'file': 'age_1/Fighting_Band.png',           'cell': 'tactics',    'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'name': 'Fighting Band', 'file': 'age_1/Fighting_Band.png',           'cell': 'tactics',    'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'name': 'Fighting Band', 'file': 'age_1/Fighting_Band.png',           'cell': 'tactics',    'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'name': 'Heavy Cavalry', 'file': 'age_1/Heavy_Cavalry.png',           'cell': 'tactics',    'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'name': 'Heavy Cavalry', 'file': 'age_1/Heavy_Cavalry.png',           'cell': 'tactics',    'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'name': 'Legion', 'file': 'age_1/Legion.png',                  'cell': 'tactics',    'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'name': 'Legion', 'file': 'age_1/Legion.png',                  'cell': 'tactics',    'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'name': 'Ligh Cavalry', 'file': 'age_1/Light_Cavalry.png',           'cell': 'tactics',    'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'name': 'Ligh Cavalry', 'file': 'age_1/Light_Cavalry.png',           'cell': 'tactics',    'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'name': 'Medieval Army', 'file': 'age_1/medieval_army.png',           'cell': 'tactics',    'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'name': 'Medieval Army', 'file': 'age_1/medieval_army.png',           'cell': 'tactics',    'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'name': 'Medieval Army', 'file': 'age_1/medieval_army.png',           'cell': 'tactics',    'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'name': 'Phalanx', 'file': 'age_1/Phalanx.png',                 'cell': 'tactics',    'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'name': 'Phalanx', 'file': 'age_1/Phalanx.png',                 'cell': 'tactics',    'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'name': 'Phalanx', 'file': 'age_1/Phalanx.png',                 'cell': 'tactics',    'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' }
                ])

        age_II = self.shuffle([
                { 'name': 'Civil Unrest', 'file': '/age_2/Civil_Unrest.png', 'cell':'event', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'name': 'Cold War', 'file': '/age_2/Cold_War.png', 'cell':'event', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'name': 'Crime Wave', 'file': '/age_2/Crime_Wave.png', 'cell':'event', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'name': 'Economic Progress', 'file': '/age_2/Economic_Progress.png', 'cell':'event', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'name': 'Emigration', 'file': '/age_2/Emigration.png', 'cell':'event', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'name': 'Iconoclasm', 'file': '/age_2/Iconoclasm.png', 'cell':'event', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'name': 'Independence Declaration', 'file': '/age_2/Independence_Declaration.png', 'cell':'event', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'name': 'International Agreement', 'file': '/age_2/International_Agreement.png', 'cell':'event', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'name': 'National Pride', 'file': '/age_2/National_Pride.png', 'cell':'event', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'name': 'Popularization of Science', 'file': '/age_2/Popularization_of_Science.png', 'cell':'event', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'name': 'Ravages of Time', 'file': '/age_2/Ravages_of_Time.png', 'cell':'event', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'name': 'Refugees', 'file': '/age_2/Refugees.png', 'cell':'event', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'name': 'Terrorism', 'file': '/age_2/Terrorism.png', 'cell':'event', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },

                { 'name': 'Developed Territory', 'file': '/age_2/Developed_Territory.png', 'cell':'territory', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'name': 'Fertile Territory', 'file': '/age_2/Fertile_Territory.png', 'cell':'territory', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'name': 'Historic Territory', 'file': '/age_2/Historic_Territory.png', 'cell':'territory', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'name': 'Inhabited Territory', 'file': '/age_2/Inhabited_Territory.png', 'cell':'territory', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'name': 'Strategic Territory', 'file': '/age_2/Strategic_Territory.png', 'cell':'territory', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'name': 'Wealthy Territory', 'file': '/age_2/Wealthy_Territory.png', 'cell':'territory', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },

                { 'name': 'Bonus', 'file': '/age_2/Bonus.png', 'cell':'aggression', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'name': 'Bonus', 'file': '/age_2/Bonus.png', 'cell':'aggression', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'name': 'Bonus', 'file': '/age_2/Bonus.png', 'cell':'aggression', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'name': 'Bonus', 'file': '/age_2/Bonus.png', 'cell':'aggression', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'name': 'Bonus', 'file': '/age_2/Bonus.png', 'cell':'aggression', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'name': 'Bonus', 'file': '/age_2/Bonus.png', 'cell':'aggression', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },

                { 'name': 'Annex', 'file': '/age_2/Annex.png', 'cell':'aggression', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'name': 'Assassinate', 'file': '/age_2/Assassinate.png', 'cell':'aggression', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'name': 'Plunder', 'file': '/age_2/Plunder.png', 'cell':'aggression', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'name': 'Plunder', 'file': '/age_2/Plunder.png', 'cell':'aggression', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'name': 'Raid', 'file': '/age_2/Raid.png', 'cell':'aggression', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'name': 'Raid', 'file': '/age_2/Raid.png', 'cell':'aggression', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'name': 'Sabotage', 'file': '/age_2/Sabotage.png', 'cell':'aggression', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'name': 'Spy', 'file': '/age_2/Spy.png', 'cell':'aggression', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'name': 'Spy', 'file': '/age_2/Spy.png', 'cell':'aggression', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },

                { 'name': 'War over Culture', 'file': '/age_2/War_over_Culture.png', 'cell':'aggression', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'name': 'War over Resources', 'file': '/age_2/War_over_Resources.png', 'cell':'aggression', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'name': 'War over Technology', 'file': '/age_2/War_over_Technology.png', 'cell':'aggression', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'name': 'War over Territory', 'file': '/age_2/War_over_Territory.png', 'cell':'aggression', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },

                { 'name': 'Acceptance of Supremacy', 'file': '/age_2/Acceptance_of_Supremacy.png', 'cell':'pact', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'name': 'International Trade Agreement', 'file': '/age_2/International_Trade_Agreement.png', 'cell':'pact', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'name': 'Promise of Military Protection', 'file': '/age_2/Promise_of_Military_Protection.png', 'cell':'pact', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'name': 'Scientific Cooperation', 'file': '/age_2/Scientific_Cooperation.png', 'cell':'pact', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },

                { 'name': 'Classic Army', 'file': '/age_2/Classic_Army.png', 'cell':'tactics', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'name': 'Conquistadors', 'file': '/age_2/Conquistadors.png', 'cell':'tactics', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'name': 'Conquistadors', 'file': '/age_2/Conquistadors.png', 'cell':'tactics', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'name': 'Defensive Army', 'file': '/age_2/Defensive_Army.png', 'cell':'tactics', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'name': 'Defensive Army', 'file': '/age_2/Defensive_Army.png', 'cell':'tactics', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'name': 'Fortifications', 'file': '/age_2/Fortifications.png', 'cell':'tactics', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'name': 'Mobile Artillery', 'file': '/age_2/Mobile_Artillery.png', 'cell':'tactics', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'name': 'Napoleonic Army', 'file': '/age_2/Napoleonic_Army.png', 'cell':'tactics', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' }
                ])

        age_III = self.shuffle([
                { 'name': 'Impact of Agriculture', 'file': 'age_3/Impact_of_Agriculture.png', 'cell':'event', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'name': 'Impact of Architecture', 'file': 'age_3/Impact_of_Architecture.png', 'cell':'event', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'name': 'Impact of Colonies', 'file': 'age_3/Impact_of_Colonies.png', 'cell':'event', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'name': 'Impact of Competition', 'file': 'age_3/Impact_of_Competition.png', 'cell':'event', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'name': 'Impact of Government', 'file': 'age_3/Impact_of_Government.png', 'cell':'event', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'name': 'Impact of Happiness', 'file': 'age_3/Impact_of_Happiness.png', 'cell':'event', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'name': 'Impact of Industry', 'file': 'age_3/Impact_of_Industry.png', 'cell':'event', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'name': 'Impact of Population', 'file': 'age_3/Impact_of_Population.png', 'cell':'event', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'name': 'Impact of Progress', 'file': 'age_3/Impact_of_Progress.png', 'cell':'event', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'name': 'Impact of Science', 'file': 'age_3/Impact_of_Science.png', 'cell':'event', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'name': 'Impact of Strength', 'file': 'age_3/Impact_of_Strength.png', 'cell':'event', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'name': 'Impact of Technology', 'file': 'age_3/Impact_of_Technology.png', 'cell':'event', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'name': 'Impact of Wonders', 'file': 'age_3/Impact_of_Wonders.png', 'cell':'event', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },

                { 'name': 'Bonus', 'file': 'age_3/Bonus.png', 'cell':'aggression', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'name': 'Bonus', 'file': 'age_3/Bonus.png', 'cell':'aggression', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'name': 'Bonus', 'file': 'age_3/Bonus.png', 'cell':'aggression', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'name': 'Bonus', 'file': 'age_3/Bonus.png', 'cell':'aggression', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'name': 'Bonus', 'file': 'age_3/Bonus.png', 'cell':'aggression', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'name': 'Bonus', 'file': 'age_3/Bonus.png', 'cell':'aggression', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },

                { 'name': 'Armed Intervention', 'file': 'age_3/Armed_Intervention.png', 'cell':'aggression', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'name': 'Armed Intervention', 'file': 'age_3/Armed_Intervention.png', 'cell':'aggression', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'name': 'Armed Intervention', 'file': 'age_3/Armed_Intervention.png', 'cell':'aggression', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'name': 'Armed Intervention', 'file': 'age_3/Armed_Intervention.png', 'cell':'aggression', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'name': 'Armed Intervention', 'file': 'age_3/Armed_Intervention.png', 'cell':'aggression', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'name': 'Armed Intervention', 'file': 'age_3/Plunder.png', 'cell':'aggression', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'name': 'Armed Intervention', 'file': 'age_3/Plunder.png', 'cell':'aggression', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'name': 'Armed Intervention', 'file': 'age_3/Raid.png', 'cell':'aggression', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'name': 'Armed Intervention', 'file': 'age_3/Raid.png', 'cell':'aggression', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },

                { 'name': 'Holy War', 'file': 'age_3/Holy_War.png', 'cell':'aggression', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'name': 'Holy War', 'file': 'age_3/Holy_War.png', 'cell':'aggression', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'name': 'War over Culture', 'file': 'age_3/War_over_Culture.png', 'cell':'aggression', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'name': 'War over Culture', 'file': 'age_3/War_over_Culture.png', 'cell':'aggression', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'name': 'War over Culture', 'file': 'age_3/War_over_Culture.png', 'cell':'aggression', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'name': 'War over Culture', 'file': 'age_3/War_over_Culture.png', 'cell':'aggression', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },

                { 'name': 'International Tourism', 'file': 'age_3/International_Tourism.png', 'cell':'pact', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'name': 'Loss of Sovereignity', 'file': 'age_3/Loss_of_Sovereignity.png', 'cell':'pact', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'name': 'Military Pact', 'file': 'age_3/Military_Pact.png', 'cell':'pact', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'name': 'Peace Treaty', 'file': 'age_3/Peace_Treaty.png', 'cell':'pact', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },

                { 'name': 'Entrenchments', 'file': 'age_3/Entrenchments.png', 'cell':'tactics', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'name': 'Entrenchments', 'file': 'age_3/Entrenchments.png', 'cell':'tactics', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'name': 'Mechanized Army', 'file': 'age_3/Mechanized_Army.png', 'cell':'tactics', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'name': 'Mechanized Army', 'file': 'age_3/Mechanized_Army.png', 'cell':'tactics', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'name': 'Modern Army', 'file': 'age_3/Modern_Army.png', 'cell':'tactics', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'name': 'Modern Army', 'file': 'age_3/Modern_Army.png', 'cell':'tactics', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'name': 'Shock Troops', 'file': 'age_3/Shock_Troops.png', 'cell':'tactics', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'name': 'Shock Troops', 'file': 'age_3/Shock_Troops.png', 'cell':'tactics', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' }
                ])

        return {
            'future': { 'A' : [], 'I': [], 'II': [], 'III': [] },
            'current': age_a[:6],
            'current_event': None,
            'A':       [],
            'I':       age_I,
            'II':      age_II,
            'III':     age_III,
            'aggressions': [],
            'pacts': [],
            'log': []
            }

    def make_shuffled_deck(self, num_players):
        ageA = self.shuffle([
                { 'name': 'Alexander the Great', 'file': 'Alexander_the_Great.png',   'cell': 'leader', 'back': 'Age_A_Civil_-_Card_Back.png' },
                { 'name': 'Aristotle', 'file': 'Aristotle.png',             'cell': 'leader', 'back': 'Age_A_Civil_-_Card_Back.png' },
                { 'name': 'Hammurabi', 'file': 'Hammurabi.png',             'cell': 'leader', 'back': 'Age_A_Civil_-_Card_Back.png' },
                { 'name': 'Homer', 'file': 'Homer.png',                 'cell': 'leader', 'back': 'Age_A_Civil_-_Card_Back.png' },
                { 'name': 'Julius Caesar', 'file': 'Julius_Caesar.png',         'cell': 'leader', 'back': 'Age_A_Civil_-_Card_Back.png' },
                { 'name': 'Moses', 'file': 'Moses.png',                 'cell': 'leader', 'back': 'Age_A_Civil_-_Card_Back.png' },

                { 'name': 'Colossu', 'file': 'Colossus.png',              'cell': 'wonder', 'back': 'Age_A_Civil_-_Card_Back.png' },
                { 'name': 'Hanging Gardens', 'file': 'Hanging_Gardens.png',       'cell': 'wonder', 'back': 'Age_A_Civil_-_Card_Back.png' },
                { 'name': 'Library of Alexandria', 'file': 'Library_of_Alexandria.png', 'cell': 'wonder', 'back': 'Age_A_Civil_-_Card_Back.png' },
                { 'name': 'Pyramids', 'file': 'Pyramids.png',              'cell': 'wonder', 'back': 'Age_A_Civil_-_Card_Back.png' },

                { 'name': 'Engineering Genius', 'file': 'Engineering_Genius.png',    'cell': 'yellow-card', 'back': 'Age_A_Civil_-_Card_Back.png' },
                { 'name': 'Frugality', 'file': 'Frugality.png',             'cell': 'yellow-card', 'back': 'Age_A_Civil_-_Card_Back.png' },
                { 'name': 'Frugality', 'file': 'Frugality.png',             'cell': 'yellow-card', 'back': 'Age_A_Civil_-_Card_Back.png' },
                { 'name': 'Ideal Building Site', 'file': 'Ideal_Building_Site.png',   'cell': 'yellow-card', 'back': 'Age_A_Civil_-_Card_Back.png' },
                { 'name': 'Ideal Building Site', 'file': 'Ideal_Building_Site.png',   'cell': 'yellow-card', 'back': 'Age_A_Civil_-_Card_Back.png' },
                { 'name': 'Patriotism', 'file': 'Patriotism.png',            'cell': 'yellow-card', 'back': 'Age_A_Civil_-_Card_Back.png' },
                { 'name': 'Revolutionary Idea', 'file': 'Revolutionary_Idea.png',    'cell': 'yellow-card', 'back': 'Age_A_Civil_-_Card_Back.png' },
                { 'name': 'Rich Land', 'file': 'Rich_Land.png',             'cell': 'yellow-card', 'back': 'Age_A_Civil_-_Card_Back.png' },
                { 'name': 'Rich Land', 'file': 'Rich_Land.png',             'cell': 'yellow-card', 'back': 'Age_A_Civil_-_Card_Back.png' },
                { 'name': 'Work of Art', 'file': 'Work_of_Art.png',           'cell': 'yellow-card', 'back': 'Age_A_Civil_-_Card_Back.png' }
                ])

        _4ageI = [
            { 'name': 'Alchemy', 'file': 'age_1/Alchemy.png',        'cell': 'alchemy', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
            { 'name': 'Iron', 'file': 'age_1/Iron_dsn.png',       'cell': 'iron', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
            { 'name': 'Swordsmen', 'file': 'age_1/Swordsmen_dsn.png',  'cell': 'swordsmen', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
            { 'name': 'Irrigation', 'file': 'age_1/Irrigation_dsn.png', 'cell': 'irrigation', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
            { 'name': 'Knights', 'file': 'age_1/knights_dsn.png',    'cell': 'knights', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' }
            ]
        if num_players < 4:
            _4ageI = []

        _3ageI = [
                { 'name': 'Theology', 'file': 'age_1/Theology_dsn.png',         'cell': 'theology', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'name': 'Bread and Circuses', 'file': 'age_1/Bread_and_Circuses.png',   'cell': 'bread_and_circuses', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'name': 'Warefare', 'file': 'age_1/warfare_dsn.png', 'cell': 'warfare', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'name': 'Code of Laws', 'file': 'age_1/Code_of_Laws.png', 'cell': 'code_of_laws', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'name': 'Monarchy', 'file': 'age_1/Monarchy_dsn.png', 'cell': 'government', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' }
            ]
        if num_players < 3:
            _3ageI = []

        _2ageI = [
            { 'name': 'Bountiful Harvest', 'file': 'age_1/Bountiful_Harvest.png',       'cell': 'yellow-card', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
            { 'name': 'Breakthrough', 'file': 'age_1/Breakthrough.png',            'cell': 'yellow-card', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
            { 'name': 'Efficient Upgrade', 'file': 'age_1/Efficient_Upgrade.png',       'cell': 'yellow-card', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
            { 'name': 'Efficient Upgrade', 'file': 'age_1/Efficient_Upgrade.png',       'cell': 'yellow-card', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
            { 'name': 'Engineering Genius', 'file': 'age_1/Engineering_Genius.png',      'cell': 'yellow-card', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
            { 'name': 'Frugality', 'file': 'age_1/Frugality.png',               'cell': 'yellow-card', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
            { 'name': 'Ideal Building Site', 'file': 'age_1/Ideal_Building_Site_dsn.png', 'cell': 'yellow-card', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
            { 'name': 'Mineral Deposits', 'file': 'age_1/Mineral_Deposits_dsn.png',    'cell': 'yellow-card', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
            { 'name': 'Mineral Deposits', 'file': 'age_1/Mineral_Deposits_dsn.png',    'cell': 'yellow-card', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
            { 'name': 'Patriotism', 'file': 'age_1/Patiotism_Age_1_dsn.png',     'cell': 'yellow-card', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
            { 'name': 'Revolutionary Idea', 'file': 'age_1/Revolutionary_Idea_dsn.png',  'cell': 'yellow-card', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
            { 'name': 'Rich Land', 'file': 'age_1/Rich_Land_dsn.png',           'cell': 'yellow-card', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
            { 'name': 'Work of Art', 'file': 'age_1/Work_of_Art.png',             'cell': 'yellow-card', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },

            { 'name': 'Theology', 'file': 'age_1/Theology_dsn.png',         'cell': 'theology', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
            { 'name': 'Alchemy', 'file': 'age_1/Alchemy.png',              'cell': 'alchemy', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
            { 'name': 'Alchemy', 'file': 'age_1/Alchemy.png',              'cell': 'alchemy', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
            { 'name': 'Bread And Circuses', 'file': 'age_1/Bread_and_Circuses.png',   'cell': 'bread_and_circuses', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
            { 'name': 'Drama', 'file': 'age_1/Drama.png',                'cell': 'drama', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
            { 'name': 'Drama', 'file': 'age_1/Drama.png',                'cell': 'drama', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
            { 'name': 'Iron', 'file': 'age_1/Iron_dsn.png',             'cell': 'iron', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
            { 'name': 'Iron', 'file': 'age_1/Iron_dsn.png',             'cell': 'iron', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
            { 'name': 'Irrigation', 'file': 'age_1/Irrigation_dsn.png',       'cell': 'irrigation', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
            { 'name': 'Irrigation', 'file': 'age_1/Irrigation_dsn.png',       'cell': 'irrigation', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
            { 'name': 'Printing Press', 'file': 'age_1/Printing_Press_1_dsn.png', 'cell': 'printing_press', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
            { 'name': 'Printing Press', 'file': 'age_1/Printing_Press_1_dsn.png', 'cell': 'printing_press', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
            { 'name': 'Swordsmen', 'file': 'age_1/Swordsmen_dsn.png',        'cell': 'swordsmen', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
            { 'name': 'Swordsmen', 'file': 'age_1/Swordsmen_dsn.png',        'cell': 'swordsmen', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
            { 'name': 'Knights', 'file': 'age_1/knights_dsn.png',          'cell': 'knights', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
            { 'name': 'Knights', 'file': 'age_1/knights_dsn.png',          'cell': 'knights', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },

            { 'name': 'Great Wall', 'file': 'age_1/Great_Wall_dsn.png', 'cell': 'wonder', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
            { 'name': 'St. Peter\s Basilica', 'file': 'age_1/St_Peters_Basilica_dsn.png', 'cell': 'wonder', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
            { 'name': 'Taj Mahal', 'file': 'age_1/Taj_Mahal_dsn.png', 'cell': 'wonder', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
            { 'name': 'Universitas Carolina', 'file': 'age_1/universitas_carolina_dsn.png', 'cell': 'wonder', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },

            { 'name': 'Cartography', 'file': 'age_1/Cartography.png', 'cell': 'cartography', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
            { 'name': 'Code of Laws', 'file': 'age_1/Code_of_Laws.png', 'cell': 'code_of_laws', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
            { 'name': 'Masonry', 'file': 'age_1/Masonry_dsn.png', 'cell': 'masonry', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
            { 'name': 'Warefare', 'file': 'age_1/warfare_dsn.png', 'cell': 'warfare', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },

            { 'name': 'Michelangelo', 'file': 'age_1/Michelangelo_dsn.png', 'cell': 'leader', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
            { 'name': 'Joan of Arc', 'file': 'age_1/Joan_of_Arc_dsn.png', 'cell': 'leader', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
            { 'name': 'Leonardo da Vinci', 'file': 'age_1/Leonardo_da_Vinci_dsn.png', 'cell': 'leader', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
            { 'name': 'Genghis Khan', 'file': 'age_1/Genghis_Khan.png', 'cell': 'leader', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
            { 'name': 'Christopher Columbus', 'file': 'age_1/Christopher_Columbus.png', 'cell': 'leader', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
            { 'name': 'Frederick Barbarrossa', 'file': 'age_1/Frederick_Barbarrossa.png', 'cell': 'leader', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },

            { 'name': 'Monarchy', 'file': 'age_1/Monarchy_dsn.png', 'cell': 'government', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
            { 'name': 'Theocracy', 'file': 'age_1/Theocracy_dsn.png', 'cell': 'government', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' }
            ]

        ageI = self.shuffle(_4ageI + _3ageI + _2ageI)

        _4ageII = [
            { 'name': 'Journalism', 'file': 'age_2/Journalism.png',         'cell': 'journalism', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
            { 'name': 'Cavalrymen', 'file': 'age_2/Cavalrymen.png', 'cell': 'cavalrymen', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
            { 'name': 'Cavalrymen', 'file': 'age_2/Cavalrymen.png', 'cell': 'cavalrymen', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
            { 'name': 'Republic', 'file': 'age_2/Republic.png', 'cell': 'government', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
            { 'name': 'Justice System', 'file': 'age_2/Justice_System.png', 'cell': 'justice_system', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' }
        ]
        if num_players < 4:
            _4ageII = []

        _3ageII = [
            { 'name': 'Selective Breeding', 'file': 'age_2/Selective_Breeding.png', 'cell': 'selective_breeding', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
            { 'name': 'Coal', 'file': 'age_2/Coal.png',               'cell': 'coal', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
            { 'name': 'Riflemen', 'file': 'age_2/Riflemen.png', 'cell': 'riflemen', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
            { 'name': 'Constitutional Monarchy', 'file': 'age_2/Constitutional_Monarchy.png', 'cell': 'government', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
            { 'name': 'Architecture', 'file': 'age_2/Architecture.png', 'cell': 'architecture', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' }
        ]
        if num_players < 3:
            _3ageII = []

        _2ageII = [
            { 'name': 'Bountiful Harvest', 'file': 'age_2/Bountiful_Harvest.png',   'cell': 'yellow-card', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
            { 'name': 'Breakthrough', 'file': 'age_2/Breakthrough.png',        'cell': 'yellow-card', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
            { 'name': 'Efficient Upgrade', 'file': 'age_2/Efficient_Upgrade.png',   'cell': 'yellow-card', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
            { 'name': 'Efficient Upgrade', 'file': 'age_2/Efficient_Upgrade.png',   'cell': 'yellow-card', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
            { 'name': 'Engineering Genius', 'file': 'age_2/Engineering_Genius.png',  'cell': 'yellow-card', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
            { 'name': 'Frugality', 'file': 'age_2/Frugality.png',           'cell': 'yellow-card', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
            { 'name': 'Ideal Building Site', 'file': 'age_2/Ideal_Building_Site.png', 'cell': 'yellow-card', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
            { 'name': 'Mineral Deposits', 'file': 'age_2/Mineral_Deposits.png',    'cell': 'yellow-card', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
            { 'name': 'Patriotism', 'file': 'age_2/Patriotism.png',          'cell': 'yellow-card', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
            { 'name': 'Revolutionary Idea', 'file': 'age_2/Revolutionary_Idea.png',  'cell': 'yellow-card', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
            { 'name': 'Rich Land', 'file': 'age_2/Rich_Land.png',           'cell': 'yellow-card', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
            { 'name': 'Wave of Nationalism', 'file': 'age_2/Wave_of_Nationalism.png', 'cell': 'yellow-card', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
            { 'name': 'Work of Art', 'file': 'age_2/Work_of_Art.png',         'cell': 'yellow-card', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },

            { 'name': 'Selective Breeding', 'file': 'age_2/Selective_Breeding.png', 'cell': 'selective_breeding', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
            { 'name': 'Coal', 'file': 'age_2/Coal.png',               'cell': 'coal', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
            { 'name': 'Organized Religion', 'file': 'age_2/Organized_Religion.png', 'cell': 'organized_religion', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
            { 'name': 'Organized Religion', 'file': 'age_2/Organized_Religion.png', 'cell': 'organized_religion', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
            { 'name': 'Scientific Method', 'file': 'age_2/Scientific_Method.png',  'cell': 'scientific_method', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
            { 'name': 'Scientific Method', 'file': 'age_2/Scientific_Method.png',  'cell': 'scientific_method', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
            { 'name': 'Team Sports', 'file': 'age_2/Team_Sports.png',        'cell': 'team_sports', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
            { 'name': 'Journalism', 'file': 'age_2/Journalism.png',         'cell': 'journalism', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
            { 'name': 'Journalism', 'file': 'age_2/Journalism.png',         'cell': 'journalism', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
            { 'name': 'Opera', 'file': 'age_2/Opera.png',              'cell': 'opera', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
            { 'name': 'Opera', 'file': 'age_2/Opera.png',              'cell': 'opera', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },

            { 'name': 'Riflemen', 'file': 'age_2/Riflemen.png', 'cell': 'riflemen', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
            { 'name': 'Cavalrymen', 'file': 'age_2/Cavalrymen.png', 'cell': 'cavalrymen', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
            { 'name': 'Cavalrymen', 'file': 'age_2/Cannon.png', 'cell': 'cannon', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
            { 'name': 'Cannon', 'file': 'age_2/Cannon.png', 'cell': 'cannon', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
            { 'name': 'Cannon', 'file': 'age_2/Cannon.png', 'cell': 'cannon', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },

            { 'name': 'Transcontinental Railroad', 'file': 'age_2/Transcontinental_Railroad.png', 'cell': 'wonder', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
            { 'name': 'Eiffel Tower', 'file': 'age_2/Eiffel_Tower.png',              'cell': 'wonder', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
            { 'name': 'Kremlin', 'file': 'age_2/Kremlin.png',                   'cell': 'wonder', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
            { 'name': 'Ocean Liner Service', 'file': 'age_2/Ocean_Liner_Service.png',       'cell': 'wonder', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },

            { 'name': 'William Shakespeare', 'file': 'age_2/William_Shakespeare.png', 'cell': 'leader', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
            { 'name': 'James Cook', 'file': 'age_2/James_Cook.png', 'cell': 'leader', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
            { 'name': 'Napoleon Bonaparte', 'file': 'age_2/Napoleon_Bonaparte.png', 'cell': 'leader', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
            { 'name': 'Maximilien Robespierre', 'file': 'age_2/Maximilien_Robespierre.png', 'cell': 'leader', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
            { 'name': 'JS Bach', 'file': 'age_2/JS_Bach.png', 'cell': 'leader', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
            { 'name': 'Isaac Newton', 'file': 'age_2/Isaac_Newton.png', 'cell': 'leader', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },

            { 'name': 'Constitutional Monarchy', 'file': 'age_2/Constitutional_Monarchy.png', 'cell': 'government', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
            { 'name': 'Republic', 'file': 'age_2/Republic.png', 'cell': 'government', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },

            { 'name': 'Strategy', 'file': 'age_2/Strategy.png', 'cell': 'strategy', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
            { 'name': 'Justice System', 'file': 'age_2/Justice_System.png', 'cell': 'justice_system', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
            { 'name': 'Navigation', 'file': 'age_2/Navigation.png', 'cell': 'navigation', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
            { 'name': 'Architecture', 'file': 'age_2/Architecture.png', 'cell': 'architecture', 'back': 'age_2/Age_II_Civil_-_Card_Back.png'  }
            ]

        ageII = self.shuffle([_4ageII + _3ageII + _2ageII])

        _4ageIII = [
            { 'name': 'Professional Sports', 'file': 'age_3/Professional_Sports.png',    'cell':'professional_sports', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
            { 'name': 'Rockets', 'file': 'age_3/Rockets.png',         'cell':'rockets', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
            { 'name': 'Air Forces', 'file': 'age_3/Air_Forces.png',      'cell':'air_forces', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
            { 'name': 'Civil Theory', 'file': 'age_3/Civil_Theory.png', 'cell':'military_theory', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
            { 'name': 'Engineering', 'file': 'age_3/Engineering.png', 'cell':'engineering', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' }
        ]
        if num_players < 4:
            _4ageIII = []

        _3ageIII = [
            { 'name': 'Mechanized Agriculture', 'file': 'age_3/Mechanized_Agriculture.png', 'cell':'mechanized_agriculture', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
            { 'name': 'Oil', 'file': 'age_3/Oil.png',                    'cell':'oil', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
            { 'name': 'Modern Infantry', 'file': 'age_3/Modern_Infantry.png', 'cell':'modern_infantry', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
            { 'name': 'Tanks', 'file': 'age_3/Tanks.png',           'cell':'tanks', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
            { 'name': 'Democracy', 'file': 'age_3/Democracy.png', 'cell':'government', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' }
        ]
        if num_players < 3:
            _3ageIII = []

        _2ageIII = [
            { 'name': 'Bountiful Harvest', 'file': 'age_3/Bountiful_Harvest.png',      'cell':'yellow-card', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
            { 'name': 'Efficient Upgrade', 'file': 'age_3/Efficient_Upgrade.png',      'cell':'yellow-card', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
            { 'name': 'Endowment for the Arts', 'file': 'age_3/Endowment_for_the_Arts.png', 'cell':'yellow-card', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
            { 'name': 'Engineering Genius', 'file': 'age_3/Engineering_Genius.png',     'cell':'yellow-card', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
            { 'name': 'Ideal Building Site', 'file': 'age_3/Ideal_Building_Site.png',    'cell':'yellow-card', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
            { 'name': 'Military Build-up', 'file': 'age_3/Military_Build-Up.png',         'cell':'yellow-card', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
            { 'name': 'Mineral Deposits', 'file': 'age_3/Mineral_Deposits.png',       'cell':'yellow-card', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
            { 'name': 'Patriotism', 'file': 'age_3/Patriotism.png',             'cell':'yellow-card', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
            { 'name': 'Revolutionary Idea', 'file': 'age_3/Revolutionary_Idea.png',     'cell':'yellow-card', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
            { 'name': 'Work of Art', 'file': 'age_3/Work_of_Art.png',            'cell':'yellow-card', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },

            { 'name': 'Mechanized Agriculture', 'file': 'age_3/Mechanized_Agriculture.png', 'cell':'mechanized_agriculture', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
            { 'name': 'Oil', 'file': 'age_3/Oil.png',                    'cell':'oil', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
            { 'name': 'Computers', 'file': 'age_3/Computers.png',              'cell':'computers', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
            { 'name': 'Computers', 'file': 'age_3/Computers.png',              'cell':'computers', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
            { 'name': 'Professional Sports', 'file': 'age_3/Professional_Sports.png',    'cell':'professional_sports', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
            { 'name': 'Multimedia', 'file': 'age_3/Multimedia.png',             'cell':'multimedia', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
            { 'name': 'Multimedia', 'file': 'age_3/Multimedia.png',             'cell':'multimedia', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
            { 'name': 'Movies', 'file': 'age_3/Movies.png',                 'cell':'movies', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
            { 'name': 'Movies', 'file': 'age_3/Movies.png',                 'cell':'movies', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },

            { 'name': 'Modern Infantry', 'file': 'age_3/Modern_Infantry.png', 'cell':'modern_infantry', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
            { 'name': 'Tanks', 'file': 'age_3/Tanks.png',           'cell':'tanks', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
            { 'name': 'Rockets', 'file': 'age_3/Rockets.png',         'cell':'rockets', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
            { 'name': 'Rockets', 'file': 'age_3/Rockets.png',         'cell':'rockets', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
            { 'name': 'Air Forces', 'file': 'age_3/Air_Forces.png',      'cell':'air_forces', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
            { 'name': 'Air Forces', 'file': 'age_3/Air_Forces.png',      'cell':'air_forces', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },

            { 'name': 'Hollywood', 'file': 'age_3/Hollywood.png', 'cell':'wonder', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
            { 'name': 'Internet', 'file': 'age_3/Internet.png', 'cell':'wonder', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
            { 'name': 'First Space Flight', 'file': 'age_3/First_Space_Flight.png', 'cell':'wonder', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
            { 'name': 'Fast Food Chains', 'file': 'age_3/Fast_Food_Chains.png', 'cell':'wonder', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },

            { 'name': 'Albert Einstein', 'file': 'age_3/Albert_Einstein.png', 'cell':'leader', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
            { 'name': 'Mahatma Gandhi', 'file': 'age_3/Mahatma_Gandhi.png', 'cell':'leader', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
            { 'name': 'Rock and Roll Icon', 'file': 'age_3/Rock_and_Roll_Icon.png', 'cell':'leader', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
            { 'name': 'Nikola Tesla', 'file': 'age_3/Nikola_Tesla.png', 'cell':'leader', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
            { 'name': 'Winston Churchill', 'file': 'age_3/Winston_Churchill.png', 'cell':'leader', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
            { 'name': 'Game Designer', 'file': 'age_3/Game_Designer.png', 'cell':'leader', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },

            { 'name': 'Communism', 'file': 'age_3/Communism.png', 'cell':'government', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
            { 'name': 'Democracy', 'file': 'age_3/Democracy.png', 'cell':'government', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
            { 'name': 'Fundamentalism', 'file': 'age_3/Fundamentalism.png', 'cell':'government', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },

            { 'name': 'Military Theory', 'file': 'age_3/Civil_Theory.png', 'cell':'military_theory', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
            { 'name': 'Military Theory', 'file': 'age_3/Civil_Service.png', 'cell':'civil_service', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
            { 'name': 'Satellites', 'file': 'age_3/Satellites.png', 'cell':'satellites', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
            { 'name': 'Engineering', 'file': 'age_3/Engineering.png', 'cell':'engineering', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' }
            ]

        ageIII = self.shuffle([_4ageIII + _3ageIII + _2ageIII])

        return ageA + ageI + ageII + ageIII

    def shuffle(self, cards):
        shuffled = []
        for i in range(len(cards)):
            index = random.randint(0,len(cards) - 1)
            shuffled.append(cards.pop(index))

        return shuffled

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
