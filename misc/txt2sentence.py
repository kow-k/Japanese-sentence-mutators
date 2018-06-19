#!/usr/bin/env python3
# coding: utf-8
# Wikipediaダンプデータから抽出したテキストを1行1文の形式にする

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
