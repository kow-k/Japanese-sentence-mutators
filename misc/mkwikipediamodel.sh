#!/bin/sh
# wikipediaのダンプデータからword2vecのモデルを作る

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


# WikiExtractor.pyのパス
WIKIEXTRACTOR="./WikiExtractor.py"

if [ ! -f $WIKIEXTRACTOR ] ; then
    echo "Error: $WIKIEXTRACTOR が存在しません"
    exit
fi

if [ $# -ne 1 ] ; then
    echo "Usage $0 <dump bz2>"
    exit
fi

DUMP=$1

# 作業用ディレクトリを作る
mkdir worktemp

echo "### テキストを抽出"
python $WIKIEXTRACTOR -o worktemp $DUMP

echo "### 1行1文にする"
for i in worktemp/*/*
do
    python ./txt2sentence.py $i
done > worktemp/jawiki.txt

echo "### 品詞付き形態素の分割"
python ./txt2word2vecdat.py --pos worktemp/jawiki.txt > worktemp/jawiki.pos

echo "### word2vecのモデルの学習"
python ./word2vec_train.py -m jawiki.pos.bin worktemp/jawiki.pos

