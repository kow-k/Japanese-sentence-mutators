

import random
import sqlite3
from pprint import pprint
from collections import namedtuple

def safe_chain(s, t, interval = ' '):
    if s[-1] != " " and t[0] != 0:　return s + interval + t
    else:　return s + t

#
term = ('黙る', 'v')
term_pos = term[-1]

q = "select synset, word.lemma from sense, word"
q = safe_chain(q, "where word.lemma=? and word.wordid = sense.wordid and word.pos=?")
q = safe_chain(q, "limit 50")
synsets = conn.execute(q, term)
filtered_synsets = [ x for x in set(synsets) if x[0][-1] == term_pos ]
chosen_synset = random.choice(filtered_synsets)
chosen_synsetid = chosen_synset

q = "select word.* from sense, word"
q = safe_chain(q, "where word.lang=? and word.wordid = sense.wordid and synset=?")
synset_mates = conn.execute(q, ('jpn', chosen_synsetid))

selected = random.choice(synset_mates)
print("selection: %s" % (selected,))
new_term = selected[2]

###

chosen_sense = random.choice(C)
print("chosen sense: %s" % (chosen_sense,))
chosen_synsetid = chosen_sense[0]


C = []
for synset in synsets:
    print(synset); C.append(synset)
C = [ x for x in set(C) if x[0][-1] == term_pos ]
pprint("candidate %d senses: %s" % (len(C), C))

chosen_sense = random.choice(C)
print("chosen sense: %s" % (chosen_sense,))
chosen_synsetid = chosen_sense[0]

q = "select word.* from sense, word"
q = safe_chain(q, "where word.lang=? and word.wordid = sense.wordid and synset=?")
synset_mates = conn.execute(q, ('jpn', chosen_synsetid))

print("instances of %s:" % chosen_synsetid)
X = [ ]
for i, x in enumerate(synset_mates):
    print(i, x); X.append(x)

selected = random.choice(X)
print("selection: %s" % (selected,))
new_term = selected[2]
print("new term: %s" % new_term)
