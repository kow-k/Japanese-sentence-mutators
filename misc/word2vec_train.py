#!/usr/bin/env python3
# coding: utf-8

import os
import sys
#sys.path.append(os.environ['HOME']+'/lib/python')
import string
import re
from gensim.models import word2vec
from gensim.models import KeyedVectors

if __name__=='__main__':
    import argparse
    # コマンドラインオプション
    ap=argparse.ArgumentParser(description="word2vecのモデルを学習する")
    ap.add_argument('file',type=str,metavar='TXT',help='分かち書き済みテキスト(1行1文)')
    ap.add_argument('--model','-m',type=str,metavar='MODEL',help='モデル名(default:vector.bin)',default='vector.bin')
    ap.add_argument('--size','-s',type=int,metavar='INT',help='dimensionality of the feature vector (default:100)',default=100)
    ap.add_argument('--window','-w',type=int,metavar='INT',help='maximum distance between the current and predicted word within a sentence (default:5)',default=5)
    ap.add_argument('--alpha','-a',type=float,metavar='FLOAT',help='the initial learning rate(default:0.025)',default=0.025)
    ap.add_argument('--min_count','-min',type=int,metavar='INT',help='ignore all words with total frequency lower than this (default:5)',default=5)
    ap.add_argument('--sg','-sg',choices=[0,1],help='the training algorithm(0:CBOW,1:skip-gram)',default=0)
    ap.add_argument('--negative','-n',type=int,metavar='INT',help='the number of "noise words" on negative sampling (default:5)',default=5)
    ap.add_argument('--iter','-i',type=int,metavar='INT',help='the number of iterations (default: 5)',default=5)
    ap.add_argument('--not-binary','-nb',action='store_false',help='save model in not binary format',default=True)
    args=ap.parse_args()

    sentence=word2vec.LineSentence(args.file)
    model=word2vec.Word2Vec(sentence,min_count=args.min_count,size=args.size,alpha=args.alpha,sg=args.sg,negative=args.negative,iter=args.iter)

#    model.save(args.model)
    model.wv.save_word2vec_format(args.model,binary=args.not_binary)
