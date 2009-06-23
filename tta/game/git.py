#!/usr/bin/env python

import random
from django.utils import simplejson

import os
import re
from subprocess import Popen, PIPE

class Git:
    def __init__(self, dir):
        self.git_dir = '/home/cjh/tta_game/'

    def make_age_a_military(self):
        age_a = self.shuffle([
                { 'file': 'Development_of_Agriculture.png',  'cell': 'event', 'deck': 'A', 'back': 'Age_A_Military_-_Card_Back.png' },
                { 'file': 'Development_of_Crafts.png',       'cell': 'event', 'deck': 'A', 'back': 'Age_A_Military_-_Card_Back.png' },
                { 'file': 'Development_of_Markets.png',      'cell': 'event', 'deck': 'A', 'back': 'Age_A_Military_-_Card_Back.png' },
                { 'file': 'Development_of_Politics.png',     'cell': 'event', 'deck': 'A', 'back': 'Age_A_Military_-_Card_Back.png' },
                { 'file': 'Development_of_Religion.png',     'cell': 'event', 'deck': 'A', 'back': 'Age_A_Military_-_Card_Back.png' },
                { 'file': 'Development_of_Science.png',      'cell': 'event', 'deck': 'A', 'back': 'Age_A_Military_-_Card_Back.png' },
                { 'file': 'Development_of_Settlement.png',   'cell': 'event', 'deck': 'A', 'back': 'Age_A_Military_-_Card_Back.png' },
                { 'file': 'Development_of_Trade_Routes.png', 'cell': 'event', 'deck': 'A', 'back': 'Age_A_Military_-_Card_Back.png' },
                { 'file': 'Development_of_Warfare.png',      'cell': 'event', 'deck': 'A', 'back': 'Age_A_Military_-_Card_Back.png' },
                { 'file': 'No_Event.png',                    'cell': 'event', 'deck': 'A', 'back': 'Age_A_Military_-_Card_Back.png' }
                ])

        age_I = self.shuffle([
                { 'file': 'age_1/Barbarians.png',              'cell': 'event',      'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'file': 'age_1/Border_Conflict.png',         'cell': 'event',      'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'file': 'age_1/Crusades.png',                'cell': 'event',      'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'file': 'age_1/Cultural_Influence.png',      'cell': 'event',      'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'file': 'age_1/Foray.png',                   'cell': 'event',      'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'file': 'age_1/Good_Harvest.png',            'cell': 'event',      'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'file': 'age_1/Immigration.png',             'cell': 'event',      'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'file': 'age_1/new_Deposits.png',            'cell': 'event',      'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'file': 'age_1/Pestilence.png',              'cell': 'event',      'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'file': 'age_1/Raiders.png',                 'cell': 'event',      'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'file': 'age_1/Rats.png',                    'cell': 'event',      'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'file': 'age_1/Rebellion.png',               'cell': 'event',      'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'file': 'age_1/Reign_of_Terror.png',         'cell': 'event',      'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'file': 'age_1/scientific_breakthrough.png', 'cell': 'event',      'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'file': 'age_1/Uncertain_Borders.png',       'cell': 'event',      'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },

                { 'file': 'age_1/Bonus.png',                   'cell': 'aggression', 'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'file': 'age_1/Bonus.png',                   'cell': 'aggression', 'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'file': 'age_1/Bonus.png',                   'cell': 'aggression', 'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'file': 'age_1/Bonus.png',                   'cell': 'aggression', 'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'file': 'age_1/Bonus.png',                   'cell': 'aggression', 'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'file': 'age_1/Bonus.png',                   'cell': 'aggression', 'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },

                { 'file': 'age_1/Developed_Territory.png',     'cell': 'territory',  'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'file': 'age_1/Fertile_Territory.png',       'cell': 'territory',  'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'file': 'age_1/Historic_Territory.png',      'cell': 'territory',  'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'file': 'age_1/Inhabited_Territory.png',     'cell': 'territory',  'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'file': 'age_1/strategic_territory.png',     'cell': 'territory',  'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'file': 'age_1/Wealthy_Territory.png',       'cell': 'territory',  'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },

                { 'file': 'age_1/Enslave.png',                 'cell': 'aggression', 'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'file': 'age_1/Enslave.png',                 'cell': 'aggression', 'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'file': 'age_1/Plunder.png',                 'cell': 'aggression', 'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'file': 'age_1/Plunder.png',                 'cell': 'aggression', 'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'file': 'age_1/Raid.png',                    'cell': 'aggression', 'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },

                { 'file': 'age_1/Open_Borders_Agreement.png',  'cell': 'pact',       'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'file': 'age_1/Trade_Route_Agreements.png',  'cell': 'pact',       'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },

                { 'file': 'age_1/Fighting_Band.png',           'cell': 'tactics',    'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'file': 'age_1/Fighting_Band.png',           'cell': 'tactics',    'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'file': 'age_1/Fighting_Band.png',           'cell': 'tactics',    'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'file': 'age_1/Heavy_Cavalry.png',           'cell': 'tactics',    'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'file': 'age_1/Heavy_Cavalry.png',           'cell': 'tactics',    'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'file': 'age_1/Legion.png',                  'cell': 'tactics',    'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'file': 'age_1/Legion.png',                  'cell': 'tactics',    'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'file': 'age_1/Light_Cavalry.png',           'cell': 'tactics',    'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'file': 'age_1/Light_Cavalry.png',           'cell': 'tactics',    'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'file': 'age_1/medieval_army.png',           'cell': 'tactics',    'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'file': 'age_1/medieval_army.png',           'cell': 'tactics',    'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'file': 'age_1/medieval_army.png',           'cell': 'tactics',    'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'file': 'age_1/Phalanx.png',                 'cell': 'tactics',    'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'file': 'age_1/Phalanx.png',                 'cell': 'tactics',    'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' },
                { 'file': 'age_1/Phalanx.png',                 'cell': 'tactics',    'deck': 'I', 'back': 'age_1/Age_I_Military_-_Card_Back.png' }
                ])

        age_II = self.shuffle([
                { 'file': '/age_2/Civil_Unrest.png', 'cell':'event', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'file': '/age_2/Cold_War.png', 'cell':'event', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'file': '/age_2/Crime_Wave.png', 'cell':'event', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'file': '/age_2/Economic_Progress.png', 'cell':'event', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'file': '/age_2/Emigration.png', 'cell':'event', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'file': '/age_2/Iconoclasm.png', 'cell':'event', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'file': '/age_2/Independence_Declaration.png', 'cell':'event', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'file': '/age_2/International_Agreement.png', 'cell':'event', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'file': '/age_2/National_Pride.png', 'cell':'event', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'file': '/age_2/Popularization_of_Science.png', 'cell':'event', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'file': '/age_2/Ravages_of_Time.png', 'cell':'event', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'file': '/age_2/Refugees.png', 'cell':'event', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'file': '/age_2/Terrorism.png', 'cell':'event', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },

                { 'file': '/age_2/Developed_Territory.png', 'cell':'territory', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'file': '/age_2/Fertile_Territory.png', 'cell':'territory', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'file': '/age_2/Historic_Territory.png', 'cell':'territory', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'file': '/age_2/Inhabited_Territory.png', 'cell':'territory', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'file': '/age_2/Strategic_Territory.png', 'cell':'territory', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'file': '/age_2/Wealthy_Territory.png', 'cell':'territory', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },

                { 'file': '/age_2/Bonus.png', 'cell':'aggression', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'file': '/age_2/Bonus.png', 'cell':'aggression', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'file': '/age_2/Bonus.png', 'cell':'aggression', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'file': '/age_2/Bonus.png', 'cell':'aggression', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'file': '/age_2/Bonus.png', 'cell':'aggression', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'file': '/age_2/Bonus.png', 'cell':'aggression', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },

                { 'file': '/age_2/Annex.png', 'cell':'aggression', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'file': '/age_2/Assassinate.png', 'cell':'aggression', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'file': '/age_2/Plunder.png', 'cell':'aggression', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'file': '/age_2/Plunder.png', 'cell':'aggression', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'file': '/age_2/Raid.png', 'cell':'aggression', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'file': '/age_2/Raid.png', 'cell':'aggression', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'file': '/age_2/Sabotage.png', 'cell':'aggression', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'file': '/age_2/Spy.png', 'cell':'aggression', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'file': '/age_2/Spy.png', 'cell':'aggression', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },

                { 'file': '/age_2/War_over_Culture.png', 'cell':'aggression', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'file': '/age_2/War_over_Resources.png', 'cell':'aggression', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'file': '/age_2/War_over_Technology.png', 'cell':'aggression', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'file': '/age_2/War_over_Territory.png', 'cell':'aggression', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },

                { 'file': '/age_2/Acceptance_of_Supremacy.png', 'cell':'pact', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'file': '/age_2/International_Trade_Agreement.png', 'cell':'pact', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'file': '/age_2/Promise_of_Military_Protection.png', 'cell':'pact', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'file': '/age_2/Scientific_Cooperation.png', 'cell':'pact', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },

                { 'file': '/age_2/Classic_Army.png', 'cell':'tactics', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'file': '/age_2/Conquistadors.png', 'cell':'tactics', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'file': '/age_2/Conquistadors.png', 'cell':'tactics', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'file': '/age_2/Defensive_Army.png', 'cell':'tactics', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'file': '/age_2/Defensive_Army.png', 'cell':'tactics', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'file': '/age_2/Fortifications.png', 'cell':'tactics', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'file': '/age_2/Mobile_Artillery.png', 'cell':'tactics', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' },
                { 'file': '/age_2/Napoleonic_Army.png', 'cell':'tactics', 'deck': 'II', 'back': 'age_2/Age_II_Military_-_Card_Back.png' }
                ])

        age_III = self.shuffle([
                { 'file': 'age_3/Impact_of_Agriculture.png', 'cell':'event', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'file': 'age_3/Impact_of_Architecture.png', 'cell':'event', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'file': 'age_3/Impact_of_Colonies.png', 'cell':'event', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'file': 'age_3/Impact_of_Competition.png', 'cell':'event', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'file': 'age_3/Impact_of_Government.png', 'cell':'event', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'file': 'age_3/Impact_of_Happiness.png', 'cell':'event', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'file': 'age_3/Impact_of_Industry.png', 'cell':'event', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'file': 'age_3/Impact_of_Population.png', 'cell':'event', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'file': 'age_3/Impact_of_Progress.png', 'cell':'event', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'file': 'age_3/Impact_of_Science.png', 'cell':'event', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'file': 'age_3/Impact_of_Strength.png', 'cell':'event', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'file': 'age_3/Impact_of_Technology.png', 'cell':'event', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'file': 'age_3/Impact_of_Wonders.png', 'cell':'event', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },

                { 'file': 'age_3/Bonus.png', 'cell':'aggression', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'file': 'age_3/Bonus.png', 'cell':'aggression', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'file': 'age_3/Bonus.png', 'cell':'aggression', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'file': 'age_3/Bonus.png', 'cell':'aggression', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'file': 'age_3/Bonus.png', 'cell':'aggression', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'file': 'age_3/Bonus.png', 'cell':'aggression', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },

                { 'file': 'age_3/Armed_Intervention.png', 'cell':'aggression', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'file': 'age_3/Armed_Intervention.png', 'cell':'aggression', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'file': 'age_3/Armed_Intervention.png', 'cell':'aggression', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'file': 'age_3/Armed_Intervention.png', 'cell':'aggression', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'file': 'age_3/Armed_Intervention.png', 'cell':'aggression', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'file': 'age_3/Plunder.png', 'cell':'aggression', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'file': 'age_3/Plunder.png', 'cell':'aggression', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'file': 'age_3/Raid.png', 'cell':'aggression', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'file': 'age_3/Raid.png', 'cell':'aggression', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },

                { 'file': 'age_3/Holy_War.png', 'cell':'aggression', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'file': 'age_3/Holy_War.png', 'cell':'aggression', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'file': 'age_3/War_over_Culture.png', 'cell':'aggression', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'file': 'age_3/War_over_Culture.png', 'cell':'aggression', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'file': 'age_3/War_over_Culture.png', 'cell':'aggression', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'file': 'age_3/War_over_Culture.png', 'cell':'aggression', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },

                { 'file': 'age_3/International_Tourism.png', 'cell':'pact', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'file': 'age_3/Loss_of_Sovereignity.png', 'cell':'pact', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'file': 'age_3/Military_Pact.png', 'cell':'pact', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'file': 'age_3/Peace_Treaty.png', 'cell':'pact', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },

                { 'file': 'age_3/Entrenchments.png', 'cell':'tactics', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'file': 'age_3/Entrenchments.png', 'cell':'tactics', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'file': 'age_3/Mechanized_Army.png', 'cell':'tactics', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'file': 'age_3/Mechanized_Army.png', 'cell':'tactics', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'file': 'age_3/Modern_Army.png', 'cell':'tactics', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'file': 'age_3/Modern_Army.png', 'cell':'tactics', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'file': 'age_3/Shock_Troops.png', 'cell':'tactics', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' },
                { 'file': 'age_3/Shock_Troops.png', 'cell':'tactics', 'deck': 'III', 'back': 'age_3/Age_III_Military_-_Card_Back.png' }
                ])

        return { 'future': { 'A' : [], 'I': [], 'II': [], 'III': [] },
                 'current': age_a[:6],
                 'current_event': None,
                 'A':       [],
                 'I':       age_I,
                 'II':      age_II,
                 'III':     age_III,
                 'aggressions': [],
                 'pacts': [] }

    def make_shuffled_deck(self):
        ageA = self.shuffle([
                { 'file': 'Alexander_the_Great.png',   'cell': 'leader', 'back': 'Age_A_Civil_-_Card_Back.png' },
                { 'file': 'Aristotle.png',             'cell': 'leader', 'back': 'Age_A_Civil_-_Card_Back.png' },
                { 'file': 'Hammurabi.png',             'cell': 'leader', 'back': 'Age_A_Civil_-_Card_Back.png' },
                { 'file': 'Homer.png',                 'cell': 'leader', 'back': 'Age_A_Civil_-_Card_Back.png' },
                { 'file': 'Julius_Caesar.png',         'cell': 'leader', 'back': 'Age_A_Civil_-_Card_Back.png' },
                { 'file': 'Moses.png',                 'cell': 'leader', 'back': 'Age_A_Civil_-_Card_Back.png' },

                { 'file': 'Colossus.png',              'cell': 'wonder', 'back': 'Age_A_Civil_-_Card_Back.png' },
                { 'file': 'Hanging_Gardens.png',       'cell': 'wonder', 'back': 'Age_A_Civil_-_Card_Back.png' },
                { 'file': 'Library_of_Alexandria.png', 'cell': 'wonder', 'back': 'Age_A_Civil_-_Card_Back.png' },
                { 'file': 'Pyramids.png',              'cell': 'wonder', 'back': 'Age_A_Civil_-_Card_Back.png' },

                { 'file': 'Engineering_Genius.png',    'cell': 'yellow-card', 'back': 'Age_A_Civil_-_Card_Back.png' },
                { 'file': 'Frugality.png',             'cell': 'yellow-card', 'back': 'Age_A_Civil_-_Card_Back.png' },
                { 'file': 'Frugality.png',             'cell': 'yellow-card', 'back': 'Age_A_Civil_-_Card_Back.png' },
                { 'file': 'Ideal_Building_Site.png',   'cell': 'yellow-card', 'back': 'Age_A_Civil_-_Card_Back.png' },
                { 'file': 'Ideal_Building_Site.png',   'cell': 'yellow-card', 'back': 'Age_A_Civil_-_Card_Back.png' },
                { 'file': 'Patriotism.png',            'cell': 'yellow-card', 'back': 'Age_A_Civil_-_Card_Back.png' },
                { 'file': 'Revolutionary_Idea.png',    'cell': 'yellow-card', 'back': 'Age_A_Civil_-_Card_Back.png' },
                { 'file': 'Rich_Land.png',             'cell': 'yellow-card', 'back': 'Age_A_Civil_-_Card_Back.png' },
                { 'file': 'Rich_Land.png',             'cell': 'yellow-card', 'back': 'Age_A_Civil_-_Card_Back.png' },
                { 'file': 'Work_of_Art.png',           'cell': 'yellow-card', 'back': 'Age_A_Civil_-_Card_Back.png' }
                ])

        ageI = self.shuffle([
                { 'file': 'age_1/Bountiful_Harvest.png',       'cell': 'yellow-card', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'file': 'age_1/Breakthrough.png',            'cell': 'yellow-card', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'file': 'age_1/Efficient_Upgrade.png',       'cell': 'yellow-card', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'file': 'age_1/Efficient_Upgrade.png',       'cell': 'yellow-card', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'file': 'age_1/Engineering_Genius.png',      'cell': 'yellow-card', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'file': 'age_1/Frugality.png',               'cell': 'yellow-card', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'file': 'age_1/Ideal_Building_Site_dsn.png', 'cell': 'yellow-card', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'file': 'age_1/Mineral_Deposits_dsn.png',    'cell': 'yellow-card', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'file': 'age_1/Mineral_Deposits_dsn.png',    'cell': 'yellow-card', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'file': 'age_1/Patiotism_Age_1_dsn.png',     'cell': 'yellow-card', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'file': 'age_1/Revolutionary_Idea_dsn.png',  'cell': 'yellow-card', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'file': 'age_1/Rich_Land_dsn.png',           'cell': 'yellow-card', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'file': 'age_1/Work_of_Art.png',             'cell': 'yellow-card', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },

                { 'file': 'age_1/Theology_dsn.png', 'cell': 'theology', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'file': 'age_1/Theology_dsn.png', 'cell': 'theology', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'file': 'age_1/Alchemy.png', 'cell': 'alchemy', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'file': 'age_1/Alchemy.png', 'cell': 'alchemy', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'file': 'age_1/Alchemy.png', 'cell': 'alchemy', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'file': 'age_1/Bread_and_Circuses.png', 'cell': 'bread_and_circuses', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'file': 'age_1/Bread_and_Circuses.png', 'cell': 'bread_and_circuses', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'file': 'age_1/Drama.png', 'cell': 'drama', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'file': 'age_1/Drama.png', 'cell': 'drama', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'file': 'age_1/Iron_dsn.png', 'cell': 'iron', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'file': 'age_1/Iron_dsn.png', 'cell': 'iron', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'file': 'age_1/Iron_dsn.png', 'cell': 'iron', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'file': 'age_1/Irrigation_dsn.png', 'cell': 'irrigation', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'file': 'age_1/Irrigation_dsn.png', 'cell': 'irrigation', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'file': 'age_1/Irrigation_dsn.png', 'cell': 'irrigation', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'file': 'age_1/Printing_Press_1_dsn.png', 'cell': 'printing_press', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'file': 'age_1/Printing_Press_1_dsn.png', 'cell': 'printing_press', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'file': 'age_1/Swordsmen_dsn.png', 'cell': 'swordsmen', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'file': 'age_1/Swordsmen_dsn.png', 'cell': 'swordsmen', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'file': 'age_1/Swordsmen_dsn.png', 'cell': 'swordsmen', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'file': 'age_1/knights_dsn.png', 'cell': 'knights', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'file': 'age_1/knights_dsn.png', 'cell': 'knights', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'file': 'age_1/knights_dsn.png', 'cell': 'knights', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },

                { 'file': 'age_1/Great_Wall_dsn.png', 'cell': 'wonder', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'file': 'age_1/St_Peters_Basilica_dsn.png', 'cell': 'wonder', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'file': 'age_1/Taj_Mahal_dsn.png', 'cell': 'wonder', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'file': 'age_1/universitas_carolina_dsn.png', 'cell': 'wonder', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },

                { 'file': 'age_1/Cartography.png', 'cell': 'cartography', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'file': 'age_1/Code_of_Laws.png', 'cell': 'code_of_laws', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'file': 'age_1/Code_of_Laws.png', 'cell': 'code_of_laws', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'file': 'age_1/Masonry_dsn.png', 'cell': 'masonry', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'file': 'age_1/warfare_dsn.png', 'cell': 'warfare', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'file': 'age_1/warfare_dsn.png', 'cell': 'warfare', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },

                { 'file': 'age_1/Michelangelo_dsn.png', 'cell': 'leader', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'file': 'age_1/Joan_of_Arc_dsn.png', 'cell': 'leader', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'file': 'age_1/Leonardo_da_Vinci_dsn.png', 'cell': 'leader', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'file': 'age_1/Genghis_Khan.png', 'cell': 'leader', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'file': 'age_1/Christopher_Columbus.png', 'cell': 'leader', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'file': 'age_1/Frederick_Barbarrossa.png', 'cell': 'leader', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },

                { 'file': 'age_1/Monarchy_dsn.png', 'cell': 'government', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'file': 'age_1/Monarchy_dsn.png', 'cell': 'government', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' },
                { 'file': 'age_1/Theocracy_dsn.png', 'cell': 'government', 'back': 'age_1/Age_I_Civil_-_Card_Back.png' }
                ])

        ageII = self.shuffle([
                { 'file': 'age_2/Bountiful_Harvest.png', 'cell': 'yellow-card', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
                { 'file': 'age_2/Breakthrough.png', 'cell': 'yellow-card', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
                { 'file': 'age_2/Efficient_Upgrade.png', 'cell': 'yellow-card', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
                { 'file': 'age_2/Efficient_Upgrade.png', 'cell': 'yellow-card', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
                { 'file': 'age_2/Engineering_Genius.png', 'cell': 'yellow-card', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
                { 'file': 'age_2/Frugality.png', 'cell': 'yellow-card', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
                { 'file': 'age_2/Ideal_Building_Site.png', 'cell': 'yellow-card', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
                { 'file': 'age_2/Mineral_Deposits.png', 'cell': 'yellow-card', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
                { 'file': 'age_2/Patriotism.png', 'cell': 'yellow-card', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
                { 'file': 'age_2/Revolutionary_Idea.png', 'cell': 'yellow-card', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
                { 'file': 'age_2/Rich_Land.png', 'cell': 'yellow-card', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
                { 'file': 'age_2/Wave_of_Nationalism.png', 'cell': 'yellow-card', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
                { 'file': 'age_2/Work_of_Art.png', 'cell': 'yellow-card', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },

                { 'file': 'age_2/Selective_Breeding.png', 'cell': 'selective_breeding', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
                { 'file': 'age_2/Selective_Breeding.png', 'cell': 'selective_breeding', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
                { 'file': 'age_2/Coal.png', 'cell': 'coal', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
                { 'file': 'age_2/Coal.png', 'cell': 'coal', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
                { 'file': 'age_2/Organized_Religion.png', 'cell': 'organized_religion', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
                { 'file': 'age_2/Organized_Religion.png', 'cell': 'organized_religion', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
                { 'file': 'age_2/Scientific_Method.png', 'cell': 'scientific_method', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
                { 'file': 'age_2/Scientific_Method.png', 'cell': 'scientific_method', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
                { 'file': 'age_2/Team_Sports.png', 'cell': 'team_sports', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
                { 'file': 'age_2/Journalism.png', 'cell': 'journalism', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
                { 'file': 'age_2/Journalism.png', 'cell': 'journalism', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
                { 'file': 'age_2/Journalism.png', 'cell': 'journalism', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
                { 'file': 'age_2/Opera.png', 'cell': 'opera', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
                { 'file': 'age_2/Opera.png', 'cell': 'opera', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },

                { 'file': 'age_2/Riflemen.png', 'cell': 'riflemen', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
                { 'file': 'age_2/Riflemen.png', 'cell': 'riflemen', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
                { 'file': 'age_2/Cavalrymen.png', 'cell': 'cavalrymen', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
                { 'file': 'age_2/Cavalrymen.png', 'cell': 'cavalrymen', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
                { 'file': 'age_2/Cavalrymen.png', 'cell': 'cavalrymen', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
                { 'file': 'age_2/Cannon.png', 'cell': 'cannon', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
                { 'file': 'age_2/Cannon.png', 'cell': 'cannon', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
                { 'file': 'age_2/Cannon.png', 'cell': 'cannon', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },

                { 'file': 'age_2/Transcontinental_Railroad.png', 'cell': 'wonder', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
                { 'file': 'age_2/Eiffel_Tower.png', 'cell': 'wonder', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
                { 'file': 'age_2/Kremlin.png', 'cell': 'wonder', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
                { 'file': 'age_2/Ocean_Liner_Service.png', 'cell': 'wonder', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },

                { 'file': 'age_2/William_Shakespeare.png', 'cell': 'leader', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
                { 'file': 'age_2/James_Cook.png', 'cell': 'leader', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
                { 'file': 'age_2/Napoleon_Bonaparte.png', 'cell': 'leader', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
                { 'file': 'age_2/Maximilien_Robespierre.png', 'cell': 'leader', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
                { 'file': 'age_2/JS_Bach.png', 'cell': 'leader', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
                { 'file': 'age_2/Isaac_Newton.png', 'cell': 'leader', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },

                { 'file': 'age_2/Constitutional_Monarchy.png', 'cell': 'government', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
                { 'file': 'age_2/Constitutional_Monarchy.png', 'cell': 'government', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
                { 'file': 'age_2/Republic.png', 'cell': 'government', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
                { 'file': 'age_2/Republic.png', 'cell': 'government', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },

                { 'file': 'age_2/Strategy.png', 'cell': 'strategy', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
                { 'file': 'age_2/Justice_System.png', 'cell': 'justice_system', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
                { 'file': 'age_2/Justice_System.png', 'cell': 'justice_system', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
                { 'file': 'age_2/Navigation.png', 'cell': 'navigation', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
                { 'file': 'age_2/Architecture.png', 'cell': 'architecture', 'back': 'age_2/Age_II_Civil_-_Card_Back.png' },
                { 'file': 'age_2/Architecture.png', 'cell': 'architecture', 'back': 'age_2/Age_II_Civil_-_Card_Back.png'  }
                ])

        ageIII = self.shuffle([
                { 'file': 'age_3/Bountiful_Harvest.png', 'cell':'yellow-card', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
                { 'file': 'age_3/Efficient_Upgrade.png', 'cell':'yellow-card', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
                { 'file': 'age_3/Endowment_for_the_Arts.png', 'cell':'yellow-card', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
                { 'file': 'age_3/Engineering_Genius.png', 'cell':'yellow-card', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
                { 'file': 'age_3/Ideal_Building_Site.png', 'cell':'yellow-card', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
                { 'file': 'age_3/Civil_Build-Up.png', 'cell':'yellow-card', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
                { 'file': 'age_3/Mineral_Deposits.png', 'cell':'yellow-card', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
                { 'file': 'age_3/Patriotism.png', 'cell':'yellow-card', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
                { 'file': 'age_3/Revolutionary_Idea.png', 'cell':'yellow-card', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
                { 'file': 'age_3/Work_of_Art.png', 'cell':'yellow-card', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },

                { 'file': 'age_3/Mechanized_Agriculture.png', 'cell':'mechanized_agriculture', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
                { 'file': 'age_3/Mechanized_Agriculture.png', 'cell':'mechanized_agriculture', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
                { 'file': 'age_3/Oil.png', 'cell':'oil', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
                { 'file': 'age_3/Oil.png', 'cell':'oil', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
                { 'file': 'age_3/Computers.png', 'cell':'computers', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
                { 'file': 'age_3/Computers.png', 'cell':'computers', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
                { 'file': 'age_3/Professional_Sports.png', 'cell':'professional_sports', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
                { 'file': 'age_3/Professional_Sports.png', 'cell':'professional_sports', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
                { 'file': 'age_3/Multimedia.png', 'cell':'multimedia', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
                { 'file': 'age_3/Multimedia.png', 'cell':'multimedia', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
                { 'file': 'age_3/Movies.png', 'cell':'movies', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
                { 'file': 'age_3/Movies.png', 'cell':'movies', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },

                { 'file': 'age_3/Modern_Infantry.png', 'cell':'modern_infantry', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
                { 'file': 'age_3/Modern_Infantry.png', 'cell':'modern_infantry', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
                { 'file': 'age_3/Tanks.png', 'cell':'tanks', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
                { 'file': 'age_3/Tanks.png', 'cell':'tanks', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
                { 'file': 'age_3/Rockets.png', 'cell':'rockets', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
                { 'file': 'age_3/Rockets.png', 'cell':'rockets', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
                { 'file': 'age_3/Rockets.png', 'cell':'rockets', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
                { 'file': 'age_3/Air_Forces.png', 'cell':'air_forces', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
                { 'file': 'age_3/Air_Forces.png', 'cell':'air_forces', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
                { 'file': 'age_3/Air_Forces.png', 'cell':'air_forces', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },

                { 'file': 'age_3/Hollywood.png', 'cell':'wonder', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
                { 'file': 'age_3/Internet.png', 'cell':'wonder', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
                { 'file': 'age_3/First_Space_Flight.png', 'cell':'wonder', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
                { 'file': 'age_3/Fast_Food_Chains.png', 'cell':'wonder', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },

                { 'file': 'age_3/Albert_Einstein.png', 'cell':'leader', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
                { 'file': 'age_3/Mahatma_Gandhi.png', 'cell':'leader', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
                { 'file': 'age_3/Rock_and_Roll_Icon.png', 'cell':'leader', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
                { 'file': 'age_3/Nikola_Tesla.png', 'cell':'leader', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
                { 'file': 'age_3/Winston_Churchill.png', 'cell':'leader', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
                { 'file': 'age_3/Game_Designer.png', 'cell':'leader', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },

                { 'file': 'age_3/Communism.png', 'cell':'government', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
                { 'file': 'age_3/Democracy.png', 'cell':'government', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
                { 'file': 'age_3/Democracy.png', 'cell':'government', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
                { 'file': 'age_3/Fundamentalism.png', 'cell':'government', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },

                { 'file': 'age_3/Civil_Theory.png', 'cell':'military_theory', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
                { 'file': 'age_3/Civil_Theory.png', 'cell':'military_theory', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
                { 'file': 'age_3/Civil_Service.png', 'cell':'civil_service', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
                { 'file': 'age_3/Satellites.png', 'cell':'satellites', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
                { 'file': 'age_3/Engineering.png', 'cell':'engineering', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' },
                { 'file': 'age_3/Engineering.png', 'cell':'engineering', 'back': 'age_3/Age_III_Civil_-_Card_Back.png' }
                ])

        return ageA + ageI + ageII + ageIII


    def shuffle(self, cards):
        shuffled = []
        for i in range(len(cards)):
            index = random.randint(0,len(cards) - 1)
            shuffled.append(cards.pop(index))

        return shuffled

    def make_initial_civ(self):
        civ = { 'government':  { 'file': 'Despotism.png',   'blue': 0, 'yellow': 0 },
                'philosophy':  { 'file': 'Philosophy.png',  'blue': 0, 'yellow': 1 },
                'religion':    { 'file': 'Religion.png',    'blue': 0, 'yellow': 0 },
                'bronze':      { 'file': 'Bronze.png',      'blue': 0, 'yellow': 2 },
                'agriculture': { 'file': 'Agriculture.png', 'blue': 0, 'yellow': 2 },
                'warriors':    { 'file': 'Warriors.png',    'blue': 0, 'yellow': 1 },
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
        return { 'p1': civ, 'p2': civ, 'p3': civ, 'p4': civ }

    def undo(self, branch):
        proc = Popen(('git', 'update-ref', "refs/heads/" + branch, branch + '~1'),
                     env = { "GIT_DIR":self.git_dir },
                     stdin = PIPE,
                     stdout = PIPE,
                     stderr = PIPE)

        out, err = proc.communicate()

    def serialize_object(self, object):
        serialized = simplejson.dumps(object, sort_keys=True, indent=3)
        print serialized
        return serialized

    def write_deck(self, branch, deck, commit_msg="WRITE DECK"):
        return self.write_game(branch, { 'deck': deck, 'civ': self.get_civ(branch), 'military': self.get_military(branch) }, commit_msg)

    def write_civ(self, branch, civ, commit_msg="WRITE CIV"):
        return self.write_game(branch, { 'deck': self.get_deck(branch), 'civ': civ, 'military': self.get_military(branch) }, commit_msg)

    def write_game(self, branch, game, commit_msg="DEFAULT COMMIT"):
        serialized = self.serialize_object(game)
        proc = Popen(('git', 'hash-object', '-w', '--stdin'),
                     env = { "GIT_DIR":self.git_dir },
                     stdin = PIPE,
                     stdout = PIPE,
                     stderr = PIPE)

        out, err = proc.communicate(serialized)
        print out.rstrip()
        print err
        tree = "100644 blob " + out.rstrip() + "\t" + "deck"

        proc = Popen(('git', 'mktree'),
                     env = { "GIT_DIR":self.git_dir },
                     stdin = PIPE,
                     stdout = PIPE,
                     stderr = PIPE)

        out, err = proc.communicate(tree)
        tree_hash = out.rstrip()
        print out.rstrip()
        print err

        proc = Popen(('git', 'ls-tree', tree_hash),
                     env = { "GIT_DIR":self.git_dir },
                     stdin = PIPE,
                     stdout = PIPE,
                     stderr = PIPE)

        out, err = proc.communicate()
        print out.rstrip()
        print err

        proc = Popen(('git', 'commit-tree', tree_hash, '-p', branch),
                     env = { "GIT_DIR":self.git_dir },
                     stdin = PIPE,
                     stdout = PIPE,
                     stderr = PIPE)

        out, err = proc.communicate(commit_msg)
        print out.rstrip()
        print err

        proc = Popen(('git', 'update-ref', "refs/heads/" + branch, out.rstrip()),
                     env = { "GIT_DIR":self.git_dir },
                     stdin = PIPE,
                     stdout = PIPE,
                     stderr = PIPE)

    def get_game(self, branch):
        proc = Popen(('git', 'ls-tree', '-z', branch),
                     env = { "GIT_DIR":self.git_dir },
                     stdin = PIPE,
                     stdout = PIPE,
                     stderr = PIPE)

        ls_tree_pattern = re.compile('((\d{6}) (tree|blob)) ([0-9a-f]{40})\t(.+)$')

        out, err = proc.communicate()
        lines = out.rstrip().split('\0')
        print lines

        for line in lines:
            if not line: continue
            match = ls_tree_pattern.match(line)
            if not match: continue
            if not match.group(5) == 'deck': continue

            hash = match.group(4)
            print hash


        proc = Popen(('git', 'cat-file', 'blob',  hash),
                     env = { "GIT_DIR":self.git_dir },
                     stdin = PIPE,
                     stdout = PIPE,
                     stderr = PIPE)
        out, err = proc.communicate()
        contents = out
        game = simplejson.loads(contents)
        return game

    def get_deck(self, branch):
        return self.get_game(branch)['deck']

    def get_civ(self, branch):
        return self.get_game(branch)['civ']

    def get_military(self, branch):
        return self.get_game(branch)['military']

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
        print out
        print err
