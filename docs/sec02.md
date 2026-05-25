---
title: |-
    メディアネットワーク演習II
    個別課題2 (ネットワーク)
---

[戻る](./)

## 目標 ##

他の人からのアクセスを受け付けられるようにサーバを設定する．また，他の人のサーバにアクセスできるようにする．WSLとWindowsのネットワーク的な関係を理解する．型あるいは構造，スキーマについて考える．仲良くなる．

## 動かしてみよう(ローカルで) ##

### サーバ ###

以下のように`api/main.py`と`api/schemas/message.py`をダウンロードして配置し[^tree]，`uvicorn api.main:app`により以下で定義したAPIを有するサーバを起動する(仮想環境を有効化することを忘れずに)．GitHub から取り出したものを利用してもよい．

[^tree]: この図は`tree --charset=ascii --dirsfirst -F`により取得した．ディレクトリの構造をツリー状に表示するコマンドである`tree`については`man tree`参照．

```
`-- api/
    |-- schemas/
    |   `-- message.py
    `-- main.py
```

[`api/main.py`](../sec02/api/main.py)

```python
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import api.schemas.message as message_schema

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['null'],
    allow_methods=['*'],
)

app.state.message = message_schema.Message()


@app.get("/message", response_model=message_schema.Message)
async def get_message():
    return app.state.message


@app.post("/message", response_model=message_schema.Message)
async def post_message(message: message_schema.MessageBase):
    app.state.message = message_schema.Message(time=datetime.now(),
                                         **message.model_dump())
    return app.state.message
```

[`api/schemas/message.py`](../sec02/api/schemas/message.py)

```python
from datetime import datetime
from pydantic import BaseModel, Field


class MessageBase(BaseModel):
    name: str | None = Field(None,
                             examples=["System"],
                             description="Message from")
    message: str | None = Field(None,
                                examples=["Default Message"],
                                description="Message body")


class Message(MessageBase):
    time: datetime | None = Field(None, description="Message post time")
```

-   Windows + WSL環境の場合は，通常Windowsのブラウザでこのページを見ているはずなので，ファイルのダウンロードはWindows側で行われる．そのファイルをWSLの中に適切に移動すること．[WSL上のLinuxにあるファイルへのアクセス](sec00.html#wsl上のlinuxにあるファイルへのアクセス)など参照．
-   Visual Studio Code上ではオープンしているフォルダ配下でファイルの移動等ができる(マウスによる直感的な操作)．
-   WSLのターミナルでも可能．[Linuxコマンド紹介]参照．

<http://127.0.0.1:8000/docs>にアクセスしてAPIドキュメントを確認する．今回の例では `api/schemas/message.py` によりスキーマ(schema)を定義している．これによりどういったデータがやり取りされるかを明確にし，それ以外のデータ(型不一致や不正な値)が送られた際に，バリデーションおよび型変換が自動的に行われるようになる．また，`description="Message from"` などの記述によりドキュメントが自動生成される．様々なAPIを持つサーバを作成する場合ドキュメント作成が(手動では)困難になるので，このようにコード中に埋め込んでおき自動生成するといった手法が一般的にとられる[^doxygen]．

<http://127.0.0.1:8000/docs>の下の方の`Schemas`という箇所にスキーマがまとめられている．

![](images/sec02_schema.png)

[^doxygen]: Python自体の場合は[pydoc](https://docs.python.org/3/library/pydoc.html)，CやC++の場合は[doxygen](https://www.doxygen.nl/)など．

補足: 今回もローカルのHTMLファイル(`file://`)からアクセスするため，`Origin: null` を許可している．

### クライアント ###

前回同様HTMLに含まれるJavaScriptによりサーバとやり取りしてみる．以下のHTMLを`client.html`として用意して，ブラウザで開く(Windows + WSL環境であればWindows側で開く)．

今回はアクセスする先を指定できるようにしている．Default は `http://127.0.0.1:8000/message` であり，`127.0.0.1` はローカルループバックアドレスと呼ばれ，自分自身を指す特別なIPアドレスである(自分自身のみアクセスできる; 通常は `localhost` というホスト名と同等)．この箇所をネットワーク上の他のサーバの IP アドレスとして，以降ではテストする．なお，`http://127.0.0.1:8000/message` の `8000` はポート番号[^port]と呼ばれる(特に問題が生じない限り8000番ポートを用いる)．

一通り動作を確認せよ．

[`client.html`](../sec02/client.html) (保存してその保存したファイルを開く)

```html
<!doctype html>
<html>
<head>
<title>個別課題2</title>
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
$(function () {
    // GET (メッセージ取得)
    $('button#get_message').on(
        'click', function () {
            const url = $('#get_message_url').val()
            console.log(url)
            api_request(url).then(function(value) {
                $('#get_message_result_name').html(value['name'])
                $('#get_message_result_message').html(value['message'])
                $('#get_message_result_time').html(value['time'])
                console.log(value['message'])
            })
        })
    // POST (メッセージ送信)
    $('button#post_message').on(
        'click', function () {
            const url = $('#post_message_url').val()
            console.log(url)
            const data = {
                name: $("#post_message_name").val().trim(),
                message: $("#post_message_message").val().trim()
            }
            if (data['name'].length == 0 || data['message'].length == 0 || url.length == 0) {
                return
            }
            api_request_post(url, data).then(function(value) {
                $('#post_message_result').html(value['name'] + ': ' + value['message'])
            })
        })
    // GETした結果のクリア
    $('button#get_message_clear').on(
        'click', function () {
            $('#get_message_result_name').empty()
            $('#get_message_result_message').empty()
            $('#get_message_result_time').empty()
        })
    // POST情報のクリア
    $('button#post_message_clear').on(
        'click', function () {
            $('#post_message_result').empty()
            $('#post_message_message').val('')
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

## 班内で情報共有する仕組みを確立する ##

(これは後でやってもよい．先に[ネットワークの準備](#ネットワークの準備)(←おそらく時間がかかる)ができた人がGoogle Chatのスペースを作成するなど)

班内で IP address を伝え合う必要がある(あるいは今後の自由製作課題でファイルをやり取りする必要が生じるので)ので，なんらかのコラボレーションツール(チャットやファイル共有ができるもの)を使うことを強くオススメする．

[LINE](https://line.me/)や[Slack](https://slack.com/)，[Chatwork](https://go.chatwork.com/)，[Google Chat](https://chat.google.com/)などが候補として挙げられる．各班で適宜情報共有する仕組みを確立すること．

特に好みがなければ[Google Chat](https://chat.google.com/)をELMSのGoogle Accountで利用するのが最も簡単(全員アカウントを持っているので)．以下に簡単に設定方法を紹介する．

代表者が[スペース](https://support.google.com/chat/answer/7659784?hl=ja)を作成して，班のメンバをスペースに参加させる(メールアドレスの入力が必要)．一旦作成してしまえば，各自のPCから発言できる．スペースは[Google Chat](https://chat.google.com/) (ELMSのGoogle Accountになっていることを確認すること)の以下の `New chat` の箇所から作成できる．Space name は適当に決める(案がなければ『20XX年度MN演習II○班』や『○○と愉快な仲間たち』など何でもよい; 後で変更できる)．

![](images/sec02_google_chat1.png)

![](images/sec02_google_chat2.png)

![](images/sec02_google_chat3.png)

## ネットワークの準備 ##

注意: 演習の際にWiFiで接続するネットワークのプロファイルは**プライベート**としておくこと．

DefaultのWindows + WSL環境では以下の2つのIPアドレスが存在する([IPアドレスを調べる]を参照して自身のネットワーク上でのIPアドレスを調べるとよい)．

-   Windows の IP アドレス
-   WSL の IP アドレス

補足:

-   MacやWindows版のPythonを利用している場合は(WSLは存在しないため) IP アドレスは1つのみ．したがって，Portフォワーディングの設定は省略できる．
-   ずっと以前(Windows 10時代)に WSL をインストールしたなどで WSL 1 (WSL の version は PowerShell などで [`wsl -l -v`](https://learn.microsoft.com/ja-jp/windows/wsl/basic-commands) により調べることができる)を利用している場合は WSL と Windows のネットワークは共通，つまり IP アドレスが共通なので，その IP アドレスがそのまま利用できるため，Portフォワーディングの設定は省略できる．

DefaultのWindows + WSL環境ではNATモード(上記の通り2つのIPアドレスが存在する)が用いられており，Portフォワーディングの設定が必要となるため演習がかなり煩雑になる．そのためWSLのNetwork modeをMirrored (ミラーモード)に変更する．このモードでは Windows と WSL が同一ネットワーク上で同一のIPアドレスを共有するため，外部からのアクセスが容易になる．つまりこの場合，以下の IP アドレスは同じになる．

-   Windows の IP アドレス
-   WSL の IP アドレス

"Windows Subsystem for Linux Settings" (日本語では「Linux用Windowsサブシステムの設定」)というGUIによる設定プログラム(`wslsettings.exe`)が用意されている([参考](https://news.mynavi.jp/article/20241107-3060285/))ので，それを開いて Networking の箇所で Networking mode を Mirrored に変更する．加えて Host Address Loopback を On にする[^address_loopback]．

![](images/sec02_windows_wsl_mirrored.png)

[^address_loopback]: Host Address Loopback の説明は以下のとおりで，Windows に割り当てられた IP アドレスを用いて，WSL と Windows の間で相互に接続できるようになる．
    >   Only applicable when wsl2.networkingMode is set to mirrored. When
    >   set to True, will allow the Container to connect to the Host, or
    >   the Host to connect to the Container, by an IP address that's
    >   assigned to the Host. Note that the 127.0.0.1 loopback address can
    >   always be used - this option allows for all additionally assigned
    >   local IP addresses to be used as well.

変更した後は WSL を再起動する必要がある．WSL を Install した時と同様，PowerShellで以下を実行すると，WSL を Shutdown することができる．Shutdown の後に再度 WindowsメニューからUbuntuを探して起動するか，vscode から接続すれば WSL は起動する．

```powershell
wsl --shutdown
```

[IPアドレスを調べる]を参照してIPアドレスを調べ，同じ IP アドレスになっているかを確認する．

-   Windows の IP アドレス
-   WSL の IP アドレス

たとえば IP アドレスが `192.168.11.13` であるとして，この IP アドレスでサーバを起動するには，以下のように`--host`オプションを利用する．

```console
(test) tsutsui@DESKTOP-ICHCFQ4:~$ uvicorn api.main:app --host 192.168.11.13
INFO:     Will watch for changes in these directories: ['/home/tsutsui/work/enshu2_2024/content/sec02']
INFO:     Uvicorn running on http://192.168.11.13:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [37448] using StatReload
INFO:     Started server process [37451]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

以下により動作を確認する(Host Address Loopback が Off の場合，以下は接続できない; 班の他の人からはアクセスができる)．

-   `http://192.168.11.13:8000/docs` にアクセス
-   `client.html` を開いて URL の箇所を
    `http://192.168.11.13:8000/message` に変更して動作確認．

なお，`--host 192.168.11.13` のように特定のIPアドレスを指定してサーバを起動した場合，`http://127.0.0.1:8000/docs` により接続しようとしても繋がらなくなる．また，IP アドレスが変更になった場合に再度実行するコマンドを変更する必要がある．このような問題は IP アドレスとして `0.0.0.0` を利用すると解決する．`0.0.0.0` はそのホストの任意の IP アドレス(すべてのネットワークインタフェース)を意味する．以下のように `uvicorn` を起動する．

```
uvicorn api.main:app --host 0.0.0.0
```

### WSL Networking mode NAT の場合 ###

**Networking mode を Mirrored に変更した場合は，この箇所は飛ばしてよい**

たとえば WSL の IP アドレスが `172.28.139.139` であるとして，この IP アドレスでサーバを起動するには，以下のように`--host`オプションを利用する．

```console
(test) tsutsui@DESKTOP-ICHCFQ4:~$ uvicorn api.main:app --host 172.28.139.139
INFO:     Will watch for changes in these directories: ['/home/tsutsui/work/enshu2_2024/content/sec02']
INFO:     Uvicorn running on http://172.28.139.139:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [37448] using StatReload
INFO:     Started server process [37451]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

以下により動作を確認する．

-   `http://172.28.139.139:8000/docs` にアクセス
-   `client.html` を開いて URL の箇所を
    `http://172.28.139.139:8000/message` に変更して動作確認．

たとえば `http://172.28.139.139:8000/docs` にアクセスすると，サーバ側では以下が表示される．`172.28.128.1` は(環境により異なるが) Windows と WSL の間で通信するための，**Windows側**のIPアドレスである．

```console
INFO:     172.28.128.1:57914 - "GET /docs HTTP/1.1" 200 OK
INFO:     172.28.128.1:57914 - "GET /openapi.json HTTP/1.1" 200 OK
```

WSLはWindowsとは別の仮想ネットワーク上のホストとして動作するため，WSLがネットワーク機能を利用できるように，WSL環境は以下のような構成となっている．

![](images/sec02_wsl_network.svg)

>   筒井メモ: WSL内で複数のOSを動かしたとしても何故かIPアドレスは共通になる．上の図ではWindows内部にネットワークがあるような図になっているが，実際は異なる様子(ネットワークではあるが，ホスト(IPアドレスは)は2つのみ)．また，`172.28.139.139` についてはWindows機個別にランダムに決まる様子．

`172.28.139.139` や `172.28.128.1` といったIPアドレス(ネットワークとしては`172.28.128.0/20`)はWindows内部でのみ有効であり，

-   WSLからWindowsを通じて外部にアクセスする際はNAPTと呼ばれる機能により Windows 側の IP アドレスが利用される．
-   一方外部からWindowsを通じてWSLにアクセス可能とするためには，そのような設定(ポートフォワーディング)が必要になる．

なお，`127.0.0.1` はWSLとWindows間で自動的に転送される仕組みがあるため，これまで明示的な設定を行わずともアクセスできていた．

### Windows Defender Firewall の設定 ###

Windowsの場合(Macでも同様かもしれない; [参考](https://support.apple.com/ja-jp/guide/mac-help/mh34041/mac)) Firewall の設定が必要になる．Default の状態では外部から 8000番ポート[^port]へのアクセスは遮断される．

[^port]: ネットワーク構成論の講義や演習でやります．

`Windows Defender Firewall with Advanced Security` (日本語では「セキュリティが強化された Windows Defender ファイアウォール」[^english_windows]; WFAS)を開いて，`Inbound Rules` に以下の `New Rule` を追加する．なお，試した範囲ではOSの再起動は不要である(うまく動作しない場合は再起動を試してみるのもよい)．

[^english_windows]: Windows を日本語の設定で利用しているとこのように用語が複雑で直感的でないので，Windows (に限らず開発元言語が英語のもの)は英語の設定で利用したほうがよいと著者は考えている．Windows キーから検索する際に英語で検索した方が簡単に目的のものを探すことができる．

-   Rule Type: Port
-   Name: fastapi 等適当で構わない(後で思い出せるような名前にしておく)
-   Profile: Private[^private_network]でのみ有効とする．また，演習の際にWiFiで接続するネットワークのプロファイルは**プライベート**としておく．
-   Action: Allow the connection
-   Protocols and Ports: TCP の Specific local port(s): 8000

![](images/sec02_windows_firewall1.png)

![](images/sec02_windows_firewall2.png)

![](images/sec02_windows_firewall3.png)

![](images/sec02_windows_firewall4.png)

![](images/sec02_windows_firewall5.png)

![](images/sec02_windows_firewall6.png)

[^private_network]: 「プライベートネットワーク」と言うこともあるが，これは別の意味(プライベートIPアドレスを利用するネットワーク)もあるので注意すること．Windowsで設定する内容はあくまでネットワークプロファイルであり，この設定に応じてセキュリティレベルが変更される(パブリックではより強く制限する)．したがって，今回のルール追加はプライベートネットワークでのみ有効としておき，パブリックプロファイルの利用が想定される公衆WiFiなどでは有効にならないようにする．

### Portフォワーディングの設定 ###

**Networking mode を Mirrored に変更した場合は，この箇所は飛ばしてよい**

Windows において，以下により外部からの通信を内部に転送する設定を行う．ここでは以下の想定をしている．

-   Windows の IP アドレス: `192.168.11.13`
-   WSL の IP アドレス: `172.28.139.139`

注意:

-   管理者権限のPowerShellにて実行すること．
-   Portフォワーディングの設定については(以下のコマンドを実行する範囲では)再起動不要である．
-   以下，手順を順に書いているが，`0.0.0.0` を利用するのがオススメ．理解したうえで途中のコマンドは省略して問題ない．

```{.nowrap}
netsh interface portproxy add v4tov4 listenaddress=192.168.11.13 listenport=8000 connectaddress=172.28.139.139 connectport=8000
```

上記設定により `192.168.11.13:8000` へのアクセスは `172.28.139.139:8000` に転送される．また，設定一覧は以下により確認できる．

```
PS C:\Users\htutu> netsh interface portproxy show all


Listen on ipv4:             Connect to ipv4:

Address         Port        Address         Port
--------------- ----------  --------------- ----------
192.168.11.13   8000        172.28.139.139  8000

```

設定を削除するには以下を実行する．

```{.nowrap}
netsh interface portproxy delete v4tov4 listenaddress=192.168.11.13 listenport=8000
```

**補足**

上記ではIPアドレス `192.168.11.13`，ポート`8000` 宛の通信を WSL (IPアドレス `172.28.139.139`，ポート `8000`)に転送する設定を説明しているが，[Windows のIPアドレスが変わるたびに設定を変更する必要がある]{ style="color:red; font-weight: bolder;" }(DHCPによりIPアドレスが動的に割り当てられる環境では，再起動や再接続のたびに変更される可能性がある)．

Windows のネットワークインタフェースに到達したデータについて，それの

-   宛先IPアドレス: 任意
-   宛先ポート番号: `8000`

のものを WSL (IPアドレス `172.28.139.139`，ポート `8000`)に転送するには以下のようにする．`0.0.0.0` は任意の IP アドレス(すべてのネットワークインタフェース)を意味する

```{.nowrap}
netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=8000 connectaddress=172.28.139.139 connectport=8000
```

[ただしこの場合，`uvicorn api.main:app` のみで起動した `uvicorn` に `http://127.0.0.1:8000/` でのアクセスできなくなるので注意(`--host` option を用いて起動すること)．]{ style="color:red; font-weight: bolder;" }

なお，`uvicorn` についてもこの `0.0.0.0` (任意IP アドレス宛)を `--host` option に利用することができる．

```
uvicorn api.main:app --host 0.0.0.0
```

### 理解のためのおまけ ###

アプリケーションプログラムを特定のIPアドレス/ポート番号で待ち受けるようにすることを，そのシステムコール名に由来して[`bind`](https://man7.org/linux/man-pages/man2/bind.2.html)すると言うことがある(ネットワークやOSに詳しい人は良くこのような言い方をする)．

`uvicorn api.main:app --host 172.28.139.139` では IP アドレス `172.28.139.139`，(Defaultの)ポート番号 `8000` に `bind` される．`uvicorn api.main:app --host 0.0.0.0` では IP アドレス `0.0.0.0` (そのネットワークインタフェースに割り当てられている任意(全て)の IP アドレス)，ポート番号 `8000` に `bind` されるわけである．

## 動かしてみよう(ネットワーク経由で) ##

以下を想定する(各自自身のIPアドレスで読み替えること)．

-   Windows の IP アドレス: `192.168.11.13`

上記設定で `http://192.168.11.13:8000/docs` にアクセスできるようになっているはずである(Networking mode が Mirrored の場合は，Host Address Loopback が On である必要がある)．自身で起動したサーバに自身の計算機(NotePC)からアクセスできるか確認せよ．

補足:

-   WSL Networking mode NAT の場合
    -   ネットワークプロファイル Public のまま上記設定を行い，その後 Private に変更した場合は，ポートフォワーディングの設定がうまく有効にならない．その場合，一回 `netsh` を利用して設定を削除して再度設定を行うと有効になる(再起動不要)．
-   ネットワークプロファイル Public のままで通信ができている場合は，Public でのセキュリティレベルの設定が低くなっている可能性があるので，設定の見直しをおすすめする．

## 課題 ##

班内の他の人のサーバに `client.html` を通じてアクセスし，GET，POSTを実行，挙動を確認せよ．IPアドレス情報を班の中でうまく共有すること．

## 追加課題 ##

Message のスキーマを改造し，動作を確認せよ．たとえば，以下のように Priority を Message につけるなど(つけるだけですけど)．

[`api/schemas/message_sample.py`](../sec02/api/schemas/message_sample.py)

```python
from datetime import datetime
from pydantic import BaseModel, Field


class MessageBase(BaseModel):
    name: str | None = Field(None,
                             examples=["System"],
                             description="Message from")
    message: str | None = Field(None,
                                examples=["Default Message"],
                                description="Message body")
    priority: int = Field(0, examples=[5],
                          description="Message priority. "
                          "Higher value means high priority.")


class Message(MessageBase):
    time: datetime | None = Field(None, description="Message post time")
```

`message_sample.py` は `message.py` に rename して利用するか，利用する側で `import api.schemas.message as message_schema` の箇所を調整すること．

他に改造できる点があれば(思いつけば)，いろいろ試してみること([セキュリティ対策](#セキュリティについて)をする，なども考えられる)．

## 解説 ##

### IPアドレスを調べる ###

#### Windows ####

-   Select Start
-   Select Settings
-   Select Network & internet
-   Select Wi-Fi
-   Select the Wi-Fi network you're connected to
-   Under Properties, look for your IP address listed next to IPv4 address

![](images/sec02_windows_ipaddress1.png)

![](images/sec02_windows_ipaddress2.png)

あるいはPowerShell等にて`ipconfig`コマンドを使う．以下のみならず多くの情報が表示される．その中から探す．少し大変．

```
Wireless LAN adapter Wi-Fi:

   Connection-specific DNS Suffix  . : flets-east.jp
   IPv6 Address. . . . . . . . . . . : 2408:(略)
   Temporary IPv6 Address. . . . . . : 2408:(略)
   Link-local IPv6 Address . . . . . : fe80::(略)%14
   IPv4 Address. . . . . . . . . . . : 192.168.1.10
   Subnet Mask . . . . . . . . . . . : 255.255.255.0
   Default Gateway . . . . . . . . . : fe80::(略)%14
                                       192.168.1.1
```

#### WSL (Linux) ####

`ip`コマンドを用いる．下の場合は`172.28.139.139`がWSLのIPアドレス．

```
tsutsui@DESKTOP-ICHCFQ4:~$ ip a
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host
       valid_lft forever preferred_lft forever
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
    link/ether (略) brd ff:ff:ff:ff:ff:ff
    inet 172.28.139.139/20 brd 172.28.143.255 scope global eth0
       valid_lft forever preferred_lft forever
    inet6 fe80::(略)/64 scope link
       valid_lft forever preferred_lft forever
```

#### Mac ####

-   Terminal で `networksetup -listallhardwareports` でデバイス名を探して(ここでは`en0`とする; `networksetup` コマンドについては[こちら](https://support.apple.com/ja-jp/guide/remote-desktop/apdd0c5a2d5/mac)参照)，そのデバイスの IP address を `ipconfig getifaddr en0` で表示する．
-   UNIX 系の `ifconfig` コマンド[^ip]が存在するかもしれない．それを利用しても調べられる．
-   たぶん GUI でも調べられるはず．

[^ip]: Linux でも `ifconfig` コマンド([net-tools](https://net-tools.sourceforge.io/))が存在するが，最近は [iproute2](https://wiki.linuxfoundation.org/networking/iproute2)由来の `ip` コマンドが推奨される([参考](https://wiki.linuxfoundation.org/networking/net-tools))．

### セキュリティについて ###

この演習ではセキュリティ対策を行っていない．外部に公開するのはあまりに危険なので注意すること．たとえば，`<img src="https://www.hokudai.ac.jp/common/img/h_logo.png" />` という Message をサーバに送り，`client.html` で GET して表示させると北大のロゴが表示される．

```json
{
  "name": "System",
  "message": "<img src=\"https://www.hokudai.ac.jp/common/img/h_logo.png\" />"
}
```

画像程度であれば問題ないが，JavaScript をクライアントに実行させることも可能となり(たとえば`<script>alert("ぼくはまちちゃん！")</script>`をサーバに送る)，任意のスクリプトを実行させる攻撃([クロスサイトスクリプティング(XSS)](https://ja.wikipedia.org/wiki/%E3%82%AF%E3%83%AD%E3%82%B9%E3%82%B5%E3%82%A4%E3%83%88%E3%82%B9%E3%82%AF%E3%83%AA%E3%83%97%E3%83%86%E3%82%A3%E3%83%B3%E3%82%B0))の温床となる．

```json
{
  "name": "System",
  "message": "<script>alert(\"ぼくはまちちゃん！\")</script>"
}
```

### Linuxコマンド紹介 ###

ファイル/ディレクトリ操作

-   `ls`: ファイル一覧
    -   `ls -lart`: ファイル一覧オススメオプション付き\
        (新しいものが下に表示されるのでたくさんファイルがあっても最新の情報は見られる)
        -   `-l`: 日付等も表示
        -   `-a`: `.` で始まるファイル(いわゆる隠しファイル)も表示
        -   `-t`: 時間順にソート
        -   `-r`: それを逆順にする
-   `cp src dst`: ファイル `src` を `dst` にコピー\
    (ディレクトリをコピーする際は`-r`オプションが必要)
    -   `dst` がディレクトリの場合は `dst/src` というファイルにコピーされる．
-   `mv src dst`: ファイル `src` を `dst` に移動\
    (ディレクトリも移動可)
    -   `dst` がディレクトリの場合は `dst/src` というファイルに移動される．
-   `rm file`: ファイル`file`の削除(ディレクトリを削除する際は`-r`オプションが必要)
-   `mkdir dir`: ディレクトリ `dir` 作成

ディレクトリ操作(今いるディレクトリ(current directory)を変更するなど)

-   `cd dir`: ディレクトリ `dir` に移動する
-   `cd ..`: 1つ上のディレクトリに移動する
-   `pwd`: 今いるディレクトリ(current directory)を表示する
-   `cd -`: 1つ前にいたディレクトリに移動する
-   `cd`: home directory に移動する
    -   なお `~` は home directory として扱われる．ユーザ名がtsutsuiの場合，home directory は通常 `/home/tsutsui/` (環境変数 `HOME` (`$HOME`)も同じ)．
        -   `cd ~/api/` や `source ~/.venv/bin/activate` のように利用可能

シェルの機能(コマンドを入力して実行する環境それ自体)

-   `↑`，`↓`: 過去のコマンドを表示する．
-   `C-r`: 過去のコマンドの検索，`C-r` の後に文字列を入力するとそれにマッチする過去のコマンドが表示される(`Enter` で実行)．文字列を入力して再度 `C-r` を入力すると，さらに過去のコマンドを検索する．`C-c` で中断できる．
-   `TAB`: 補完．`source test/bin/acti` まで入力して `TAB` キーを入力すると `test/bin/activate` が存在すれば `source test/bin/activate` に補完される．
-   なお Ubuntu の Default のシェルは [`bash`](https://www.gnu.org/software/bash/manual/)であるが，より強力な機能を有する [`zsh`](https://www.zsh.org/) (`zsh` にさらに [oh my zsh](https://ohmyz.sh/) で機能強化することができる)や [`fish`](https://fishshell.com/)もある．

他

-   `less file`: ファイル`file`の中を見る(`q`で終了)
-   `man ls`: `ls` のマニュアルを参照する(`q`で終了)

### Python補足 ###

Pythonは動的型付け言語である．C言語などの静的型付け言語と異なりあまり
型を意識せずともプログラミングが可能である反面，動的型付けに由来する問
題も多く発生する．

そのためPythonではPython 3.5にて[Type Hints](https://peps.python.org/pep-0484/)が導入され，以降様々な機能拡張が行われている．<https://docs.python.org/3/library/typing.html> に掲載されている例を以下に示す[^moon_weight]．

```python
def surface_area_of_cube(edge_length: float) -> str:
    return f"The surface area of the cube is {6 * edge_length ** 2}."
```

ここでは引数`edge_length`は`float`が期待され，返り値は`str`であると定義されている．なお，`edge_length`に`float`以外(たとえば`int`)が渡されても特にエラーを発生せず実行可能であり，あくまで静的解析ツールでのチェック(それによるコード品質の改善)を想定している．

[^moon_weight]: ここのサンプルコードは元々以下であったが，[**質量**は変わらない](https://github.com/python/cpython/issues/120661)，という指摘を受け差し替えられた．
    ```python
        def moon_weight(earth_weight: float) -> str:
            return f'On the moon, you would weigh {earth_weight * 0.166} kilograms.'
    ```

本日のコード中にある `name: str | None` はこのような構文を利用したものである．`name` としては `str` か `None` が想定され，その Default の値は `Field(None, examples=["System"], description="Message from")` で与えられているが[^pydantic]，端的には `None` である(他の情報はドキュメント生成などに利用される)．すなわち，`name` や `message` のフィールドはリクエストに含めなくてもよく，その場合は自動的に `None` が設定される．

```python
class MessageBase(BaseModel):
    name: str | None = Field(None, examples=["System"], description="Message from")
    message: str | None = Field(None, examples=["Default Message"], description="Message body")
```

---

`main.py` の以下の箇所，少々不思議かもしれない．

```python
    app.state.message = message_schema.Message(time=datetime.now(),
                                         **message.model_dump())
```

`message` は `MessageBase` のインスタンスであり，`model_dump()` により[辞書型(dictionary)](https://docs.python.org/ja/3/tutorial/datastructures.html#dictionaries)に変換している(他の言語ではハッシュやmapや連想配列などと呼ばれる; key とそれに対応する value で構成される)．辞書型の前に `**` をつけると `key=value` の形式に展開され，関数の引数として渡される．

```console
 % python
Python 3.12.3 (main, Feb  4 2025, 14:48:35) [GCC 13.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> def test(name, power):
...     print(f"{name}: {power}")
...
>>> a = { "name": "Hiroshi Tsutsui", "power": 20 }
>>> test(**a)
Hiroshi Tsutsui: 20
```

[^pydantic]:本演習ではスキーマの定義に[pydantic](https://docs.pydantic.dev/latest/)を利用している．FastAPIとともに用いられ，API開発，特にその検証に有効なライブラリである．

## おまけ: ブラウザの音声認識/音声合成機能を使ってみる ##

[クライアント](../sec02/client-audio.html)

参考:

-   [Web Speech API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)
-   [Webページでブラウザの音声認識機能を使おう - Web Speech API Speech Recognition](https://qiita.com/hmmrjn/items/4b77a86030ed0071f548)

[戻る](./)
