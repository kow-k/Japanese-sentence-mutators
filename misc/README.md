スクリプト群

# Wikipediaのダンプデータからword2vecのモデルを作る

## 前提
- python3の実行環境
- pythonのライブラリ
  - gensim
  - MeCab

## 手順
1. https://dumps.wikimedia.org/jawiki/latest/ から日本語wikipediaのダンプデータ(jawiki-latest-pages-articles.xml.bz2)をダウンロード
2. Wikipedia Extractor ( http://medialab.di.unipi.it/wiki/Wikipedia_Extractor )を使ってテキストを抽出
3. txt2sentence.pyで1行1文の形式に変換
4. txt2word2vecdat.pyでword2vecの学習用形式に変換
  - --pos オプションを付ける
5. word2vec_train.pyで学習モデルを生成

