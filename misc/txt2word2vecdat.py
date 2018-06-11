#!/usr/bin/python
# coding: utf-8

import os
import sys
#sys.path.append(os.environ['HOME']+'/lib/python')
import string
import re
import MeCab

if __name__=='__main__':
    import argparse
    # コマンドラインオプション
    ap=argparse.ArgumentParser(description="textをword2vecの学習用データにする(分かち書きしてひとまとめ)")
    ap.add_argument('file',type=open,metavar='FILE',help='1行1文')
    ap.add_argument('--stem','-s',action='store_true',help='動詞，形容詞を基本形に戻す')
    ap.add_argument('--pos','-p',action='store_true',help='品詞情報付き')
    ap.add_argument('--mecabopt','-m',type=str,metavar='STRING',help='mecabのオプション',default='')
    args=ap.parse_args()

    tagger=MeCab.Tagger(args.mecabopt)
    
    for ln in args.file:
        ln=ln.rstrip()
        ln=re.sub('^　','',ln)
        morphs=re.split('\n',tagger.parse(ln).rstrip())
        morphs.pop() # EOS
        word=[]
        pos=[]
        for m in morphs:
            line=re.split('\t',m)
            features=re.split(',',line[1])
            sur=line[0]
            if args.stem and re.match('動詞|形容詞',features[0]):
                sur=features[6]
            # resultの最後とくっつけるやつ
            # - 名詞・サ変接続+動詞・サ変・スル
            if pos!=[] and pos[-1]=='名詞-サ変接続' and features[4]=='サ変・スル':
                word[-1]+=sur
                pos[-1]='動詞'
            else:
                word.append(sur)
                ps=features[0]
                if features[0]=='名詞' and features[1]=='サ変接続':
                    ps+='-'+features[1]
                pos.append(ps)
        result=[]
        for i in range(len(word)):
            if args.pos:
                result.append(word[i]+'-'+pos[i])
            else:
                result.append(word[i])

        print(' '.join(result))
        
