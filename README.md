# PandA-for-iOS

PandAから課題一覧を取得してウィジェットに表示します。

## 使用方法

1. [Pythonista 3](https://apps.apple.com/jp/app/pythonista-3/id1085978097)を購入する。
2. ウィジェット画面で[編集]を選択し，Pythonistaを追加して完了。
3. [このあたり](https://qiita.com/maboy/items/cef5dee13d5b2e9ac843)を参考にStaShを入れる。
4. StaSh上で`pip install requests`する。
5. StaSh上で`git clone https://github.com/IkuzakIkuzok/PandA-for-iOS.git`する。
6. PandA-for-iOS/credential.pyのユーザー名(`USERNAME`)とパスワード(`PASSWORD`)を自分の情報に書き換える。
7. PandA-for-iOS/main.pyを実行し，[Use in "Today"]を選択しOK。
8. ウィジェット画面で[Load]を押すと課題の取得を行います。

## 注意事項

- おそらくメモリ制限の都合で，表示できない場合があります。諦めてください。
- 提出済みの課題も併せて表示されます。諦めてください。

## その他

何かありましたら[Twitter](https://twitter.com/__guanine)にてお知らせください。
(ここでIssueを立てられても見ていないかもしれないので)
