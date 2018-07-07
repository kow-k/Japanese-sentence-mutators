#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2016-2018 Kow Kuroda
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
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
headersep  = ":"
sys.stdin  = io.TextIOWrapper(sys.stdin.buffer, encoding=in_enc)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding=out_enc)

if __name__=='__main__':
    import argparse
    # コマンドラインオプション
    ap=argparse.ArgumentParser(description="主節の述語に係る句を削除する")
    ap.add_argument('--debug',action='store_true',help='debug')
    ap.add_argument('--exclude_wa',action='store_true',help='"NPは"は削除しない')
    ap.add_argument('--lb',type=int,help='除去して残る句の数の下限(default:2)',default=2)
    ap.add_argument('--silent',action='store_true',help='入力の非表示')
    ap.add_argument('--headersep',type=str,help='ヘッダーの区切り記号',default=':')
    args=ap.parse_args()
    cab=CaboCha.Parser('-f1')

    try:
        if args.debug: print("encoding: %s" % sys.getdefaultencoding())
        while True:
            inp=input().rstrip()
            if args.debug:
                print('Input : '+inp)
            if not args.silent:
                print(inp + '[original]')
            # headerの分離
            try:
                header, inp = inp.split(headersep)
            except ValueError:
                header = ""; headersep = ""
            cabocha=cab.parseToString(inp)
            sentence=Struc.structure(cabocha)
            target=sentence[len(sentence)-1]['deps']
            phrase=[]
            for c in sentence:
                temp=''
                for m in c['morphs']:
                    line=re.split('\t',m)
                    temp+=line[0]
                phrase.append(temp)

            for i in range(len(phrase)):
                if i not in target and i != len(phrase)-1:
                    phrase[sentence[i]['link']]=phrase[i]+phrase[sentence[i]['link']]
                    phrase[i]=''

            phrase=[x for x in phrase if x!='']
            # 最後のchunkは固定
            pred=phrase.pop()

            # 削除対象の抽出
            phraseidx=[]
            for i in range(0,len(phrase)):
                if args.exclude_wa:
                    if not re.search('は(?:$|(?:，|、)$)',phrase[i]):
                        phraseidx.append(i)
                else:
                    phraseidx.append(i)


            # 削除する項を一つずつ増やしていく
            # 終了条件
            end=args.lb

            c=1
            if args.debug:
                print('Phrases:',phrase)
                print('Reduce Candidates:',phraseidx)

            while True:
                if len(phrase) - c < end: break
                if args.debug:
                    print('## delete',c,'phrase(s)')
                rests=combinations(phraseidx,c)
                for r in rests:
                    result=[]
                    for i in range(0,len(phrase)):
                        if not i in r:
                            result.append(phrase[i])
                    text = ''.join(result)+pred
                    if args.silent:
                        print(header + headersep + text)
                    else:
                        print(header + headersep + text + "[reduced %d phrase(s)]" % c)
                c+=1


    except EOFError:
        pass

## end of program
