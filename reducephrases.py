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
def process(sentence, parget):
	phrases = [ ]
	for c in sentence:
		temp = ''
		for m in c['morphs']:
			line = re.split('\t', m)
			temp += line[0]
		phrases.append(temp)

	for i in range(len(phrases)):
		if i not in target and i != len(phrases) - 1:
			phrases[sentence[i]['link']] = phrases[i] + phrases[sentence[i]['link']]
			phrases[i] = ''

	phrases = [ x for x in phrases if x != '' ]
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
	reduce(phrases, phraseindices, pred)

def reduce(phrases, phraseindices, pred):
	# 削除する項を一つずつ増やしていく
	# 終了条件
	end = args.lb
	count = 1
	if args.debug:
		print('Phrases: %s' % phrases)
		print('Reduce candidates: %s' % phraseindices)
	while True:
		if len(phrases) - count < end: break
		if args.debug:
			print('## delete', count, 'phrase(s)')
		rests = combinations(phraseindices, count)
		for r in rests:
			result = [ ]
			for i in range(0, len(phrases)):
				if not i in r:
					result.append(phrases[i])
			text = ''.join(result) + pred
			print(header + headersep + text + "[reduced %d phrase(s)]" % count)
		count += 1

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
						header, inp = inp.split(headersep)
					except ValueError:
						header = ""; headersep = ""
					#
					cabocha = cab.parseToString(inp)
					sentence = Struc.structure(cabocha)
					target = sentence[len(sentence) - 1]['deps']
					process(sentence, target)
	except EOFError:
		pass

## end of program
