#!/bin/sh
# wikipediaのダンプデータからword2vecのモデルを作る

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

