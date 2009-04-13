#!/usr/bin/env python

import random
from django.utils import simplejson

import os
import re
from subprocess import Popen, PIPE

git_dir = '/home/cjh/tta_game/'

def make_shuffled_deck():
    cards = ['Alexander_the_Great.png',
             'Aristotle.png',
             'Colossus.png',
             'Despotism.png',
             'Engineering_Genius.png',
             'Frugality.png',
             'Hammurabi.png',
             'Hanging_Gardens.png',
             'Homer.png',
             'Ideal_Building_Site.png',
             'Julius_Caesar.png',
             'Library_of_Alexandria.png',
             'Moses.png',
             'Patriotism.png',
             'Pyramids.png',
             'Revolutionary_Idea.png',
             'Rich_Land.png',
             'Work_of_Art.png']
     
    shuffled = []
    for i in range(len(cards)):
        index = random.randint(0,len(cards) - 1)
        shuffled.append(cards.pop(index))

    return shuffled

def undo(branch):
    proc = Popen(('git', 'update-ref', "refs/heads/" + branch, branch + '~1'),
                 env = { "GIT_DIR":git_dir },
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
     
    out, err = proc.communicate()

def serialize_deck(deck):
    serialized = simplejson.dumps(deck, sort_keys=True, indent=3)
    print serialized
    return serialized

def write_deck(branch, deck, commit_msg="DEFAULT COMMIT"):
    serialized = serialize_deck(deck)
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

def get_deck(branch):
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
    deck = simplejson.loads(contents)
    return deck

def create_branch_at_master_head(branch):
    proc = Popen(('git', 'branch', branch, 'master'),
                 env = { "GIT_DIR":git_dir },
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)

    out, err = proc.communicate()


def replace_master_with_branch(branch):
    deck = get_deck(branch)
    write_deck('master', deck, "replacing master with " + branch)

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
