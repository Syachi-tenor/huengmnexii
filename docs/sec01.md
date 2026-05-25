---
title: |-
    メディアネットワーク演習II
    個別課題1 (POST, JavaScriptによるクライアント実装)
---

[戻る](./)

## 目標 ##

HTTPのPOSTメソッドを用いてサーバにデータを送り，サーバ上のデータの更新を確認する．JavaScriptを用いたクライアントを作成し，動作を確認する．可能であればGitHubを利用する．

## 動かしてみよう(POSTメソッド) ##

以下のプログラムを`api/main.py`として用意する．

[`api/main.py`](../sec01/api/main.py)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['null'],
    allow_methods=['*'],
)

app.state.message = "Hello World"


@app.get("/message")
async def get_message():
    return {
        "message": app.state.message,
        "status": 200,
    }


@app.post("/message")
async def post_message(message):
    app.state.message = message
    return {
        "message": app.state.message,
        "status": 200,
    }
```

仮想環境を有効化して，上記APIを持つWebサーバを起動する(環境構築および仮想環境については[前回資料](sec00.html)参照)．

```console
uvicorn api.main:app --reload
```

`--reload`オプションをつけて`uvicorn`を起動するとファイルの更新が自動的に検知され，サーバの再起動(Pythonスクリプトの再読込)が行われる．

ブラウザで<http://127.0.0.1:8000/message>にアクセスして動作を確認する．また，<http://127.0.0.1:8000/docs>にアクセスしてAPIドキュメントを確認する．

![](images/sec01_docs.png)

-   `GET /message`
-   `POST /message`

2つが定義されていることがわかる．これらそれぞれは**エンドポイント**と呼ばれる．`POST /message`によりサーバにデータが送られ，変数`app.state.message`の値が更新される．`GET /message`によりデータを取得して更新されたことを確認する．

`POST /message`でデータ(`message`)をサーバに送って，サーバ上のデータが更新されることを確認する．

![](images/sec01_post.png)

(なお，この例では簡略化のためクエリパラメタで受け取っている)

(なお，本来はスキーマを定義してより厳密にAPIを定義する必要があるが，これについては今後の回で行う; スキーマを利用する場合，以下のコードも若干変わってくる)

## 動かしてみよう(JavaScript) ##

これまで<http://127.0.0.1:8000/message>や<http://127.0.0.1:8000/docs>にアクセスして動作を確認していたが，HTMLに含まれるJavaScriptによりサーバとやり取りしてみる．

以下のHTMLを`client.html`として用意して，ブラウザで開く(Windows + WSL環境であればWindowsで開く)．

[`client.html`](../sec01/client.html) (保存してその保存したファイルを開く)

```html
<!doctype html>
<html>
<head>
<title>個別課題1</title>
<meta charset="utf-8" />
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
<script>
const server = 'http://localhost:8000' // 開発時のAPIサーバ接続先
async function api_request(path) {
    const url = server + path
    try {
        const response = await fetch(url)
        const json = await response.json()
        return json
    } catch (err) {
        console.error("GET失敗:", err)
        return { message: "エラーが発生しました" }
    }
}
async function api_request_post(path, data) {
    // この回だけ簡略実装にしている
    const query = new URLSearchParams({message: data})
    const url = server + path + '?' + query
    try {
        const response = await fetch(url, {
            method: 'POST',
        })
        const json = await response.json()
        return json
    } catch (err) {
        console.error("POST失敗:", err)
        return { message: "エラーが発生しました" }
    }
}
$(function () {
    // GET (メッセージ取得)
    $('button#get_message').on(
        'click', function () {
            api_request('/message').then(function(value) {
                $('#get_message_result').empty()
                $('#get_message_result').append(value['message'])
                console.log(value['message'])
            })
        })
    // POST (メッセージ送信)
    $('button#post_message').on(
        'click', function () {
            let data = $("#post_message_body").val()
            api_request_post('/message', data).then(function(value) {
                $('#post_message_result').empty()
                $('#post_message_result').append(value['message'])
            })
        })
    // GETした結果を表示するDIV内のクリア
    $('button#get_message_clear').on(
        'click', function () {
            $('#get_message_result').empty()
        })
    // POST情報のクリア
    $('button#post_message_clear').on(
        'click', function () {
            $('#post_message_result').empty()
            $('#post_message_body').val('')
        })
})
</script>
</head>
<body>

<h3>GET http://127.0.0.1:8000/message</h3>

<p>
<button id="get_message">GET</button>
<button id="get_message_clear">Clear</button>
</p>

<p>取得したメッセージ:</p>
<div id="get_message_result"></div>

<h3>POST http://127.0.0.1:8000/message</h3>

<p>
<label for="post_message_body">送信するメッセージ:</label><br>
<textarea id="post_message_body"></textarea>
</p>

<p>
<button id="post_message">POST</button>
<button id="post_message_clear">Clear</button>
</p>

<p>送信したメッセージ:</p>
<div id="post_message_result"></div>

</body>
</html>
```

ブラウザに以下のような表示がされ[^css]，`GET`，`POST`のテストが可能となっている．

![](images/sec01_html.png)

[^css]: 見た目が質素だが，CSSを使えば自分好みの見た目にできるかもしれない．

## 課題 ##

`POST /message`により`message`を送った際に，サーバのデータ(文字列)をそれで置き換えるのではなく，サーバの文字列の末尾に送った文字列を追加(結合)していくような実装に改造し，実際に動作するかJavaScriptを用いて確認せよ．

## 追加課題 ##

独自APIを定義しJavaScriptによるクライアントで動作を確認せよ．たとえば，

-   `GET /message/len`でサーバにある文字列の長さを返す

-   `POST /message`で送る`message`によって，サーバのメッセージになにがしか処理するようなもの
    -   `clear`という文字列を送ったらサーバの文字列が空になる，それ以外は末尾に追加される，
    -   `x2`という文字列を送ったらサーバの文字列が倍の長さになる，など，

## Git と GitHub ##

第1回は簡単なので，今のうちに Git と GitHub について説明しておく．

[Git](https://git-scm.com/)は，プログラムなどのソースコード管理を行う分散型のバージョン管理シ
ステム(version control system, VCS)の1つである．Linux のソースコード管
理を目的として Linus Torvalds氏によって開発された[^linux_git]．VCSとして過去には
SCCS，[RCS](https://www.gnu.org/software/rcs/)，[CVS](https://cvs.nongnu.org/)，[Subversion](https://subversion.apache.org/)などが存在したが，
現在ではGitが事実上の標準である[^distributed_vcs]．

GitHub はソフトウェア開発プラットフォームであり，Gitを利用した分散型バージョン管理を提供，CI/CD[^cicd]サービス(GitHub Actions)なども統合されている．Gitを用いて共同作業を行う場合，なにがしかの共有システムを用いる必要があるが(研究室などではファイルサーバを利用できる)，そのためにGitHubを利用することができる．

GitHubは自由課題に取り組む際に極めて役に立つはずである．グループワーク(自由課題)においては各グループで作業を行うが，そのソースコードを共有することができる．演習Iで利用していたグループもあるかもしれない．

以下，なにかの役立つかもしれない小ネタ．

-   GitHub 自体は主にRuby ([Ruby on Rails](https://rubyonrails.org/))で実装されている．
-   GitHub は Microsoft に75億ドルで買収された(2018年)
    -   Microsoftに買収されることに懸念を持ったユーザは[GitLab](https://about.gitlab.com/)に移行した
    -   日本経済新聞電子版は「マイクロソフト、**設計図共有サイト**を8200億円で買収」との見出しで速報を出した([参考](https://www.itmedia.co.jp/news/articles/1806/05/news069.html))．

[^linux_git]: 以前(もう20年以上前)はBitKeeperが利用されていたが，その無償提供の打ち切りを契機としてGitは開発された．

[^distributed_vcs]: Gitと同世代の分散型VCSとしてBazzarやMercurialなどがある．

[^cicd]: CI/CD (continuous integration and continuous delivery/deployment)．継続的インティグレーション/継続的デリバリー(デプロイメント)．CI/CDパイプラインとも呼ばれる．自動化されたビルド，各種テストの実行，検証環境/本番環境への反映(デプロイ)．

### GitHub ###

<https://github.com/> から Sign up する．大学のメールアドレスで登録するのがよい(Continue with Google から Sign up すれば SSO が利用できる)．学生は[GitHub Education](https://docs.github.com/ja/education/about-github-education/github-education-for-students/about-github-education-for-students)に登録すればCopilot [^copilot_privacy_update]およびそのプレミアム機能を無料で利用できる(大学のメールアドレスでの登録と学生証の提出が必要; [Settings](https://github.com/settings) → Billing and licensing → [Education benefits](https://github.com/settings/education/benefits) から申請)．

[^copilot_privacy_update]: [Updates to GitHub Copilot interaction data usage policy](https://github.blog/news-insights/company-news/updates-to-github-copilot-interaction-data-usage-policy/) のアナウンスのとおり2026年4月24日以降，Copilot等におけるインタラクションデータ(入力，出力，コードスニペット，関連コンテキスト等)は，ユーザーがオプトアウトしない限り，AIモデルの学習と改善に使用される．学習に利用されたくないデータ(研究等で利用する部外秘のデータやプライベートなデータ等)については，Copilot等での利用を避けるか，必要に応じてオプトアウトすること．[GitHub Copilot Settings](https://github.com/settings/copilot/features) の `Allow GitHub to use my data for AI model training` でオプトアウトできる．

なお，就職活動などで過去の自身のコードを自身の実績のアピールとして利用することも考えられる．したがって，他の人から見られるかもしれないことを考慮したほうがよい．具体的にはアカウント名など(もちろん好みのアカウント名でよいですが)．

筒井の場合は <https://github.com/htsutsui> がユーザのトップページになる．Repository (レポジトリ; 格納庫の意味)という単位でコード(プロジェクト)は管理される．この単位で Git で取り出したり，サーバに送ったりする．

まずは『ユーザー名のレポジトリを作成し，そこに `README.md` を配置する』を目指すとよい．`README.md` ([markdown 形式](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)で記載する; GitHub 独自の方言がある)の内容はユーザのトップページに表示され，自身のスキルをここに列挙する(そしてアピールする)などで利用されるらしい．

### GitHubへのアクセス ###

以下でこの演習のサンプルコードを(手元に)取り出すことができる．`huengmnexii/` というフォルダが作成され，その中にサンプルコードをSection (回)毎に置いてある．

```console
git clone https://github.com/HU-ICN/huengmnexii/
```

公開されているコードを取り出すだけであれば，上記で十分だが，自身のコードをサーバ(GitHub)に送るなどするには認証を行う必要がある．一般的には SSH の鍵ペアを作成し，公開鍵を GitHub に登録し，秘密鍵を用いて SSH にて接続する．ただし初学者には少し大変なので，以下では HTTPS およびトークンを利用する方法を紹介する．<https://github.com/settings/tokens> にて(自分専用の)トークンを生成して，それを用いてアクセスする．

と，思っていたが，vscode を利用するとトークンやSSHなどを気にせず GitHub にアクセスできるようである(内部で結局トークンを得ている様子)．Git の操作も vscode にて GUI で行えるので，そちらを用いる場合は適宜読み飛ばしてよい(実際にコマンドを打って使ったほうが理解はしやすいはず)．

### GitHub上でのレポジトリの作成 ###

『ユーザー名のレポジトリを作成し，そこに `README.md` を配置する』を目指す．

<https://github.com/new> からユーザ名と同じレポジトリを作成する．Choose visibility が Public だといきなり公開されるので，Private にしておくとよいかもしれない．`Add README` なども選択せず，このまま作成(Create repository)する．

![](images/sec01_github_newrepo0.png)

![](images/sec01_github_newrepo1.png)

なお，自身のプロジェクトのレポジトリを作成した後，他のユーザ(同じグループの人など)のアクセスを許可するには GitHub 上の該当レポジトリの設定(`https://github.com/<username>/<repository>/settings/access`)にて，Collaborator を追加する．

### vscodeからのGitHubを操作する ###

-   `Ctrl+Shift+P`でCommand Paletteを開いて
    `Git: Clone`を探して選択する．

-   `Clone from GitHub`という選択肢があるはずなので，それを選択する．

-   `The extension 'GitHub' wants to sign in using GitHub`というダイア
    ログが表示されるので `Allow` を選択．

-   ブラウザが開き，以下のような画面が現れる．既に GitHub に Sign in
    している状態であれば `Continue` をクリックする(そうでない場合は
    Sign inして継続する)．

    >   Authorize Visual Studio Code\
    >   From the options below, choose which account you would like to
    >   use to authorize this app.

    (これにより WSL 内部の `/home/<username>/.git-credentials` にトークンが保持される．ブラウザはWindows側のものが利用される．このようにうまく連携するように vscode が設計されている．このような連携は，GitHubがMicrosoftに買収された後，vscode との連携が強化されたことによるものと考えられる．GitHub Copilotなども同様である)

-   vscode 側で自身のレポジトリや最近アクセスしたレポジトリがリストさ
    れるので，そこから `clone` したいものを選択する．

    `https://github.com/<username>/<username>` (`<username>` は自分のユーザ名で置き換えること)を指定する．

-   どこに保存するか聞かれるので，保存したい場所を指示する．

-   `clone` に成功したら `Would you like to open the repository?` と聞
    かれるので，`Open` を選択する(Folder が Open される)．

-   `README.md` ファイルを作成して `commit` を行い `push` する．

    `commit` の際に `Make sure you configure your 'user.name' and 'user.email' in git`
    などと怒られる場合は以下を実行する(自分の名前，メールアドレスにすること．．．)．

    ```console
    $ git config --global user.name "Hiroshi Tsutsui"
    $ git config --global user.email "hiroshi.tsutsui@ist.hokudai.ac.jp"
    ```

-   `https://github.com/<username>/<username>` をブラウザで開いて確認する．



その他，左端のアイコンが縦に並んでいる部分(アクティビティバー; [Activity Bar](https://code.visualstudio.com/api/ux-guidelines/activity-bar))で，

-   Explorer (`Control-Shift-E`)にファイルリストが表示されるが，変更のあったファイルには `M` マークがつく(`git status`)

-   Source Control (`Control-Shift-G`)から Commit や Push ができる．

-   下の方の Accounts (人のアイコン)から GitHub へのログイン状態を確認できる．

### GitHubでのトークンの生成 ###

**この内容は vscode を利用しない(あるいは詳細を知りたい)人向けの情報**

<https://github.com/settings/tokens> (Settings → Developer Settings → Personal access tokens → Tokens (classic)) から **Generate new token (classic)** (For general use) に進む．その後以下を入力する．

-   Note: 何に使うトークンかの自分用のメモを入れ(日付などでよいと思う)
-   Expiration: 30 days (default)
    -   長期間有効なトークンだと危険なので default でよい(安全; ただし30日後に再度生成する必要がある)
    -   No expiration としても不要になったトークンは無効化できる
-   Select scopes で以下を選択する．
    -   `repo` (全部)
    -   `workflow`
    -   `read:org`

`Generate token` によりトークンを生成する．一度しか表示されないので，Copy すること．

![](images/sec01_github_token.png)

### GitHubのトークンの手元の環境への登録 ###

**この内容は vscode を利用しない(あるいは詳細を知りたい)人向けの情報**

様々やり方があるが `gh` コマンドを利用する方法を紹介する．`gh` コマンドがインストールされていない場合は `sudo apt install gh` などでインストールすること(Not found などと怒られる場合は `sudo apt update` してから再度 `sudo apt install gh` する)．

以下のように `gh auth login` を実行する．WSL (Ubuntu等)の内部であればどの folder で実行しても問題ない．これは対話的なプログラムになっているので，以下のように選択する．`Paste an authentication token` 以外はおそらく Default (`Login with a web browser` は選択できない; WSL環境に browser がインストールされていないだろうから)．

```console
$ gh auth login
? What account do you want to log into? GitHub.com
? What is your preferred protocol for Git operations on this host? HTTPS
? Authenticate Git with your GitHub credentials? Yes
? How would you like to authenticate GitHub CLI? Paste an authentication token
Tip: you can generate a Personal Access Token here https://github.com/settings/tokens
The minimum required scopes are 'repo', 'read:org', 'workflow'.
? Paste your authentication token: ****************************************
- gh config set -h github.com git_protocol https
✓ Configured git protocol
✓ Logged in as htsutsui
```

これで，このトークンの所有者(つまり自分)の権限で GitHub にアクセスできるようになる．
なお上記は，基本的には `/home/<username>/.git-credentials` ファイルに以下の様な内容を書き込むだけである．トークンが変更になる場合は直接変更してもよい．

```
https://<username>:<token>@github.com
```

再度 `gh auth login` を実行すると
`! You were already logged in to this account` などと怒られるかもしれないが
`/home/<username>/.git-credentials` が更新されてさえいればトークンが使える状態になっている．

なお，ここでは `/home/<username>/.git-credentials` ファイルを作成する目的だけで `gh` コマンドを利用しているが，他にも GitHub 向けの機能がある(issue をリストする `gh issue list` など)．

### コマンドでのレポジトリ操作例 ###

**この内容は vscode を利用しない(あるいは詳細を知りたい)人向けの情報．**

vscode の Git/GitHub の機能を利用せずに `https://github.com/<username>/<username>` に `README.md` を配置することを目指す．

以下でレポジトリを取り出す．`<username>` は自分のユーザ名で置き換えること．

```console
git clone https://github.com/<username>/<username>
```

これで `<username>` というフォルダができる．これはWorking Tree (Working Directory)と呼ばれる．
そこには `.git/` というフォルダがあり，その中に管理用のファイルが保持されている(通常は直接操作しないが `git` コマンドが利用する; ローカルレポジトリの実体がここに保持されている; Working Treeも含めてローカルレポジトリと呼ぶこともある)．`<username>` というフォルダ(Working Tree)自体がプロジェクトのトップ階層扱いになるので，vscode でこのフォルダを開くとよい(以下のようなコマンドを使わずとも vscode が親切にしてくれるかもしれない; [参考](https://code.visualstudio.com/docs/sourcecontrol/github))．

はじめて git を利用する場合は以下のコマンドにより，自身の情報を設定する(この情報が `commit` の際に記録される)．設定は `/home/<username>/.gitconfig` に保持される(一度設定するだけでよい)．

```console
$ git config --global user.name "Hiroshi Tsutsui"
$ git config --global user.email "hiroshi.tsutsui@ist.hokudai.ac.jp"
```

`<username>` というフォルダに `README.md` というファイルを作成し，以下により `add`/`commit`/`push` を行う．`https://github.com/<username>/<username>` を開いてファイルが参照可能か確かめる．

```console
$ git add README.md
$ git commit -m "first commit"
$ git push origin main
```

`git push` ができない場合は[トークン](#トークンの生成)の設定がうまくできていない．

`README.md` を更新して，再度 GitHub 側に反映させたい場合は，上記コマン
ドにてサーバに送ることができる(2回目からは `git push origin main` ではなく `git push` と省略可能)．

### Git ###

上記まででなんとなくファイルをGitHubに送れているものと思う(上記までできればひとまず十分です．．．)．以下 Git (GitHub ではない)のいくつかの機能を紹介する．

ファイルを追加/編集した後に，その内容を記録(`commit`)し，それをサーバ
に送る(`push`)，というのが基本的な作業の流れになる．`commit` するファイルは
`add` により指定する(staging するなどとも呼ばれる)．

ローカルレポジトリ(Working Tree)の状態は `status` により確認できる．以下は `main.py`
を新たに配置(単に新たに作成)しただけの状態．

```console
% git status
On branch main
Your branch is up to date with 'origin/main'.

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        main.py

nothing added to commit but untracked files present (use "git add" to track)
```

`git add main.py` して再度 `status` を確認すると以下の様になる(stage されたことがわかる; stage を取り消すには `git reset main.py` を実行する)．

```console
% git status
On branch main
Your branch is up to date with 'origin/main'.

Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
        new file:   main.py
```

以下のように `add` により stage したものを `commit` する．`-m` によりコメントを指定している．

```console
$ git commit -m "main.py added"
[main 98fff64] main.py added
 1 file changed, 0 insertions(+), 0 deletions(-)
 create mode 100644 main.py
```

`git log` で履歴を確認できる．

```console
$ git log
commit xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx (HEAD -> main)
Author: Hiroshi Tsutsui <hiroshi.tsutsui@ist.hokudai.ac.jp>
Date:   Sat Apr 11 21:48:05 2026 +0900

    main.py added

commit xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx (origin/main)
Author: Hiroshi Tsutsui <hiroshi.tsutsui@ist.hokudai.ac.jp>
Date:   Sat Apr 11 21:30:46 2026 +0900

    second commit

commit xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Author: Hiroshi Tsutsui <hiroshi.tsutsui@ist.hokudai.ac.jp>
Date:   Sat Apr 11 21:28:38 2026 +0900

    first commit
```

ここで，`main` はブランチ名，`origin` はリモートレポジトリに付けられたローカル側での名前である(このあたりから難しくなる)．`git push` により，ローカルの `main` ブランチの内容を，リモート(`origin`)上の `main` ブランチに反映する．

```console
$ git push
Enumerating objects: 4, done.
Counting objects: 100% (4/4), done.
Delta compression using up to 24 threads
Compressing objects: 100% (2/2), done.
Writing objects: 100% (3/3), 288 bytes | 288.00 KiB/s, done.
Total 3 (delta 0), reused 0 (delta 0), pack-reused 0 (from 0)
To https://github.com/htsutsui/htsutsui
   4a2c0a7..98fff64  main -> main
$ git log
commit 98fff640a6c5fedf7b9ba99b8bd43fxxxxxxxxxx (HEAD -> main, origin/main)
Author: Hiroshi Tsutsui <hiroshi.tsutsui@ist.hokudai.ac.jp>
Date:   Sat Apr 11 21:48:05 2026 +0900

    main.py added
(略)
```

`remote` の情報は以下で確認できる．

```
$ git remote -v
origin  https://github.com/htsutsui/htsutsui (fetch)
origin  https://github.com/htsutsui/htsutsui (push)
```

branch および `remote` にある branch の情報は以下で確認できる．

```console
$ git branch -v
* main 98fff64 main.py added
$ git branch -r -v
  origin/main 98fff64 main.py added
```

`origin/main` は `origin` (今回の場合は GitHub)にある `main` というブラ
ンチで，手元のブランチ `main` と同じ状態(同じ commit が最新の状態)になっ
ていることがわかる．

`origin/main` は，共同編集者によって修正(別の commit が行われる)可能性
がある．そういった最新の情報を取り出すには以下(`fetch`)を行う(ここでは
情報を取得するだけで Working Tree にあるファイルの更新等は行われない)．
何も更新がなければ何も表示されない．

```console
$ git fetch
remote: Enumerating objects: 3, done.
remote: Counting objects: 100% (3/3), done.
remote: Compressing objects: 100% (2/2), done.
remote: Total 2 (delta 0), reused 2 (delta 0), pack-reused 0 (from 0)
Unpacking objects: 100% (2/2), 275 bytes | 39.00 KiB/s, done.
From https://github.com/htsutsui/htsutsui
   98fff64..4c34791  main       -> origin/main
$ git fetch
```

手元で branch の状況を見てみる．手元の `main` が `behind 1` であり，
`origin/main` に対して1つの commit 分 behind であることがわかる．

```
$ git branch -v
* main 98fff64 [behind 1] main.py added
$ git branch -r -v
  origin/HEAD -> origin/main
  origin/main 4c34791 main-debug.py added
```

少し試したいので，手元で別のファイル名のファイル(`main-dev.py`)を追加してみる．

```
$ git add main-dev.py
$ git commit -m "main-dev.py added"
[main 86a7e72] main-dev.py added
 1 file changed, 0 insertions(+), 0 deletions(-)
 create mode 100644 main-dev.py
```

この状態で push すると以下の様に怒られる．英語を読めば理由が書いてある．

```
$ git push
To https://github.com/htsutsui/htsutsui
 ! [rejected]        main -> main (non-fast-forward)
error: failed to push some refs to 'https://github.com/htsutsui/htsutsui'
hint: Updates were rejected because the tip of your current branch is behind
hint: its remote counterpart. If you want to integrate the remote changes,
hint: use 'git pull' before pushing again.
hint: See the 'Note about fast-forwards' in 'git push --help' for details.
```

そのとおりにする．

```
$ git pull
Merge made by the 'ort' strategy.
 main-debug.py | 0
 1 file changed, 0 insertions(+), 0 deletions(-)
 create mode 100644 main-debug.py
$ git push
Enumerating objects: 6, done.
Counting objects: 100% (6/6), done.
Delta compression using up to 24 threads
Compressing objects: 100% (4/4), done.
Writing objects: 100% (4/4), 504 bytes | 252.00 KiB/s, done.
Total 4 (delta 2), reused 0 (delta 0), pack-reused 0 (from 0)
remote: Resolving deltas: 100% (2/2), completed with 1 local object.
To https://github.com/htsutsui/htsutsui
   4c34791..225866d  main -> main
```

途中で以下の様な見たこともない画面になるかもしれない(`merge` が発生し，自動的に merge が行われ，そのコメントを要求されている; Default ままで問題ない)．`GNU nano 7.X` などと表示されていれば C-x で終了，おそらくそれ以外の場合は vi なので，その場合は `ZZ` で保存して終了できる．

```
Merge branch 'main' of https://github.com/htsutsui/htsutsui
# Please enter a commit message to explain why this merge is necessary,
# especially if it merges an updated upstream into a topic branch.
#
# Lines starting with '#' will be ignored, and an empty message aborts
# the commit.
```

なお，`git pull` は標準的な設定では概ね以下と同じである(設定によっては `merge` ではなく `rebase` を用いる)．

```
$ git fetch
$ git merge origin/main
```

上記では幸い自動的に `merge` が行われたが，ソースコードの同じ行を複数人が修正すると衝突(conflict)が発生してややこしいことになる(ファイルを修正して，`git add` のうえ `git commit` する，ことで解決できる)．詳細すぎるので，これについては別途各自調べよ(そのような状態を作ってみるとよいかもしれない)．

`git push` であるが，手元の `main` を `origin/main` に送るだけでなく，`origin/main-tsutsui-fix` などのリモートレポジトリ `origin` の新たな branch に送ることもできる．

```
$ git push origin main:main-tsutsui-fix
Enumerating objects: 6, done.
Counting objects: 100% (6/6), done.
Delta compression using up to 24 threads
Compressing objects: 100% (4/4), done.
Writing objects: 100% (4/4), 519 bytes | 519.00 KiB/s, done.
Total 4 (delta 2), reused 0 (delta 0), pack-reused 0 (from 0)
remote: Resolving deltas: 100% (2/2), completed with 1 local object.
remote: 
remote: Create a pull request for 'main-tsutsui-fix' on GitHub by visiting:
remote:      https://github.com/htsutsui/htsutsui/pull/new/main-tsutsui-fix
remote: 
To https://github.com/htsutsui/htsutsui
 * [new branch]      main -> main-tsutsui-fix
```

remote からのメッセージにあるように，これで pull request を上記 URL にアクセスして作成することができる．

通常は `main` に直接送られると皆が混乱するので，pull request を作成して他のユーザに review してもらってからその変更を `main` に取り込む．

なお，`git push` はここでの設定では `git push origin main:main` と同じである(Default でどこに送るかは `.git/config` というファイルに記録されており，変更も可能)．

よく使うコマンド一覧．

-   `git clone`: レポジトリを clone する
-   `git add <file>`: ファイルをステージする
-   `git restore --staged <file>`: Staging を取り消す
    -   `git reset <file>`: Staging を取り消す(古くから使われているやり方; `git restore` の導入は2019年8月の Git 2.23 より)
-   `git commit -m "Comment"`: Commit する(`-m "Comment"` がなければ nano か vi が起動する; 設定できる)．
-   `git log`: log を確認する(`--stat` や `-p` や `--graph` の option がよく用いられる)．
-   `git diff`: Working Tree の未ステージの変更(差分)を表示する(引数で様々な差分表示が可能)．
-   `git status`: 手元のレポジトリの状態の確認(`-s` で simple な表示になる)
-   `git remote`: remote の操作．`origin` 以外の remote を追加するなども可能．
-   `git branch`: branch の操作．新たな branch を作成するなど．
-   `git switch`: branch の切り替え
-   `git fetch`: remote の更新情報を取得する(Working Tree は更新されない)
-   `git init`: 初期化
-   `git merge`: 他の branch の変更を現在の branch に取り込む
-   `git rebase`: 現在の branch の変更を，指定した branch の先につなぎ直す
-   `git reset`: branch の位置や staging 状態を特定の commit に reset する
    -   `--hard`: Working Tree のファイルも更新される
    -   `--mixed`: Working Tree のファイルは更新されない(default)

他に以下(上記だけでも多いが．．．)．

-   `git revert`: commit を revert する(逆方向の変更を新たな commit として適用)
-   `git cherry-pick`: 指定した commit を現在の branch に適用する

いくつか重要なものを忘れているような気がするが，commit，つまり変更内容の記録さえ行えていれば様々にその変更(commit)を操作することができる．なお，以下注意．

-   ファイル名を変更すると変更が追いにくくなるので注意(`git mv` などのコマンドもあるが)．
-   ソースファイルのバージョン管理を目的としているので，可能な限りバイナリファイル(画像など)や大きなファイルはレポジトリに入れない．また通常，中間生成物(Cプログラムをコンパイルしてできた object file(`.o`)など)もレポジトリに入れない．
-   パスワードなどが含まれないように注意する．修正して `push` したとしても履歴として残る．

## 解説 ##

### HTTPメソッド ###

Hypertext Transfer Protocol (HTTP; [RFC 9110](https://datatracker.ietf.org/doc/html/rfc9110))ではいくつかの[メソッド](https://datatracker.ietf.org/doc/html/rfc9110#name-methods)が定義されている．ここでは`GET`と`POST`を利用している．他にAPIとしてよく使われるものに`PUT`や`DELETE`などがある(更に他に`HEAD`などがある)．

-   `GET`はクライアントからサーバに，主にデータの取得を要求するメソッドであり，
-   `POST`はクライアントからサーバに，主にデータを送るメソッドである．

クライアントからサーバにデータ送るメソッドとしては`PUT`もあるが，こちらは**ある**データの置き換えの意図で用いられることが多い(今後の回でやる予定)．なお，設計流儀による部分もある．

なお，`GET`のみに対応したWebサーバの実装をネットワーク構成論の演習回で
行う予定．

### Cross-origin resource sharing (CORS) ###

Pythonのコードに以下の記述がある．ブラウザには，[同一生成元ポリシー(same-origin policy, SOP)](https://en.wikipedia.org/wiki/Same-origin_policy)に基づく制限があり，[クロスオリジンリソース共有(CORS)](https://en.wikipedia.org/wiki/Cross-origin_resource_sharing)はそれを制御された形で緩和する仕組みである(一方で，[クロスサイトリクエストフォージェリ(CSRF)](https://en.wikipedia.org/wiki/Cross-site_request_forgery)のような別のセキュリティ課題も存在する)．

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=['null'],
    allow_methods=['*'],
)
```

実際の運用では任意のクライアントからのアクセスを受け付けると様々なセキュリティ上の問題が発生する．同一生成元ポリシーにより制限されているが，CORSによりサーバの設定に応じて制限が緩和される．今回，自身の計算機に保存したHTMLファイルからWeb APIにアクセスするため，それを許可している(上記コードを削除して動作させてみるとHTML上のJavaScriptからアクセスできなくなることを確認できる)．

補足: 自身の計算機に保存したHTMLファイルからWeb APIにアクセスする場合，HTTP のリクエストヘッダに `Origin: null` が含まれ，これを許容している(セキュリティ上のリスクがあるため推奨されない; 意図しないローカルファイルからのアクセスを許してしまう可能性がある)．`allow_origins=['*']` とすると任意の Origin を許容することになる(かなり推奨されない)．

### JavaScript ###

-   この例では[jQuery](https://jquery.com/)と呼ばれるライブラリを用いている．HTMLで記述された構造の各要素(ブロック等)(このような構造/モデルのことをDocument Object Model (DOM)と呼ぶ)に対する操作を簡潔に記述することができる．たとえば`$('button#get_message_clear')`は`id`が`get_message_clear`であるbutton要素であり，`.on()`によりそのオブジェクトの動作を定義している．

-   APIへのアクセスもjQueryを用いて記述できるが([ファイル](../sec01/client-jquery.html))，ここでは`fetch`を用いて実装している．

-   `async`や`await`は非同期処理を実現するための修飾子．非常に理解が難しいので，こんな感じで書けば動く，程度の理解で全く問題ない(興味のある人は調べてみるとよいかもしれない; 繰り返しになるが非常に理解が難しい)．

### Python 補足 ###

#### デコレータ ####

関数定義`def`の前の`@`で始まる箇所はデコレータと呼ばれる([PEP 318](https://peps.python.org/pep-0318/))．`app.get`自体がメソッドであり，その引数に`def`で定義される関数を渡すような動作をする．FastAPIではこのように記述する，程度の理解で問題ない．

```python
@app.get("/message")
async def get_message():
    return {
        "message": app.state.message,
        "status": 200,
    }
```

なお，FastAPIでは

-   デコレータ部`@app.get("/message")`の
    -   `get`を**オペレーション(operation)**，
    -   `"/message"`を**パス(path)**，
-   デコレータで修飾される関数(ここでは`get_message()`)のことを**パスオペレーション関数(path operation function)**と呼ぶ．

#### async ####

関数定義`def`の前の`async`は非同期処理のための修飾子である([PEP 492](https://peps.python.org/pep-0492/))．大量のアクセスが同時に来るようなWebサーバを想定した場合，ファイルやDBアクセスなどの待ち時間が発生するため，それらを効率よく扱うために利用される．なお，`async`は必ずしもCPUの並列実行を意味するものではない．また`async`を削除しても動作する．

非同期処理により待ち時間を効率的に扱うための仕組みである，程度の理解で問題ない．

参考: <https://fastapi.tiangolo.com/async/>

#### サーバ上のデータについて ####

この例では`app.state.message`に値を保持し，その値をPOSTされた情報により更新している．`app.state`はユーザが自由に利用できるobjectとして定義されている．例えば以下参照．

-   <https://fastapi.tiangolo.com/reference/fastapi/#fastapi.FastAPI.state>
-   <https://www.starlette.io/applications/#storing-state-on-the-app-instance>

実際には`app.message`を利用しても同様のことが実現できる．この場合ユーザが勝手に`app = FastAPI()`で作成した`FastAPI` classのobject (インスタンス)を拡張(`message`というinstance-attributeを追加)することになるので，`FastAPI`の仕様が変更になった場合に不具合が生じる可能性がある．

なお，ここで保持しているデータはサーバプロセスのメモリ上に一時的に保存されているだけであり，サーバの再起動(`--reload`による再読込を含む)により初期化される．実際のアプリケーションでは，データベースなどを用いて永続的にデータを保存することが多い．

### curl ###

<http://127.0.0.1:8000/docs>を見て気づいている人もいるかもしれないが[`curl`](https://curl.se/)というコマンドを用いてAPIにアクセスすることもできる．`curl`はプロンプトで動作する一種のHTTPクライアントであり，以下のコマンドを実行すると北大のWebページの情報(HTML)が得られる．

```console
curl https://www.hokudai.ac.jp/
```

サンプルのAPIでは以下でGET，POSTができる．

-   GET: `curl http://127.0.0.1:8000/message`
-   POST: `curl -X POST 'http://127.0.0.1:8000/message?message=Hello'`
-   POST: `curl -X POST -G http://127.0.0.1:8000/message --data-urlencode message=こんにちは` (←日本語はencodeが必要)

たとえば，一定時間毎にサーバになにかデータを送るなどは，このようなコマンドを使用することにより容易に実現できる．

[戻る](./)
