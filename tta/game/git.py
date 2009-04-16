#!/usr/bin/env python

import random
from django.utils import simplejson

import os
import re
from subprocess import Popen, PIPE

git_dir = '/home/cjh/tta_game/'

def make_age_a_military():
    age_a = shuffle([{ 'file': 'Development_of_Agriculture.png',  'cell': 'event', 'deck': 'A' },
                     { 'file': 'Development_of_Crafts.png',       'cell': 'event', 'deck': 'A' },
                     { 'file': 'Development_of_Markets.png',      'cell': 'event', 'deck': 'A' },
                     { 'file': 'Development_of_Politics.png',     'cell': 'event', 'deck': 'A' },
                     { 'file': 'Development_of_Religion.png',     'cell': 'event', 'deck': 'A' },
                     { 'file': 'Development_of_Science.png',      'cell': 'event', 'deck': 'A' },
                     { 'file': 'Development_of_Settlement.png',   'cell': 'event', 'deck': 'A' },
                     { 'file': 'Development_of_Trade_Routes.png', 'cell': 'event', 'deck': 'A' },
                     { 'file': 'Development_of_Warfare.png',      'cell': 'event', 'deck': 'A' },
                     { 'file': 'No_Event.png',                    'cell': 'event', 'deck': 'A' }])

    age_I = shuffle([{ 'file': 'age_1/Barbarians.png', 'cell': 'event', 'deck': 'I' },
                     { 'file': 'age_1/Border_Conflict.png', 'cell': 'event', 'deck': 'I' },
                     { 'file': 'age_1/Crusades.png', 'cell': 'event', 'deck': 'I' },
                     { 'file': 'age_1/Cultural_Influence.png', 'cell': 'event', 'deck': 'I' },
                     { 'file': 'age_1/Developed_Territory.png', 'cell': 'event', 'deck': 'I' },
                     { 'file': 'age_1/Enslave.png', 'cell': 'event', 'deck': 'I' },
                     { 'file': 'age_1/Fertile_Territory.png', 'cell': 'event', 'deck': 'I' },
                     { 'file': 'age_1/Fighting_Band.png', 'cell': 'tactics', 'deck': 'I' },
                     { 'file': 'age_1/Foray.png', 'cell': 'event', 'deck': 'I' },
                     { 'file': 'age_1/Good_Harvest.png', 'cell': 'event', 'deck': 'I' },
                     { 'file': 'age_1/Heavy_Cavalry.png', 'cell': 'event', 'deck': 'I' },
                     { 'file': 'age_1/Historic_Territory.png', 'cell': 'event', 'deck': 'I' },
                     { 'file': 'age_1/Immigration.png', 'cell': 'event', 'deck': 'I' },
                     { 'file': 'age_1/Inhabited_Territory.png', 'cell': 'event', 'deck': 'I' },
                     { 'file': 'age_1/Legion.png', 'cell': 'tactics', 'deck': 'I' },
                     { 'file': 'age_1/Light_Cavalry.png', 'cell': 'tactics', 'deck': 'I' },
                     { 'file': 'age_1/medieval_army.png', 'cell': 'tactics', 'deck': 'I' },
                     { 'file': 'age_1/new_Deposits.png', 'cell': 'event', 'deck': 'I' },
                     { 'file': 'age_1/Open_Borders_Agreement.png', 'cell': 'event', 'deck': 'I' },
                     { 'file': 'age_1/Pestilence.png', 'cell': 'event', 'deck': 'I' },
                     { 'file': 'age_1/Phalanx.png', 'cell': 'tactics', 'deck': 'I' },
                     { 'file': 'age_1/Plunder.png', 'cell': 'event', 'deck': 'I' },
                     { 'file': 'age_1/Raiders.png', 'cell': 'event', 'deck': 'I' },
                     { 'file': 'age_1/Raid.png', 'cell': 'event', 'deck': 'I' },
                     { 'file': 'age_1/Rats.png', 'cell': 'event', 'deck': 'I' },
                     { 'file': 'age_1/Rebellion.png', 'cell': 'event', 'deck': 'I' },
                     { 'file': 'age_1/Reign_of_Terror.png', 'cell': 'event', 'deck': 'I' },
                     { 'file': 'age_1/scientific_breakthrough.png', 'cell': 'event', 'deck': 'I' },
                     { 'file': 'age_1/strategic_territory.png', 'cell': 'event', 'deck': 'I' },
                     { 'file': 'age_1/Trade_Route_Agreements.png', 'cell': 'event', 'deck': 'I' },
                     { 'file': 'age_1/Uncertain_Borders.png', 'cell': 'event', 'deck': 'I' },
                     { 'file': 'age_1/Wealthy_Territory.png', 'cell': 'event', 'deck': 'I' }])

    return { 'future': { 'A' : [], 'I': [], 'II': [], 'III': [] },
             'current': age_a[:6],
             'A':       [],
             'I':       age_I,
             'II':      [],
             'III':     [] }

def make_shuffled_deck():
    ageI = shuffle([{ 'file': 'Alexander_the_Great.png',   'cell': 'leader' },
                    { 'file': 'Aristotle.png',             'cell': 'leader' },
                    { 'file': 'Colossus.png',              'cell': 'wonder' },
                    { 'file': 'Engineering_Genius.png',    'cell': 'yellow-card' },
                    { 'file': 'Frugality.png',             'cell': 'yellow-card' },
                    { 'file': 'Hammurabi.png',             'cell': 'leader' },
                    { 'file': 'Hanging_Gardens.png',       'cell': 'wonder' },
                    { 'file': 'Homer.png',                 'cell': 'leader' },
                    { 'file': 'Ideal_Building_Site.png',   'cell': 'yellow-card' },
                    { 'file': 'Julius_Caesar.png',         'cell': 'leader' },
                    { 'file': 'Library_of_Alexandria.png', 'cell': 'wonder' },
                    { 'file': 'Moses.png',                 'cell': 'leader' },
                    { 'file': 'Patriotism.png',            'cell': 'yellow-card' },
                    { 'file': 'Pyramids.png',              'cell': 'wonder' },
                    { 'file': 'Revolutionary_Idea.png',    'cell': 'yellow-card' },
                    { 'file': 'Rich_Land.png',             'cell': 'yellow-card' },
                    { 'file': 'Work_of_Art.png',           'cell': 'yellow-card' }])

    ageII = shuffle([{ 'file': 'age_1/Alchemy.png', 'cell': 'alchemy' },
                     { 'file': 'age_1/Bountiful_Harvest.png', 'cell': 'yellow-card' },
                     { 'file': 'age_1/Bread_and_Circuses.png', 'cell': 'bread_and_circuses' },
                     { 'file': 'age_1/Christopher_Columbus.png', 'cell': 'leader' },
                     { 'file': 'age_1/Drama.png', 'cell': 'drama' },
                     { 'file': 'age_1/Efficient_Upgrade.png', 'cell': 'yellow-card' },
                     { 'file': 'age_1/Engineering_Genius.png', 'cell': 'yellow-card' },

                     { 'file': 'age_1/Frederick_Barbarrossa.png', 'cell': 'leader' },
                     { 'file': 'age_1/Frugality.png', 'cell': 'yellow-card' },
                     { 'file': 'age_1/Genghis_Khan.png', 'cell': 'leader' },
                     { 'file': 'age_1/Great_Wall_dsn.png', 'cell': 'wonder' },
                     { 'file': 'age_1/Ideal_Building_Site_dsn.png', 'cell': 'yellow-card' },
                     { 'file': 'age_1/Iron_4_player.png', 'cell': 'iron' },
                     { 'file': 'age_1/Iron_dsn.png', 'cell': 'iron' },
                     { 'file': 'age_1/Irrigation_4_player.png', 'cell': 'irrigation' },
                     { 'file': 'age_1/Irrigation_dsn.png', 'cell': 'irrigation' },
                     { 'file': 'age_1/Joan_of_Arc_dsn.png', 'cell': 'leader' },
                     { 'file': 'age_1/knights_4_player.png', 'cell': 'knights' },
                     { 'file': 'age_1/knights_dsn.png', 'cell': 'knights' },
                     { 'file': 'age_1/Leonardo_da_Vinci_dsn.png', 'cell': 'leader' },
#                      { 'file': 'age_1/Masonry_dsn.png', 'cell': 'leader' },
                     { 'file': 'age_1/Michelangelo_dsn.png', 'cell': 'leader' },
                     { 'file': 'age_1/Mineral_Deposits_dsn.png', 'cell': 'yellow-card' },
                     { 'file': 'age_1/Monarchy_3_player.png', 'cell': 'government' },
                     { 'file': 'age_1/Monarchy_dsn.png', 'cell': 'government' },
                     { 'file': 'age_1/Patiotism_Age_1_dsn.png', 'cell': 'yellow-card' },
                     { 'file': 'age_1/Printing_Press_1_dsn.png', 'cell': 'printing_press' },
                     ])


    return ageI + ageII

     
def shuffle(cards):
    shuffled = []
    for i in range(len(cards)):
        index = random.randint(0,len(cards) - 1)
        shuffled.append(cards.pop(index))

    return shuffled

def make_initial_civ():
    civ = { 'government':  { 'file': 'Despotism.png',   'blue': 0, 'yellow': 0 },
            'philosophy':  { 'file': 'Philosophy.png',  'blue': 0, 'yellow': 1 },
            'religion':    { 'file': 'Religion.png',    'blue': 0, 'yellow': 0 },
            'bronze':      { 'file': 'Bronze.png',      'blue': 0, 'yellow': 2 },
            'agriculture': { 'file': 'Agriculture.png', 'blue': 0, 'yellow': 2 },
            'warriors':    { 'file': 'Warriors.png',    'blue': 0, 'yellow': 1 },
            'hand': [ { 'file': 'Development_of_Science.png', 'cell': 'event', 'deck': 'A' },],
            'unused_workers': 1,
            'yellow_tokens': 18,
            'culture': 0,
            'culture_plus': 0,
            'tech': 0,
            'tech_plus': 1,
            'strength': 1,
            'blue_tokens': 18}
    return { 'p1': civ, 'p2': civ, 'p3': civ, 'p4': civ }

def undo(branch):
    proc = Popen(('git', 'update-ref', "refs/heads/" + branch, branch + '~1'),
                 env = { "GIT_DIR":git_dir },
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
     
    out, err = proc.communicate()

def serialize_object(object):
    serialized = simplejson.dumps(object, sort_keys=True, indent=3)
    print serialized
    return serialized

def write_deck(branch, deck, commit_msg="WRITE DECK"):
    return write_game(branch, { 'deck': deck, 'civ': get_civ(branch), 'military': get_military(branch) }, commit_msg)

def write_civ(branch, civ, commit_msg="WRITE CIV"):
    return write_game(branch, { 'deck': get_deck(branch), 'civ': civ, 'military': get_military(branch) }, commit_msg)

def write_game(branch, game, commit_msg="DEFAULT COMMIT"):
    serialized = serialize_object(game)
    proc = Popen(('git', 'hash-object', '-w', '--stdin'),
                 env = { "GIT_DIR":git_dir },
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
     
    out, err = proc.communicate(serialized)
    print out.rstrip()
    print err
    tree = "100644 blob " + out.rstrip() + "\t" + "deck"
     
    proc = Popen(('git', 'mktree'),
                 env = { "GIT_DIR":git_dir },
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
     
    out, err = proc.communicate(tree)
    tree_hash = out.rstrip()
    print out.rstrip()
    print err

    proc = Popen(('git', 'ls-tree', tree_hash),
                 env = { "GIT_DIR":git_dir },
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
     
    out, err = proc.communicate()
    print out.rstrip()
    print err
     
    proc = Popen(('git', 'commit-tree', tree_hash, '-p', branch),
                 env = { "GIT_DIR":git_dir },
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
     
    out, err = proc.communicate(commit_msg)
    print out.rstrip()
    print err

    proc = Popen(('git', 'update-ref', "refs/heads/" + branch, out.rstrip()),
                 env = { "GIT_DIR":git_dir },
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)

def get_game(branch):
    proc = Popen(('git', 'ls-tree', '-z', branch),
                 env = { "GIT_DIR":git_dir },
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
                 env = { "GIT_DIR":git_dir },
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate()
    contents = out
    game = simplejson.loads(contents)
    return game

def get_deck(branch):
    return get_game(branch)['deck']

def get_civ(branch):
    return get_game(branch)['civ']

def get_military(branch):
    return get_game(branch)['military']

def create_branch_at_master_head(branch):
    proc = Popen(('git', 'branch', branch, 'master'),
                 env = { "GIT_DIR":git_dir },
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)

    out, err = proc.communicate()


def replace_master_with_branch(branch):
    game = get_deck(branch)
    write_game('master', game, "replacing master with " + branch)

    delete_branch(branch)

def delete_branch(branch):
    proc = Popen(('git', 'branch', '-D', branch),
                 env = { "GIT_DIR":git_dir },
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)

    out, err = proc.communicate()
    print out
    print err
