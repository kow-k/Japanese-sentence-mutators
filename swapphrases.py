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

# created by Hikaru Yokono (yokono.hikaru@jp.fujitsu.com).
#
# modifications by Kow Kuroda (kow.kuroda@gmail.com), 2017/02/22, 23, 04/08; 2020/02/15
# 1. sys.stdin, stdout の wrapping 処理を追加
# 2. repeat factor r の導入
# modifications by Kow Kuroda (kow.kuroda@gmail.com), 2020/02/18
# 3. 文節の構成の仕方を再実装して，D1 D2 H の順序が D2 D1 H と再生される問題を解消

import os
import sys
#sys.path.append(os.environ['HOME']+'/lib/python3')
import string
import re
import Struc
import random
import CaboCha

import io
out_enc = in_enc = "utf-8"
sys.stdin   = io.TextIOWrapper(sys.stdin.buffer, encoding = in_enc)
sys.stdout  = io.TextIOWrapper(sys.stdout.buffer, encoding = out_enc)

# functions
def process(inp, headersep):
	# original の表示 (任意)
	if not args.silent:
		print(inp + '[original]')
	# headerの分離
	try:
		header, inp = inp.split(headersep)
	except ValueError:
		header = ""; headersep = ""
	result = inp
	r = args.repeat # r は世代に相当
	d = r
	while d > 0:
		d -= 1
		inp = result
		cabocha = cab.parseToString(inp)
		parses = Struc.structure(cabocha)
		# 並べ替え
		phrases, pred = swap(parses)
		# 結果の表示
		text = ''.join(phrases) + pred
		if len(header) <= 0:
			print(text + "[swap %d with degree %d]" % ((r - d), args.degree))
		else:
			print(header + headersep + " " + text + "[swap %d with degree %d]" % ((r - d), args.degree))

def swap(parses):

	## 候補生成
	## original code
	#phrases = [ ]
	#for p in parses:
	#	temp = ''
	#	for m in p['morphs']:
	#		line = re.split('\t', m)
	#		temp += line[0]
	#	phrases.append(temp)
	#for i in range(len(phrases)):
	#	if i not in targets and i != len(phrases) - 1:
	#		phrases[parses[i]['link']] = phrases[i] + phrases[parses[i]['link']]
	#		phrases[i] = ''
	#phrases = [ x for x in phrases if x != '' ]
	## 新しいコード
	P = [ p['surface'] for p in parses ]
	if args.debug:
		print("# surfaces: %s" % P)
	#
	if args.aggressive:
		phrases, pred = P[:-1], P[-1]
	else:
		phrases, pred = gen_phrases(parses)
	#
	if args.debug:
		print("# phrases to swap: %s" % phrases)
		print("# pred: %s" % pred)

	# 入れ替え, 最後のchunkは固定
	# --start と--end の範囲
	start = args.start
	end = 0
	if args.end == 0:
		end = len(phrases) - 1
	else:
		end = args.end
	# 1回で何回 swap させるか (--degree): start から end までの要素の数/2が上限
	times = int(args.degree)
	# 何と何を入れ替えるかをリストで表現する: 要素 2 個が swap 1 回に該当
	indices = list(range(start, end + 1))
	if args.debug:
		print("# indices: %s" % indices)
	#
	if int(len(indices) / 2) < times:
		times = int(len(indices) / 2)
	random.shuffle(indices)
	if args.debug:
		print('# swapped indices: %s' % indices)
	#
	pnt = 0
	for n in range(0, times):
		temp = phrases[indices[pnt]]
		phrases[indices[pnt]] = phrases[indices[pnt + 1]]
		phrases[indices[pnt + 1]] = temp
		pnt += 2
	if args.debug:
		print('# swap result: %s' % phrases)
	return phrases, pred

def gen_phrases(parses):

	pred_index = len(parses) - 1
	pred = parses[pred_index]['surface']
	if args.debug:
		print("# pred at %d: %s" % (pred_index, pred))
	targets = parses[pred_index]['deps']
	if args.debug:
		print("# targets: %s" % targets)
	# 新しい方法で分節を構成
	if len(targets) <= 1:
		phrases = [ p['surface'] for p in parses ]
	elif len(targets) == 2:
		pass
	else:
		targets = [ i for i in targets if not i == 0 ] # remove offending 0
	if args.debug:
		print("# modified targets: %s" % targets)
	if len(targets) == 0:
		phrases = [ parses[0]['surface'] ]
	else:
		phrases = [ ]
		for i, x in enumerate(targets):
			if i == 0:
				try:
					matches = parses[ : targets[i] + 1]
					phrase = "".join([ m['surface'] for m in matches ])
					phrases.append(phrase)
				except IndexError:
					pass
			else:
				try:
					matches = parses[targets[i - 1] + 1: targets[i] + 1]
					phrase = "".join([ m['surface'] for m in matches ])
					phrases.append(phrase)
				except IndexError:
					pass
			phrases = [ p for p in phrases if p != '' ]
	return phrases, pred

## main

if __name__ == '__main__':

	import argparse
	# コマンドラインオプション
	ap = argparse.ArgumentParser(description = "主節の述語に係る句の並びを変える")
	ap.add_argument('--debug', action = 'store_true', help = 'debug')
	ap.add_argument('--start', type = int, help = '順序替えの範囲 (始点) (0 からカウント)', default = 0)
	ap.add_argument('--end', type = int, help = '順序替えの範囲 (終点)', default = 0)
	## Kow Kuroda added the following three arguments.
	ap.add_argument('--degree', type = int, help = '処理当りのスワップの度数 (default 1)', default = 1)
	ap.add_argument('--repeat', type = int, help = '反復回数', default = 1)
	ap.add_argument('--aggressive', action = 'store_true', help = '分節のまとめ上げをしない')
	ap.add_argument('--silent', action = 'store_true', help = '入力の非表示')
	ap.add_argument('--headersep', type = str, help = 'ヘッダーの区切り記号', default = ':')
	ap.add_argument('--commentchar', type = str, help = 'コメント行の識別記号', default='%')
	#
	args = ap.parse_args()
	#
	cab = CaboCha.Parser('-f1')
	#
	try:
		if args.debug:
			print("encoding: %s" % sys.getdefaultencoding())
		## Kow Kuroda modified the following routine on 2017/04/08
		## by adding loop under r = args.repeat.
		while True:
			inp = input().rstrip()
			if args.debug:
				print('Input : ' + inp)
			if len(inp) > 0:
				if inp[0] == args.commentchar: # コメント行を無視
					pass
				else:
					process(inp, args.headersep)
	except EOFError:
		pass

## end of program
