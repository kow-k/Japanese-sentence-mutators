#!/usr/bin/env python3
# coding: utf-8
# Wikipediaダンプデータから抽出したテキストを1行1文の形式にする
import os
import sys
#sys.path.append(os.environ['HOME']+'/lib/python3')
import string
import re

if __name__=='__main__':
    import argparse
    # コマンドラインオプション
    ap=argparse.ArgumentParser(description="Wikipediaダンプデータから抽出したテキストを1行1文の形式にする")
    ap.add_argument('file',type=open,metavar='TXT',help='wikipedia text file')
    ap.add_argument('--debug','-d',action='store_true',help='for debug')
    args=ap.parse_args()

    title=False
    for ln in args.file:
        ln=ln.rstrip()
        if re.match('<doc',ln):
            title=True
        elif title==True:
            title=False
        elif re.match('</doc>',ln):
            pass
        else:
            if ln=='':
                continue
            ln=re.sub('。','。\n',ln)
            ln=ln.rstrip()
            print(ln)

### end of program
