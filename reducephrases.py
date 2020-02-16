#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2016-2020 Kow Kuroda
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#	 http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os
import sys
import string
import re
import Struc
import random
import CaboCha
from itertools import combinations

import io
out_enc = in_enc = "utf-8"
sys.stdin  = io.TextIOWrapper(sys.stdin.buffer, encoding=in_enc)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding=out_enc)

# Functions
def process(sentence, targets, header, headersep):

	phrases = [ ]
	for c in sentence:
		temp = ''
		for m in c['morphs']:
			line = re.split('\t', m)
			temp += line[0]
		phrases.append(temp)
	#
	for i in range(len(phrases)):
		if i not in targets and i != (len(phrases) - 1):
			phrases[sentence[i]['link']] = phrases[i] + phrases[sentence[i]['link']]
			phrases[i] = ''
	phrases = [ x for x in phrases if x != '' ]
	if args.debug:
		print("# phrases before popping: %s" % phrases)
	# 最後の chunkは固定
	pred = phrases.pop()
	# 削除対象の抽出
	phraseindices = [ ]
	for i in range(0, len(phrases)):
		if args.exclude_wa:
			if not re.search('は(?:$|(?:，|、)$)', phrases[i]):
				phraseindices.append(i)
		else:
			phraseindices.append(i)
	if args.debug:
		print('# Phrases: %s' % phrases)
		print('# Reduction candidates: %s' % phraseindices)
	reductions = reduce(phrases, phraseindices, pred)
	if args.debug:
		print(reductions)
	for i, reduction in enumerate(reductions):
		if len(reduction) > 0:
			print(header + headersep + " " + reduction[0] + "[degree %d]" % (reduction[1]))
		else:
			print("# Reduction didn't apply")

def reduce(phrases, phraseindices, pred):
	# 削除する項を一つずつ増やしていく
	# 終了条件
	end = args.lb
	degree = 1
	reductions = [ ]
	while True:
		if len(phrases) - degree < end:
			text = ''.join(phrases) + pred
			reductions.append((text, 0))
			break
		else:
			if args.debug:
				print('## Delete', degree, 'phrase(s)')
			rests = combinations(phraseindices, degree)
			for r in rests:
				results = [ ]
				for i in range(0, len(phrases)):
					if not i in r:
						results.append(phrases[i])
				text = ''.join(results) + pred
				#reductions.append(text)
				reductions.append((text, degree)) # return text, degree pair
				#print(header + headersep + text + "[reduced %d phrase(s)]" % degree)
			degree += 1
	return reductions

if __name__ == '__main__':

	import argparse
	# コマンドラインオプション
	ap = argparse.ArgumentParser(description = "主節の述語に係る句を削除する")
	ap.add_argument('--debug', action = 'store_true', help = 'debug')
	ap.add_argument('--exclude_wa', action = 'store_true', help = '"NPは" を削除しない')
	ap.add_argument('--lb', type = int, help = '除去して残る句の数の下限 (default:2)', default = 2)
	ap.add_argument('--silent', action = 'store_true', help = '入力の非表示')
	ap.add_argument('--headersep', type = str, help = 'ヘッダーの区切り記号', default = ':')
	ap.add_argument('--commentchar', type = str, help = 'コメント行の識別記号', default = '%')
	#
	args = ap.parse_args()
	cab = CaboCha.Parser('-f1')
	#
	try:
		if args.debug:
			print("encoding: %s" % sys.getdefaultencoding())
		while True:
			inp = input().rstrip()
			if args.debug:
				print('Input : ' + inp)
			if len(inp) > 0:
				if inp[0] == args.commentchar: # コメント行を無視
					pass
				else:
					if not args.silent:
						print(inp + '[original]')
					# headerの分離
					try:
						header, inp = inp.split(args.headersep)
					except ValueError:
						header = ""; headersep = ""
					#
					cabocha = cab.parseToString(inp)
					sentence = Struc.structure(cabocha)
					if args.debug:
						print("# sentence: %s" % sentence)
					targets = sentence[len(sentence) - 1]['deps']
					if args.debug:
						print("# targets: %s" % targets)
					process(sentence, targets, header, args.headersep)
	except EOFError:
		pass

## end of program
