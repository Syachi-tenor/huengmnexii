---
title: |-
    メディアネットワーク演習II
    個別課題3 (シリアライズ，ファイル)
---

[戻る](./)

## 目標 ##

これまで演習で扱ったサーバ(Web API のサーバ; APIサーバ)では，サーバを再起動するとデータが初期化される．サーバに記録されているデータをファイルに保存し，サーバを停止・再起動した際でも以前のデータを継続的に保持するようにする．加えてシリアライズやファイルの取り扱いについて理解するとともに，画像を扱う．

## 動かしてみよう ##

### サーバの起動 ###

```
./
|-- api/
|   |-- schemas/
|   |   `-- message.py
|   `-- main.py
`-- client.html
```

上記のように以下のファイルを配置し[^tree]，`uvicorn api.main:app`により `api/main.py` で定義したAPIを有するサーバを起動する(仮想環境を有効化することを忘れずに)．

[sec03.zip](sec03.zip)をダウンロードし，`sec03.zip`があるディレクトリにて `unzip sec03.zip` を実行すれば展開される(今いるディレクトリに展開されるので注意すること; 個別にダウンロードしてもよいし GitHub から取り出したものを利用してもよい)．

[^tree]: この図は`tree --charset=ascii --dirsfirst -F`により取得した．ディレクトリの構造をツリー状に表示するコマンドである`tree`については`man tree`参照．

[`api/main.py`](../sec03/api/main.py)


```python
from datetime import datetime
import json

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import ValidationError

import api.schemas.message as message_schema


def load(app):
    try:
        with open("data.json", "rt", encoding="utf-8") as f:
            data_dict = json.load(f)
            app.state.message = message_schema.Message.model_validate(data_dict)
    except (FileNotFoundError, ValidationError):
        # ファイルが存在しない or ファイルがうまく読めない
        # →Default の Message を作成する
        app.state.message = message_schema.Message()


async def save(app):
    with open("data.json", "wt", encoding="utf-8") as f:
        f.write(app.state.message.model_dump_json(indent=4))


@asynccontextmanager
async def lifespan(app: FastAPI):
    load(app)
    yield
    await save(app)


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['null'],
    allow_methods=['*'],
)


@app.get("/", response_class=HTMLResponse)
async def get_client():
    """Return client HTML"""
    data = ''
    with open('client.html', 'rt', encoding='utf-8') as f:
        data = f.read()
    return data


@app.get("/message", response_model=message_schema.Message)
async def get_message():
    return app.state.message


@app.post("/message", response_model=message_schema.Message)
async def post_message(message: message_schema.MessageBase):
    m = message_schema.Message(time=datetime.now(),
                               **message.model_dump())
    app.state.message = m
    return m
```


[`api/schemas/message.py`](../sec03/api/schemas/message.py)


```python
from datetime import datetime
from pydantic import BaseModel, Field, Base64Bytes


class MessageBase(BaseModel):
    name: str | None = Field(None,
                             examples=["System"],
                             description="Message from")
    message: str | None = Field(None,
                                examples=["Default Message"],
                                description="Message body")
    image: Base64Bytes | None = Field(None, description="Image data")
    image_type: str | None = Field(None, description="Image MIME type")
    image_filename: str | None = Field(None,
                                       description="File name of image data")


class Message(MessageBase):
    time: datetime | None = Field(None, description="Message post time")
```


[`client.html`](../sec03/client.html)


```html
<!doctype html>
<html>
<head>
<title>個別課題3</title>
<meta charset="utf-8" />
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
<script>
async function api_request(url) {
    try {
        const response = await fetch(url)
        const json = await response.json()
        return json
    } catch (err) {
        console.error("GET失敗:", err)
        return { message: "エラーが発生しました" }
    }
}
async function api_request_post(url, data) {
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        })
        const json = await response.json()
        return json
    } catch (err) {
        console.error("POST失敗:", err)
        return { message: "エラーが発生しました" }
    }
}
async function post_data(url, data) {
    api_request_post(url, data).then(function(value) {
        $('#post_message_result').html(value['name'] + ': ' + value['message'])
    })
}
$(function () {
    // GET (メッセージ取得)
    $('button#get_message').on(
        'click', function () {
            const url = $('#get_message_url').val()
            api_request(url).then(function(value) {
                if (value['image'] ) {
                    const img = 'data:' + value['image_type'] + ';base64,' + value['image']
                    $('#get_message_result_image').attr("src", img)
                } else {
                    $('#get_message_result_image').attr("src", "")
                }
                $('#get_message_result_name').html(value['name'])
                $('#get_message_result_message').html(value['message'])
                $('#get_message_result_image_type').html(value['image_type'])
                $('#get_message_result_image_filename').html(value['image_filename'])
                $('#get_message_result_time').html(value['time'])
            })
        })
    // POST (メッセージ送信)
    $('button#post_message').on(
        'click', function () {
            const url = $('#post_message_url').val()
            let data = {
                name: $("#post_message_name").val().trim(),
                message: $("#post_message_message").val().trim()
            }
            if (data['name'].length == 0 || data['message'].length == 0 || url.length == 0) {
                return
            }
            const file = $("#post_message_image").prop('files')[0]
            if (file) {
                const read = new FileReader();
                read.readAsBinaryString(file);
                read.onloadend = function(){
                    data = Object.assign({}, data, {
                        image: btoa(read.result),
                        image_type: file.type,
                        image_filename: file.name
                    });
                    post_data(url, data)
                }
            } else {
                post_data(url, data)
            }
        })
    // GETした結果のクリア
    $('button#get_message_clear').on(
        'click', function () {
            $('#get_message_result_name').empty()
            $('#get_message_result_message').empty()
            $('#get_message_result_image').attr("src", "")
            $('#get_message_result_image_type').empty()
            $('#get_message_result_image_filename').empty()
            $('#get_message_result_time').empty()
        })
    // POST情報のクリア
    $('button#post_message_clear').on(
        'click', function () {
            $('#post_message_result').empty()
            $('#post_message_message').val('')
            $('#post_message_image').val('')
        })
})
</script>
<style>
input {
    width: 80%;
}
</style>
</head>
<body>

<h3>GET</h3>

メッセージの取得．

<ul>
<li>URL: <input type="text" id="get_message_url" value="http://127.0.0.1:8000/message"></li>
<li>Name: <span id="get_message_result_name"></span></li>
<li>Message: <span id="get_message_result_message"></span></li>
<li>Image: <img id="get_message_result_image" width=100></li>
<li>Image type: <span id="get_message_result_image_type"></span></li>
<li>Image filename: <span id="get_message_result_image_filename"></span></li>
<li>Time: <span id="get_message_result_time"></span></li>
</ul>

<p>
<button id="get_message">GET</button>
<button id="get_message_clear">Clear</button>
</p>

<h3>POST</h3>

メッセージの送信．

<ul>
<li>URL: <input type="text" id="post_message_url" value="http://127.0.0.1:8000/message"></li>
<li>Name: <input type="text" id="post_message_name"></li>
<li>Message: <input type="text" id="post_message_message"></li>
<li>Image file: <input id="post_message_image" type="file"></li>
</ul>

<p>
<button id="post_message">POST</button>
<button id="post_message_clear">Clear</button>
</p>

<p>送信したメッセージ(Name: Message):</p>
<div id="post_message_result"></div>

</body>
</html>
```


### 動作確認1 ###

<http://127.0.0.1:8000/> をブラウザで開くと以下のようなクライアントのページ(画面)が表示される．

![](images/sec03_client.png)

これは `api/main.py` の以下の箇所で `/` にアクセスがあった場合に `client.html` (の中身)を返すようにしているためである．

```python
@app.get("/", response_class=HTMLResponse)
async def get_client():
    data = ''
    with open('client.html', 'rt', encoding='utf-8') as f:
        data = f.read()
    return data
```

このようにファイル(の中身)をクライアント側に返すことができる([おまけ(静的ファイル)]参照)．クライアント側ではこの送られた HTML 記述がブラウザに表示され，これによりボタンを押して Web API にアクセスするなど，クライアントとしての動作を行える．

つまり，『サーバ』から『クライアント』に『クライアント』を送っているのである[^note]．

[^note]: 混乱させる(考えさせる)言い方になっているので各自で混乱を解消してください．

![](images/sec03_api.svg)

### 動作確認2 ###

サンプルでは，メッセージとともに画像データも送れるようになっている(画像がなくてもメッセージを送れる)．

適当/適切な画像データ(問題となるような画像は用いないこと)を用意してサーバに送ってみる．いくつか画像を [images-sample/](images-sample/) に用意しているのでこれを用いてもよい．サーバに送った後に `GET` すると画像が取得・表示される．

なお，<http://127.0.0.1:8000/> ではなく <http://localhost:8000/> を開いている場合，`http://127.0.0.1:8000/message` 宛に GET や POST のリクエストを送ると[CORS違反](sec01.html#cross-origin-resource-sharing-cors)になる(`localhost` の IP アドレスは通常 `127.0.0.1` であるが，`localhost` と `127.0.0.1` は異なるオリジンであるとみなされる)．<http://localhost:8000/> からは `http://localhost:8000/message` 宛に GET や POST のリクエストを送る必要がある．

### 動作確認3 ###

今回の目的は以下である．

>   サーバに記録されているデータをファイルに保存し，サーバを停止・再起動した際でも以前のデータを継続的に保持するようにする．

(ファイルに保存しているため，サーバのメモリ上ではなく，永続的にデータが保持される)

サーバを停止・再起動，その後にメッセージを `GET` してみて，確かに以前送ったメッセージが取得できることを確認する．

通常，データはデータベース[^database]に保存するような実装とすることが多いが，本演習では簡単のためデータをファイルに保存している．データはサーバの，サーバを起動したディレクトリにあるファイル `data.json` に保存される．ファイルの中身を確認せよ．

```json
{
    "name": "筒井",
    "message": "こんにちは",
    "image": null,
    "image_type": null,
    "image_filename": null,
    "time": "2024-04-20T13:55:45.528302"
}
```

今回 `Message` の型を前回のものから以下の通り変更している．

>   以下のような表現は `patch` 形式や `diff` 形式(厳密には diff の [Unified形式](https://www.gnu.org/software/diffutils/manual/html_node/Example-Unified.html))と呼ばれ，`-` で始まる行は削除された行，`+` で始まる行は追加された行を表す．github とかで commit を参照するとよくこういった表記があると思う．

```diff
--- sec02/api/schemas/message.py	2026-04-12 05:09:39.409278437 +0900
+++ sec03/api/schemas/message.py	2026-04-12 05:09:39.409540242 +0900
@@ -1,5 +1,5 @@
 from datetime import datetime
-from pydantic import BaseModel, Field
+from pydantic import BaseModel, Field, Base64Bytes
 
 
 class MessageBase(BaseModel):
@@ -9,6 +9,10 @@
     message: str | None = Field(None,
                                 examples=["Default Message"],
                                 description="Message body")
+    image: Base64Bytes | None = Field(None, description="Image data")
+    image_type: str | None = Field(None, description="Image MIME type")
+    image_filename: str | None = Field(None,
+                                       description="File name of image data")
 
 
 class Message(MessageBase):
```

`Message` に以下を追加している．

-   `image`: 画像データ
-   `image_type`: 画像のタイプ
    (`image/jpeg` や `image/png` などの [Content-type](https://en.wikipedia.org/wiki/Media_type))
-   `image_filename`: 画像のファイル名(←特に今回使わない)

これらは `Message` が画像とともに `POST` される際にクライアントからサーバに送られる情報であり，そのままサーバ側で保持される．画像データ自体はバイナリであるので，ここでは Base64 と呼ばれる符号化[^Base64]により文字列に変換している．データサイズとしては大きくなる[^Base64_size]が扱いが容易になる．

[^Base64]: [RFC 4648, "The Base16, Base32, and Base64 Data Encodings," Oct. 2006](https://datatracker.ietf.org/doc/html/rfc4648).

    バイナリデータ(画像ファイル，音声ファイルなど)には，通常のテキストデータとは異なり，制御文字(NULL文字，改行コード，エスケープ文字など)や非表示文字が含まれる．そのため，バイナリデータをそのまま取り扱うと，通信プロトコルやファイルフォーマットで問題が発生することがある．たとえば，JSONやHTML，HTTPリクエスト/レスポンスなどはテキストデータを想定しており，制御文字が含まれると，データの破損や送受信エラーが発生する可能性がある．また，電子メールにファイルを添付する場合も，メールは本来テキストデータ(7bitの[ASCII文字列](https://ja.wikipedia.org/wiki/ASCII))を送ることを前提としたプロトコル(SMTP)を使用しているため，バイナリファイルを直接送信することはできない．このため，メールの添付ファイルでは[MIME (Multipurpose Internet Mail Extensions)](https://ja.wikipedia.org/wiki/Multipurpose_Internet_Mail_Extensions)が使用され，バイナリデータをBase64符号化して文字列にして送受信できるようになっている．

[^Base64_size]: Base64 は 6 bit を 8 bit の文字に変換する．そのため，データ量は約 4/3 (133%)になる．$2^6=64$ なので Base64 と呼ばれる．文字としては数字(10個)とアルファベット大文字(26個)/小文字(26個)と `-` と `_` が利用される(正規表現で書くと `[0-9a-zA-Z_-]`; 合計64個)．以下，[images-sample/](images-sample/) の画像を Base64 符号化し，バイト数を確認した結果．この程度でプログラムを書くのはあれなので[ワンライナー](https://ja.wikipedia.org/wiki/%E3%82%B7%E3%82%A7%E3%83%AB%E8%8A%B8)(シェルの機能 [`for`](https://www.gnu.org/software/bash/manual/html_node/Looping-Constructs.html#index-for)，[pipe](https://www.gnu.org/software/bash/manual/html_node/Pipelines.html)(`|`) とコマンド([`stat`](https://www.gnu.org/software/coreutils/manual/html_node/stat-invocation.html)，[`base64`](https://www.gnu.org/software/coreutils/manual/html_node/base64-invocation.html)，[`wc`](https://www.gnu.org/software/coreutils/manual/html_node/wc-invocation.html)，[`awk`](https://www.gnu.org/software/gawk/manual/html_node/index.html))を組み合わせて1行でなんとか)している．

    ```{.nowrap}
    % for i in *.png *.jpg ; do echo $i $(stat -c %s "$i") $(base64 -w0 < "$i" | wc -c) ; done | awk '{printf "%s: %d -> %d (%.2f%%)\n", $1, $2, $3, $3/$2*100}'
    eng_logo.png: 3782 -> 5044 (133.37%)
    hu_logo.png: 4952 -> 6604 (133.36%)
    photo.jpg: 63162 -> 84216 (133.33%)
    ```

画像をサーバに送った際にそれが `data.json` にどのように保存されるかを確認すること．

なお，クライアントで `Message` を `GET` した場合に，`Message` に画像があればそれを表示するが，Base64 で符号化されたデータをそのまま表示している．以下の箇所の `value['image']` は文字列であり，

```javascript
                if (value['image'] ) {
                    const img = 'data:' + value['image_type'] + ';base64,' + value['image']
                    $('#get_message_result_image').attr("src", img)
                }
```

`data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAoAAAAHgAQMAAAAPH06nAAAAIGNIUk0AAHomAACAhAAA+gAAAIDo%0AAAB1MAAA6mAAADqYAAAXcJy6UTwAAAAGUExURf8AAP///0EdNBEAAAABYktHRAH/Ai3eAAAAB3RJ%0ATUUH6AQUBhgDA6fgFgAAAD1JREFUeNrtwQENAAAAwqD3T20ON6AAAAAAAAAAAAAAAAAAAAAAAAAA%0AAAAAAAAAAAAAAAAAAAAAAAAA4M8Al+AAAUvMG0oAAAAASUVORK5CYII=` のような文字列を作成して，それを `img` 要素の `src` 属性に設定している．この文字列をブラウザのアドレスバーに入力し，なにが表示されるか確認してみること([640x480の赤い画像](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAoAAAAHgAQMAAAAPH06nAAAAIGNIUk0AAHomAACAhAAA+gAAAIDo%0AAAB1MAAA6mAAADqYAAAXcJy6UTwAAAAGUExURf8AAP///0EdNBEAAAABYktHRAH/Ai3eAAAAB3RJ%0ATUUH6AQUBhgDA6fgFgAAAD1JREFUeNrtwQENAAAAwqD3T20ON6AAAAAAAAAAAAAAAAAAAAAAAAAA%0AAAAAAAAAAAAAAAAAAAAAAAAA4M8Al+AAAUvMG0oAAAAASUVORK5CYII=)(←右クリックメニューからオープン)です)．

[^database]: MySQLやPostgreSQLといったリレーショナル・データベース(RDB)がよく用いられる．データベースも一種のサーバであり，そのサーバへのアクセスを提供するPythonのライブラリ(あるいはフレームワーク)も存在し，FastAPIから簡単に利用できる(ただし知らなければならないことが膨大になるのでここでは省略する)．

    MySQL: MySQLを開発していた企業はサン・マイクロシステムズに買収され，サン・マイクロシステムズ自体もオラクルに吸収合併された．もともとはオープンソースソフトウェアであったが，オラクルによるライセンス形態の変更があり，MySQLからフォークしたMariaDBがオープンソースのコミュニティでは利用されることが多い(MySQLへの依存を継続するオープンソースのプロジェクトも存在する)．

    Oracle: Oracle Database というRDBを開発・販売している．データベースといえばOracle，という時代があった．ただし高価．

### 解説(`main.py`の挙動) ###

以下の記述により，起動時に `data.json` が存在すればそのデータを読み出し(`load()` により読み出し)，**終了時**に `data.json` にデータを保存する実装としている(`save()` により保存)．`app` はその変数 `app.state` にアクセスするために引数として渡している．

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    load(app)
    yield
    await save(app)


app = FastAPI(lifespan=lifespan)
```

## 課題 ##

班内の他の人のサーバにアクセスし，GET，POSTを実行，挙動を確認せよ(画像を送ってみたりすること)．IPアドレス情報を班の中でうまく共有すること．

先週やった以下の項目を確認すること．

-   [Windows Defender Firewall の設定](sec02.html#windows-defender-firewall-の設定)\
    一度設定すれば特に新たな設定は不要なはず．
-   (Networking mode が NAT の場合のみ) [Portフォワーディングの設定](sec02.html#portフォワーディングの設定)\
    IPアドレスが変更になっていれば再度転送の設定が必要(再起動は不要かもしれない)．

大きな画像を送ると `data.json` のサイズが大きくなるので注意すること(ファイルの保存に時間を要するかも知れない)．Base64 符号化により画像データのサイズが大きくなる．

また，クライアントはその API をテストするサーバのページ(サーバの IP アドレスを
`192.168.11.13` とした場合 `http://192.168.11.13:8000/`)か，client.html をダウンロードして開いたものを利用すること．たとえば `http://192.168.11.14:8000/` から `http://192.168.11.13:8000/message` に GET/POST しようとするとエラーが生じる([CORS違反](sec01.html#cross-origin-resource-sharing-cors)になる)．

---

サンプルの `client.html` では `URL:` の input 要素に `127.0.0.1:8000` がハードコーディング(直接記述)されている．あまり親切ではないので，サーバの IP アドレスおよびポート番号で置き換えるようにしたい．これは以下の修正を行うと実現できる．`client.html` に含まれる `127.0.0.1:8000` をサーバの IP アドレスおよびポート番号で置き換えてクライアントに送るようにしている．

(どこのなにを修正するかをよく考えること)

```diff
--- sec03/api/main.py	2026-04-17 00:11:17.820627930 +0900
+++ sec03-rev/api/main.py	2026-04-26 16:31:18.712157694 +0900
@@ -2,7 +2,7 @@
 import json
 
 from contextlib import asynccontextmanager
-from fastapi import FastAPI
+from fastapi import FastAPI, Request
 from fastapi.middleware.cors import CORSMiddleware
 from fastapi.responses import HTMLResponse
 from pydantic import ValidationError
@@ -43,11 +43,13 @@
 
 
 @app.get("/", response_class=HTMLResponse)
-async def get_client():
+async def get_client(request: Request):
     """Return client HTML"""
     data = ''
     with open('client.html', 'rt', encoding='utf-8') as f:
         data = f.read()
+    server_ip, port = request.scope.get("server")
+    data = data.replace("127.0.0.1:8000", f"{server_ip}:{port}")
     return data
 
 
```

## 追加課題 ##

サンプルではサーバは1つのメッセージしか保持しない．`POST` によりサーバに送られるメッセージをリストとして保持するように改造しなさい．

## 解説 ##

`data.json` はその拡張子のとおり [JSON (JavaScript Object Notation)](https://en.wikipedia.org/wiki/JSON)(ジェイソン)と呼ばれる形式である．ファイルに保存されているということは，プログラミング言語上では文字列として扱われるが，それをたとえば Python の場合は容易に辞書型(あるいはリスト型)に変換することができる．

プログラム上での変数はメモリ上に配置されており，複雑な構造になると(文字列やCの配列は構造が簡単)それらは大抵メモリ上に不連続に配置されることになる(C言語ではポインタ等を利用してアクセスされる)．こういったプログラム上の変数を文字列(あるいはバイト列)に変換することを**シリアライズ**と呼ぶ．

ファイルに保存する例はわかりやすいが，APIを利用したサーバとクライアント間でのデータのやりとりも，シリアライズされたデータが用いられる(JSONを用いることが多いが，単に文字列やバイト列でやり取りされることもある)．

```json
{
    "name": "筒井",
    "message": "こんにちは",
    "image": null,
    "image_type": null,
    "image_filename": null,
    "time": "2024-04-20T13:55:45.528302"
}
```

[`json` module](https://docs.python.org/ja/3/library/json.html)を用いて以下のように操作(JSONから辞書型を生成したり，逆に辞書型をJSONにしたり)ができる．

以下ではJSONファイルから辞書型を作成して，一部変更して(入れ子構造のデモを含む)，再度文字列にシリアライズしている．

```console
 % python3
Python 3.11.8 (main, Mar 26 2024, 12:26:07) [GCC 13.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import json
>>> data = json.loads(open('data.json').read())
>>> data
{'name': '筒井', 'message': 'こんにちは', 'image': None, 'image_type': None, 'image_filename': None, 'time': '2024-04-20T13:55:45.528302'}
>>> type(data)
<class 'dict'>
>>> data['name']
'筒井'
>>> data['time']
'2024-04-20T13:55:45.528302'
>>> data['next_message'] = data.copy()
>>> data['name'] = 'Hiroshi Tsutsui'
>>> data
{'name': 'Hiroshi Tsutsui', 'message': 'こんにちは', 'image': None, 'image_type': None, 'image_filename': None, 'time': '2024-04-20T13:55:45.528302', 'next_message': {'name': '筒井', 'message': 'こんにちは', 'image': None, 'image_type': None, 'image_filename': None, 'time': '2024-04-20T13:55:45.528302'}}
>>> str = json.dumps(data, indent=4, ensure_ascii=False)
>>> type(str)
<class 'str'>
>>> print(str)
{
    "name": "Hiroshi Tsutsui",
    "message": "こんにちは",
    "image": null,
    "image_type": null,
    "image_filename": null,
    "time": "2024-04-20T13:55:45.528302",
    "next_message": {
        "name": "筒井",
        "message": "こんにちは",
        "image": null,
        "image_type": null,
        "image_filename": null,
        "time": "2024-04-20T13:55:45.528302"
    }
}
```

JSONに似た形式としては[YAML (Yet Another Markup Language)](https://en.wikipedia.org/wiki/YAML)がある．YAMLは人手で書きやすいので，プログラムに読み込ませる設定ファイル等で利用される印象がある．

また，Pythonで単に変数をファイルに保存したい場合は [pickle](https://docs.python.org/3/library/pickle.html) [^pickle] を用いるのが効率がよい(バイナリデータとしてシリアライズされる)．Rubyでは[Marshal](https://docs.ruby-lang.org/ja/latest/class/Marshal.html)がこれに相当する．

[^pickle]: ピックル(=漬物，ピクルス)

## 追加課題のヒント ##

「メッセージをリストとして保持する」型を作成すればよい．

```diff
--- sec03/api/schemas/message.py	2026-04-12 05:09:39.409540242 +0900
+++ sec03-multi/api/schemas/message.py	2026-04-12 05:09:39.409649990 +0900
@@ -17,3 +17,7 @@
 
 class Message(MessageBase):
     time: datetime | None = Field(None, description="Message post time")
+
+
+class Messages(BaseModel):
+    messages: list[Message] = Field(default_factory=list)
```

あとは，たとえば以下．

-   `api/main.py` で `app.state.message` を `app.state.messages` に変更
-   `data.json` が存在しない場合に
    `message_schema.Message()` を生成するのではなく
    `message_schema.Messages()` を生成する
-   `POST` で `Message` が送られた際は
    `app.state.messages` の末尾に追加する([`append()`](https://docs.python.org/ja/3/tutorial/datastructures.html) する)
-   `GET` でサーバに保存されている `Message` を要求された際は，
    たとえば最新(`app.state.messages` の末尾)の `Message` を返す

これでは，過去の `Message` は保存はされているが，クライアントから `GET` で取得することができない．では，リストの任意の `Message` を `GET` で取得できるようにするにはどのようにすればよいだろうか．次回取り扱うが，調べたり考えてみると面白いかもしれない．少なくとも何番の `Message` が必要なのかをクライアントからサーバに伝える必要がある．

## おまけ(静的ファイル) ##

`/` にアクセスされた際に `client.html` (の中身)を返す記述(定義)は以下で行える旨紹介した．このようにすれば静的ファイル(←単に存在するファイル; 動的ではないもの，ぐらいの意味)をクライアントに返すような普通の Web サーバを構築することができる．

```python
@app.get("/", response_class=HTMLResponse)
async def get_client():
    data = ''
    with open('client.html', 'rt', encoding='utf-8') as f:
        data = f.read()
    return data
```

とはいえ1つずつファイル(とURLの対応)を定義するのは大変なのでFastAPIには [`mount`](https://fastapi.tiangolo.com/ja/tutorial/static-files/) と呼ばれる機能が存在する．たとえば以下のように使う[^html_option]．

[^html_option]: `html=True` は `example/` にアクセスされた際に `example/index.html` が存在すればそれを返すオプション．

[`api/main.py`](../sec03-mount/api/main.py)

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/", StaticFiles(directory="static", html=True))
```

これにより，サーバを起動した(`uvicorn` を実行した)ディレクトリからみて `static/` というディレクトリにあるファイルすべてがサーバから提供されることになる．[Apache](https://httpd.apache.org/)などのよくあるWebサーバを使わずとも，Webページを作って公開し放題である．

[ネットワーク構成論の演習](https://csw.ist.hokudai.ac.jp/network/#exii)で利用する[サンプルデータ](https://csw.ist.hokudai.ac.jp/~tsutsui/ex/server.zip)に静的Webページのデータ(写真のサムネイルたくさん)が含まれるので，それを `static/` に配置して FastAPI を起動してみよ(ネットワーク構成論の演習ではこの FastAPI に変わるものを自作する)．

ダウンロードして展開するのが面倒な場合は，以下のコマンドを実行すると `server/` というディレクトリができるので，その中のファイル(群)を利用すればよい．具体的には `server/data/` を `static/` に移動する．

```
wget -q -O - http://goo.gl/XXXXXX(非公開) | tar zxv
```

## その他 ##

JavaScriptでファイル読み込みを書くのに(本ページ作者筒井は)苦労した．．．具体的には以下の箇所．通常のプログラミング言語のように読み込み関数(`read()`など)を呼び出せばそれでファイルのデータが得られるわけではなく，以下のように `readAsBinaryString` により読み出しを指示しておいて，読み出しが終わった場合に行う処理を `FileReader` オブジェクトに登録するといった記述をする．すごくJavaScriptである．

なお，`btoa` は Base64 符号化を行う関数で，`Object.assign()` により2つの Hash (Pythonの辞書型に相当)をマージしている．

```javascript
                const read = new FileReader();
                read.readAsBinaryString(file);
                read.onloadend = function(){
                    data = Object.assign({}, data, {
                        image: btoa(read.result),
                        image_type: file.type,
                        image_filename: file.name
                    });
                    post_data(url, data)
                }
```


[戻る](./)
