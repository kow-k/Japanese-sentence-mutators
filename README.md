# ARDJ で使用した文編集のツール文編集ツール
突然変異を模した文の変種生成スクリプト

基本的には標準入力で文を受け付けて，標準出力に返す．
入力には1行1文を想定．UTF-8エンコードが動作の条件．

## 必要な Python パッケージ
- gensim [2.x以降]
- CaboCha
- MeCab

## 必要な word2vec データ
動作には gensim の word2vec が参照する単語類似度データが必要．データの獲得法は次の2つ:

1. 構築済みの [jawiki.pos.bin](https://www.dropbox.com/s/h9hy87hjqn5v3xj/jawiki.pos.bin?dl=1) データ (約200MB) を入手する．
2. 自作する: misc にあるスクリプトを使って Wikipedia の dump から構築する．
方法は misc/README.md を参照の事．モデルファイルの名称は jawiki.pos.bin とする．

なお，国立国語研究所が提供している [日本語書き言葉均衡コーパス (BCCWJ)](http://pj.ninjal.ac.jp/corpus_center/bccwj/) をライセンスを受けて利用している方には私たちが構築した単語類似度データの提供が可能．問い合わせ先は japanese#acceptability#ratings&gmail#com (# を . に，& を @ に変換)．

## changewords.py
(突然変異とのアナロジーで)入力文中の単語1語をランダムに別の語に置き換える．

- どの品詞の語を変異するかは --pos で指定する:
名詞 (形容動詞の語幹を含む) のみを変換させるには --pos 0，
動詞 (助動詞は含まない) のみを変換させるには --pos 1，
形容詞のみを変換させるには --pos 2，
副詞のみを変換させるには --pos 3，
格助詞のみを変換させるには --pos 4 とする．使用例 (入力文の指定されたテキストを TEXT とする):

    ```
    cat TEXT | ./changewords.py --pos 1 # 動詞をランダムに一つ選んで置換
    ```
    ```
    cat TEXT | ./changewords.py --pos 2 # 形容詞をランダムに一つ選んで置換
    ```

ただし格助詞の変更のみ，類似度を使わないで疑似的に頻度を反映したランダム変異としている．

- 単語の置換は1度に1個だけだが，--repeat n で再帰的に n回反復する．使用例:

    ```
    cat TEXT | ./changewords.py --pos 2 --repeat 10 # 形容詞をランダムに一つ選んで置換する処理を10回繰り返す
    ```

- --silent で入力文の表示を禁止 (デフォールトでは入力文を [original] のタグつきで再生)．

- どの語に置き換えるかは Wikipedia (か BCCWJ) から学習して構築した word2vec のモデルから選ぶ．
モデルファイルは --bin で指定 (デフォールトは jawiki.pos.bi)．使用例 (入力文の指定されたテキストを TEXT とする)::

    ```
    cat TEXT | ./changewords.py --bin bccwj.pos.bin
    ```

100回探して該当するものが見つからなかった場合は諦める．この場合:
    ```
    # Alert: No mutation was made.
    ```

の警告が出る．

- --no_hiragana でひらがなのみの語への置換を禁止 (意味の横滑りを抑制に効果がある)．
- 置換する語は類似度の上限 (--ub m) と下限 (--lb n) の間にある候補の中からランダムに選択する．
- lb と ub のデフォールト値はそれぞれ 0.0 と 1.0．従って，類似度が 0.0 から1.0 の範囲の候補で置換．使用例:

    ```
    cat TEXT | ./changewords.py --lb 0.3
    ```
    ```
    cat TEXT | ./changewords.py --ub 0.7
    ```
    ```
    cat TEXT | ./changewords.py --ub 0.7 --lb 0.5
    ```

## swapphrases.py
文中の文節 (≒phrase) の順番を変え，かき混ぜ (scrambling) の効果をシミュレートする．
文節の境界は CaboCha の判定によるもの．
最後の文節 (≒述語) に直接係っているものだけが入れ替えの対象となる．
入れ替え対象の節に係っている節はその節と一緒に移動する (なので，
連体修飾など中の要素の順番は入れ替わらない)．

- --start i, --end j オプションで入れ替えの範囲を i番目の分節から j番目の文節の範囲に限定する．使用例 (入力文の指定されたテキストを TEXT とする):

    ```
    cat TEXT | ./swapphrases.py --start 2 # 最初の文節 (≒phrase) をかき混ぜの対象から除く
    ```

## reducephrases.py
文中の節を段階的に再帰的に削除する．節の境界は CaboCha の判定によるもの．
最後の節に直接係っているものだけが削除の対象となる．

- --lb n で削除で残る文節数の下限 nを指定．使用例 (入力文の指定されたテキストを TEXT とする):

    ```
    cat TEXT | ./reducephrases.py --lb 3 % 少なくとも3つの文節を残す
    ```

- --exclude_wa で「は」で終わる節を削除対象から除外．


## 全体に共通する注意 (改良の必要な点)．
現状では，幾つかの処理が未実装．

- 入力に複文が来ることは想定していない (が，動作は一応する)．
- 1行に複数の文がある入力は全体で1文として扱う．
- 動詞を変換した場合に活用形がずれる場合があるが，正しい処理は未実装．
文法性を保証したいなら，sed などを使った後処理が必要．
- 真性の名詞と UniDicで名詞扱いされている形容動詞語幹との区別ができていない．
- その他の幾つかのエラー処理は未実装．

## Copyrights
Copyright (C) 2016-2018 Kow Kuroda All rights reserved.

スクリプトのライセンスは Apache License, Version 2.0 です．
