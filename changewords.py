#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2016-2020 Kow Kuroda
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#		 http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


#
# created by Hikaru Yokono (yokono.hikaru@jp.fujitsu.com).
#
# modified by Kow Kuroda (kow.kuroda@gmail.com), 2017/02/22, 23.
# 1. sys.stdin, stdout の wrapping処理を追加
# 2. 入力文の echo をデフォールトの挙動に [--silent で抑制] (2017/02/22)
# 3. 変異の有限回の再帰の実装で「世代」概念を導入 (2017/02/22)
# 4. 変異の対象を名詞，動詞，形容詞，副詞，格助詞に [--pos で選択] (2017/04/14)
#		 課題1: 活用形の処理は現状では ad hoc．
#		 課題2: 重みづけの扱いの現状はおもちゃなので，ちゃんとやった方が良い．


import os
import sys
#sys.path.append(os.environ['HOME']+'/lib/python')
import string
import re
import random
import CaboCha
from gensim.models import word2vec
from gensim.models import KeyedVectors
from collections import defaultdict

## Kow Kuroda added the following 17 lines on 2017/02/22, 23
import io
out_enc      = in_enc = "utf-8"
headersep    = ":"
sys.stdin    = io.TextIOWrapper(sys.stdin.buffer, encoding=in_enc)
sys.stdout   = io.TextIOWrapper(sys.stdout.buffer, encoding=out_enc)
case_markers = [ 'が', 'を', 'に', 'で', 'から', 'と',  'へ', 'まで', 'によって' ]
case_factors = [  0.2, 0.1,  0.2,  0.2,   0.05,  0.1,  0.05,  0.05,      0.05 ]
#case_factors = [ 0.2, 0.2,  0.3,  0.2,   0.1,   0.1,  0.05,  0.05,      0.05 ]
# 変異対象の品詞
targetpos   = ['名詞', '動詞', '形容詞', '副詞', '格助詞', '形容動詞']
postags     = { 0: "N", 1: "V", 2: "Adj", 3: "Adv", 4: "P", 5: "PredN" }

def weighted_random_choice(W, C):
	'''k個の要素からなるリストLからの無作為抽出を，Wで別に指定する数値 r
	(0.0 < r < 1.0) で疑似的に重みづけする
	'''

	if args.debug:
		print("len(W) = %s: %s" % (len(W), W))
		print("len(C) = %s: %s" % (len(C), C))
	try:
		assert len(W) > len(C)
	except AssertionError:
		return random.choice(C)
	if args.debug:
		print("# input for weighted random choice: %s" % C)
	R = [ ]; M = [ ]
	for i, x in enumerate(C):
		for j in range(int(100 * W[i])):
			M.append(x)
		R.extend(M)
	if args.debug:
		print("# candidates for weighted random choice: %s" % R)
	return random.choice(R)

def replace(words, position, cand):
	'''
	words の position の位置の単語を cand に置き換える
	words の方には活用形まで入っているけど，cand は原形なので，活用形の情報を cand に渡す
	'''
	temp = re.split('-', words[position])
	if re.match('動詞|形容詞|助動詞', temp[1]):
		cand += '-' + temp[len(temp) - 1]
	words[position] = cand
	return words

def reunion(words, inflections):
	'''
	形態素列を文に戻す
	原形は活用させる
	'''

	result = ''
	for i in range(len(words)):
			elem = re.split('-', words[i])
			if re.match('動詞|形容詞|助動詞', elem[1]):
					kihon = inflections[elem[2]]['基本形']
					pat = re.compile(kihon + '$')
					base = pat.sub('', elem[0])
					# 活用形のずれの ad hocな対応
					# 助動詞たか接続助詞ての前にある用言を，活用に連用タ接続があればそっちに，なければ連用形にする
					if i < len(words) - 1 and re.search('(-助動詞-特殊・タ|て-助詞)', words[i+1]):
						if elem[3] == '連用形' and '連用タ接続' in inflections[elem[2]]:
							elem[3] = '連用タ接続'
						elif elem[3] == '連用タ接続' and '連用タ接続' not in inflections[elem[2]] and '連用形' in inflections[elem[2]]:
							elem[3] = '連用形'
					if len(elem) == 4 and elem[3] in inflections[elem[2]]:
						result += base + inflections[elem[2]][elem[3]]
					else:
						# 変異予定の語が求められている活用形を持たない場合，原形を返してみる
						# 名詞-形容動詞語幹を形容詞に置き換えるとかで発生する
						result += elem[0]
			else:
				result += elem[0]
	return result

def k2h(str):
	'''
	カタカナ->ひらがな
	'''
	katahira = {'ア':'あ', 'イ':'い', 'ウ':'う', 'エ':'え', 'オ':'お',
	'カ':'か', 'キ':'き', 'ク':'く', 'ケ':'け', 'コ':'こ',
	'サ':'さ', 'シ':'し', 'ス':'す', 'セ':'せ', 'ソ':'そ',
	'タ':'た', 'チ':'ち', 'ツ':'つ', 'テ':'て', 'ト':'と',
	'ナ':'な', 'ニ':'に', 'ヌ':'ぬ', 'ネ':'ね', 'ノ':'の',
	'ハ':'は', 'ヒ':'ひ', 'フ':'ふ', 'ヘ':'へ', 'ホ':'ほ',
	'マ':'ま', 'ミ':'み', 'ム':'む', 'メ':'め', 'モ':'も',
	'ヤ':'や', 'ユ':'ゆ', 'ヨ':'よ',
	'ラ':'ら', 'リ':'り', 'ル':'る', 'レ':'れ', 'ロ':'ろ',
	'ワ':'わ', 'ヲ':'を', 'ン':'ん',
	'ガ':'が', 'ギ':'ぎ', 'グ':'ぐ', 'ゲ':'げ', 'ゴ':'ご',
	'ザ':'ざ', 'ジ':'じ', 'ズ':'ず', 'ゼ':'ぜ', 'ゾ':'ぞ',
	'ダ':'だ', 'ヂ':'ぢ', 'ヅ':'づ', 'デ':'で', 'ド':'ど',
	'バ':'ば', 'ビ':'び', 'ブ':'ぶ', 'ベ':'べ', 'ボ':'ぼ',
	'パ':'ぱ', 'ピ':'ぴ', 'プ':'ぷ', 'ペ':'ぺ', 'ポ':'ぽ',
	'ァ':'ぁ', 'ィ':'ぃ', 'ゥ':'ぅ', 'ェ':'ぇ', 'ォ':'ぉ',
	'ャ':'ゃ', 'ュ':'ゅ', 'ョ':'ょ',
	'ッ':'っ', 'ヰ':'ゐ', 'ヱ':'ゑ'}
	kata = list(str)
	hira = ''
	for k in kata:
		if k in katahira:
			hira += katahira[k]
		else:
			hira+=k
	return hira

def is_hira(inp):
	'''
	strがひらがなかどうかのチェック
	'''
	ch = [x for x in inp if 'あ' <= x <= 'ん']
	if len(inp) == len(ch):
		return True
	else:
		return False

if __name__=='__main__':
	import argparse
	# コマンドラインオプション
	ap = argparse.ArgumentParser(description = "品詞を固定した単語単位の置換")
	ap.add_argument('--bin', type = str, metavar = 'bin', help = 'word2vec model', default = 'jawiki.pos.bin')
	ap.add_argument('--debug', action = 'store_true', help = 'debug')
	ap.add_argument('--lb', type = float, help = '類似度の下限 (0 ~ 1.0)', default = 0)
	ap.add_argument('--ub', type = float, help = '類似度の上限 (0 ~ 1.0)', default = 1)
	## Kow Kuroda added the following three arguments.
	ap.add_argument('--repeat', type = int, help = '反復回数', default = 1)
	ap.add_argument('--silent', action = 'store_true', help = '入力の非表示')
	ap.add_argument('--show_similars', action = 'store_true', help = '類似語の表示')
	ap.add_argument('--pos', type = int, choices = list(range(0,6)), help = '変異対象 (0:名詞, 1:動詞, 2:形容詞, 3:副詞, 4:格助詞, 5:形容動詞)', default = 0)
	ap.add_argument('--exclude_PredN', action = 'store_true', help = '形容動詞を非名詞扱い')
	ap.add_argument('--extend_V', action = 'store_true', help = 'サ変名詞を動詞扱い')
	ap.add_argument('--extend_Adv', action = 'store_true', help = '形容詞を副詞扱い')
	ap.add_argument('--no_hiragana', action = 'store_true', help = '平仮名表記への置換を抑制')
	ap.add_argument('--inflection', type = argparse.FileType('r', encoding = in_enc), help = '活用語尾リスト (default:katsuyou.csv)', default = 'katsuyou.csv')
	ap.add_argument('--headersep', type = str, help = 'ヘッダーの区切り記号', default = ':')
	ap.add_argument('--commentchar', type = str, help = 'コメント行の識別記号', default = '%')
	#
	args = ap.parse_args()
	# 活用語尾リストの読み込み
	inflection = defaultdict(lambda:defaultdict(str))
	for ln in args.inflection:
		ln = ln.rstrip()
		if args.debug:
			print(ln)
		line = re.split(',', ln)
		inflection[line[0]][line[1]] = line[2]

	cab = CaboCha.Parser(u'-f1')
	model = KeyedVectors.load_word2vec_format(args.bin, binary = True)
	#
	if   args.extend_V == True:
		args.pos = 1
	elif args.extend_Adv == True:
		args.pos = 3
	#
	try:
		if args.debug: print("encoding: %s" % sys.getdefaultencoding())
		## Kow Kuroda modified the following routine on 2017/02/22, 2020/02/14
		## by adding loop under r = args.repeat.
		while True: # 行ごとのループ
			ignored = False
			inp = input().rstrip()
			if args.debug: print('Input : ' + inp)
			try:
				if inp[0] == args.commentchar:
					ignored = True
			except IndexError:
				ignored = True
			if not args.silent:
				if not ignored: print(inp + '[original]')
			# headerの分離
			try:
				header, inp = inp.split(args.headersep)
			except ValueError:
				header = ""; headersep = ""
			result = inp
			r = args.repeat # r は世代に相当
			d = r
			while d > 0:
				d -= 1
				inp = result
				morphs = re.split(u'\n', cab.parseToString(inp))
				morphs = [x for x in morphs if not re.match(u'\* ',x)]
				positions = [ ] # <= 変数名を変更
				words = [ ]
				if args.debug:
					print('# --pos', args.pos, '(' + targetpos[args.pos] + ')')
				# 変異する場所の候補を集める
				for i in range(len(morphs)):
					if morphs[i] == u'EOS':
						break
					line = re.split('\t', morphs[i])
					base = line[0]
					features = re.split(',', line[1])
					# 名詞の扱い
					if targetpos[args.pos] == '名詞':
						if features[0] == targetpos[args.pos]:
							if args.exclude_PredN == True: # 形容動詞語幹を除外
								if re.search('動詞', features[1]):
									pass
								else:
									positions.append(i)
							else:
								positions.append(i)
					# 動詞の扱い
					elif targetpos[args.pos] == '動詞':
						# 補助動詞(動詞-非自立)は置換対象にしない
						if features[1] == '非自立':
							pass
						# サ変名詞を動詞に含めるかどうか
						if args.extend_V == True:
							if features[0] == '名詞' and re.search('サ変', features[1]):
								positions.append(i)
							else:
								if features[0] == targetpos[args.pos]:
									positions.append(i)
						else:
							if features[0] == targetpos[args.pos]:
								positions.append(i)
					# 格助詞の扱い
					elif targetpos[args.pos] == '格助詞':
						if features[0] == targetpos[args.pos]:
							if re.search('^(格|副)助詞$', features[1]):
								positions.append(i)
					# 形容動詞
					elif targetpos[args.pos] == '形容動詞':
						if features[0] == targetpos[args.pos]:
							if re.search('動詞', features[1]):
								positions.append(i)
							else:
								pass
					# 副詞
					elif targetpos[args.pos] == '副詞':
						if args.extend_Adv == True:
							if features[0] == targetpos[args.pos] or features[0] == '形容詞':
								positions.append(i)
						if features[0] == targetpos[args.pos]:
							positions.append(i)
					# その他 (形容詞など) の扱い
					else:
						if features[0] == targetpos[args.pos]:
							positions.append(i)
					# 結果の生成
					if features[6] != '*':
						base = features[6]
					pos = features[0]
					if re.match('動詞|形容詞|助動詞',features[0]):
						pos += '-' + features[4] + '-' + features[5]
					words.append(base + '-' + pos)
				#
				if args.debug:
					print("# words: %s" % words)
					print("# positions: %s" % positions)
				#
				if len(positions) == 0:
					print("# detected no candidate for replacement")
					break
				# 場所決め
				cnt  = 0 # 諦めカウンタ
				flag = 0 # 諦めフラグ
				while True:
					# 変数名の変更: cand => mutant, mutant => cand; positions は位置のリスト
					try:
						target = random.choice(positions) # selects target word
					except IndexError: break
					# 格助詞の変異を導入するために条件分枝を導入
					if targetpos[args.pos] == '格助詞': # 格助詞の変異
						C = [ x for x in case_markers if x + '-助詞' != words[target] ]
						if args.debug: print(C)
						#mutant = random.choice(C)
						mutant = weighted_random_choice(case_factors, C)
						mutant += '-助詞'
						if args.show_similars:
							print("# " + words[target] + " is replaced by " + mutant + " from:")
							print("# " + ", ".join(C))
						# 置換
						words = replace(words, target, mutant)
						break
					else: # 格助詞の他の品詞の変異
						elem = re.split('-', words[target])
						query = elem[0] + '-' + elem[1]
						if re.match('動詞|助動詞|形容詞', elem[1]):
							try:
								query += '-' + elem[2]
							except IndexError: pass
						try:
							basecandidates = model.most_similar(positive = [query])
							#print(basecandidates)
							# 置換する語と元の語の品詞を一致させる
							pat = re.compile('-' + elem[1])
							#candidates = [x for x in basecandidates if pat.search(x[0])]
							candidates = [ ]
							for cand in basecandidates:
								temp = re.split('-', cand[0])
								# --no-hiragana 有効時，平仮名だけの候補をはじく
								# (副詞が対象だと置換するものがなくなりそうな予感)
								if pat.search(cand[0]):
									if not args.no_hiragana or not is_hira(temp[0]):
										candidates.append(cand)
						except KeyError:
							# 置換しようにも元の語が word2vec のモデルの中にないので
							# 本当は変異する語の選択からやり直す必要がある
							# が，今は変異は生成できなかったとあきらめる
							flag = 1; break
						#print(candidates)
						#if candidates == [ ]:
						if len(candidates) == 0:
							flag = 1; break
						mutant = random.choice(candidates)
						if args.debug:
							print('# mutant: ' + mutant[0])
						if args.show_similars: # 類似語集合の表示
							print("# replacement candidate(s): %s" % candidates)
							print("# " + mutant[0] + " replaced " + words[target])
						if args.lb <= mutant[1] and mutant[1] <= args.ub: # 類似度評価
							# 置換
							words = replace(words, target, mutant[0])
							if args.debug: print('# words: %s' % words)
							break
						# 試行回数の評価
						cnt += 1
						if args.debug: print("# Mutation tried ", cnt, "time(s)")
						if cnt == 100:
							flag = 1; break
				#
				text = reunion(words, inflection)
				if len(text) == 0:
					pass
				else:
					if ignored == True:
						pass
					else:
						print(header + headersep + text + \
							"[%s change #%d]" % (postags[args.pos], (r - d)) )
				# 結果の表示
				if flag == 1:
					print('# Alert: No mutation was made')
	except EOFError:
		pass

## end of program
