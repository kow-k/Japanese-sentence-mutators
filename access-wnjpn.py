#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, os
#from subprocess import Popen, PIPE
import sqlite3
import random
from pprint import pprint
from numpy import unique
from collections import namedtuple

import io
out_enc    = in_enc = "utf-8"
sys.stdin  = io.TextIOWrapper(sys.stdin.buffer, encoding = in_enc)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding = out_enc)

### classes

make_sense = namedtuple('sense', 'synset, lemma, pos')
make_link  = namedtuple('link', 'hypo, hype')

### functions

# def less(data):
# 	process = Popen(["less"], stdin=PIPE)
# 	try:
# 		process.stdin.write(data)
# 		process.communicate()
# 	except IOError as e:
# 		pass

def get_senses(term, pos, lang='jpn'):

	q = '''
	select synset, lemma, pos from sense, word where
		lemma=? and word.pos=? and word.lang=?
	'''
	R = cursor.execute(q, (term, pos, lang)).fetchall()
	#return unique(R) # this is harmful
	S = list(set(R)) # implements unique(...) for list
	#R = [ ]
	#for s in S: R.append(make_sense(*s))
	return [ make_sense(*s) for s in S ]

def get_instances(sense, pos, lang='jpn'):

	q = '''
	select synset, lemma, pos from sense, word where
	synset=? and word.pos=? and word.lang=? and word.wordid=sense.wordid
	'''
	R = cursor.execute(q, (sense.synset, pos, lang)).fetchall()
	return [ make_sense(*r) for r in R ]

def gather_instances(senses, pos, lang='jpn'):

	W = [ ]
	for sense in senses:
		for s in get_instances(sense, pos, lang):
			if s in W: pass
			else:      W.append(s)
	return W

def extract_terms(senses, pos):

	S = [ sense.lemma for sense in senses if sense.pos == pos ]
	R = [ ]
	for s in S:
		if s in R: pass
		else: R.append(s)
	return R

def get_links(synset, type):

	if type == 'hypo':
		q = '''
		select synset1, synset2 from synlink where synset2=? and link=?
		'''
		R = cursor.execute(q, (synset, 'hype'))
		return [ make_link(*r) for r in R.fetchall() ]
	elif type == 'hype':
		q = '''
		select synset1, synset2 from synlink where synset1=? and link=?
		'''
		R = cursor.execute(q, (synset, 'hype'))
		return [ make_link(*r) for r in R.fetchall() ]

def explore_sense(sense, pos, lang='jpn'):

	print("# exploring sense: %s" % (sense, ))
	print("# the sense has synset mates:")
	L = get_instances(sense, pos)
	if len(L) > 0:
		for i, term in enumerate(L):
			i += 1
			print("# synset mate #%d: %s"  % (i, term))
	else:
		print("# --none--")
	#
	if args.hyper:
		print("# the sense has hypernymic links:")
		L = get_links(sense.synset, 'hype')
		if len(L) == 0:
			print("# --none--")
		else:
			for i, link in enumerate():
				i += 1
				print("# link %d. %s" % (i, link))
				s_temp = make_sense((link.hype, "", pos))
				for j, term in enumerate(get_instances(s_temp, pos)):
					j += 1
					print("# hypernym #%d.%d: %s" % (i, j, term))
	if args.hypo:
		print("# the sense has hyponymic links:")
		L = get_links(sense.synset, 'hypo')
		if len(L) == 0:
			print("# --none--")
		else:
			for i, link in enumerate(L):
				i += 1
				print("# link %d. %s" % (i, link))
				s_temp = make_sense((link.hypo, "", pos))
				for j, term in enumerate(get_instances(s_temp, pos)):
					j += 1
					print("# hyponym #%d.%d: %s" % (i, j, term))

def collect_hyposynsets(sense, pos, R, depth, lang='jpn'):

	if args.debug:
		print("# input: %s" % (sense, ))
	#depth = 0
	while args.depth <= depth:
		depth -= 1
		C = get_children(sense, pos)
		if len(C) > 0:
			if args.debug:
				print("# %s has children" % (sense, ))
			for c in C:
				if args.debug:
					print("# sub sense: %s" % (c, ))
				R.append(c)
				return collect_hyposynsets(make_sense(*c), pos, R, depth, lang)
		else:
			R.append(sense)
	return R

def get_children(sense, pos, lang='jpn'):

	q = '''
	select synset, lemma, pos from word, sense, synlink where
	word.wordid=sense.wordid and sense.synset=synset1 and synset2=? and link=?
	and word.pos=? and word.lang=?
	'''
	R = cursor.execute(q, (sense.synset, 'hype', pos, lang)).fetchall()
	#return R
	R = [ make_sense(*x) for x in R ] # This is crucial
	return [ s for s in R if s.synset[-1] == pos ] # This additional fiter is needed

def has_children(sense, pos, lang='jpn'):

	R = get_children(sense, pos, lang)
	if len(R) == 0:
		return False
	else:
		return True

###

if __name__ == '__main__':

	import argparse
	# Commandline options
	parser = argparse.ArgumentParser(description = "Utility for using WordNet-Ja")
	parser.add_argument('--path_to_db', type=str, help='Path to SQLite3 database (e.g., /Users/you/directory/wnjpn.db)', default='wnjpn.db')
	parser.add_argument('--debug', action='store_true', help='debug')
	parser.add_argument('--verbose', action='store_true', help='enables verbose messaging', default=False)
	parser.add_argument('--random', action='store_true', help='enables random choice', default=False)
	parser.add_argument('--term', type=str, help='term for lookup', default='見本')
	parser.add_argument('--pos', type=str, help='pos (n, v, a) for term lookup', default='n')
	parser.add_argument('--explore', action='store_true', help='explores senses', default=False)
	parser.add_argument('--hyper', action='store_true', help='shows hypernyms', default=False)
	parser.add_argument('--hypo', action='store_true', help='shows hyponyms', default=False)
	parser.add_argument('--collect_hyponyms', action='store_true', help='collect hyponyms of a term and show them', default=False)
	parser.add_argument('--depth', type=int, help='depth at which to stop search for hypronyms', default=5)
	parser.add_argument('--index', type=int, help='index for sense to explore')
	parser.add_argument('--sample', type=int, help='number of sense samples to explore or collect instances')
	#
	args = parser.parse_args()

   # implications
	try:
		if args.debug:
			args.verbose = True
		if args.debug:
			print("encoding: %s" % sys.getdefaultencoding())
		#
		conn = sqlite3.connect(args.path_to_db)
		cursor = conn.cursor()
		#
		term, pos = args.term, args.pos
		print("# processing: %s, %s" % (term, pos))
		#
		senses = get_senses(term, pos)
		print("# it has %d senses:" % len(senses) )
		if args.debug:
			for sense in senses:
				print(sense)
		# process
		if args.explore:
			if args.random:
				chosen_sense = random.choice(senses)
				explore_sense(chosen_sense, pos)
			elif args.index:
				explore_sense(senses[args.index - 1], pos)
			else:
				if args.sample:
					senses = random.sample(senses, args.sample)
				for i, sense in enumerate(senses):
					i += 1
					print("# sampled sense #%d" % (i, ))
					explore_sense(sense, pos)
					print("# has children: %s" % (has_children(sense, pos), ))

		#
		if args.collect_hyponyms:
			if args.debug:
				print("# collecting hyposynsets")
			#dummy = make_sense('00000000-n', 'dummy', 'n')
			if args.sample:
				senses = random.sample(senses, args.sample)
			H = [ ]
			for i, sense in enumerate(senses):
				i += 1
				Hx = collect_hyposynsets(sense, pos, [ ], args.depth)
				if args.verbose:
					print("# %d/%d collected %d hyposynset(s) of %s:" % (i, len(senses), len(Hx), sense))
					print(Hx)
				# make a unique list
				for s in Hx:
					if s in H: pass
					else:      H.append(s)
			#
			pprint(H)
			print("# collected %d hyposynsets" % len(H))
			#
			print("# gathered hyponyms:")
			G = gather_instances(H, pos)
			G.extend(H) # Don't do X = G.extend(H) which doesn't work
			if args.verbose:
				pprint(sorted(G))
			print("# terms only:")
			pprint(sorted(extract_terms(G, pos)))
			print("# %d items" % len(G))

	except EOFError:
		pass

### end of script
