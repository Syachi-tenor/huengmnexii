#!/usr/bin/env python3

import time
import requests
from requests.exceptions import RequestException
import api.schemas.message

BASE_URL = 'http://127.0.0.1:8000'


def post_message(name: str, message: str):
    url = f"{BASE_URL}/messages"
    m = api.schemas.message.MessageBase(name=name, message=message)
    try:
        # json パラメータを使うことで、辞書を自動で JSON 化しヘッダーも設定されます
        requests.post(url, json=m.model_dump(), timeout=5)
    except RequestException as e:
        print(f"送信失敗: {e}")


def get_message(message_id: int):
    url = f"{BASE_URL}/messages/{message_id}"
    try:
        res = requests.get(url, timeout=5)
        res.raise_for_status() # エラーレスポンス（404など）で例外を発生
        return api.schemas.message.Message.model_validate(res.json())
    except (RequestException, ValueError) as e:
        print(f"メッセージ取得失敗 (ID: {message_id}): {e}")
        return None


def print_message(message):
    if not message:
        return
    star = "★" if getattr(message, 'important', False) else ""
    # update_time が文字列の場合はパースが必要ですが、datetime オブジェクトを想定
    time_str = message.update_time.strftime('%H:%M:%S') if hasattr(message.update_time, 'strftime') else message.update_time
    print(f"{time_str} {message.id} {message.name}: {message.message}{star}")


def check(server_current_id: int or None) -> int or None:
    url = f"{BASE_URL}/messages/current_id"
    try:
        res = requests.get(url, timeout=5)
        res.raise_for_status()
        res_dict = res.json()
        new_id = res_dict.get('current_id')
    except (RequestException, ValueError) as e:
        print(f"サーバー接続エラー: {e}")
        return server_current_id

    if server_current_id is not None and new_id != server_current_id:
        print("check: new message!")
        # 古いIDから新しいIDまでの差分をループ処理
        for i in range(server_current_id + 1, new_id + 1):
            message = get_message(i)
            if message:
                print_message(message)
                if message.message == "ぬるぽ":
                    post_message("bot", "ガッ")
                    
    return new_id


def main():
    server_current_id = None
    print("ボットを起動しました。監視を開始します...")
    
    while True:
        server_current_id = check(server_current_id)
        time.sleep(1)


if __name__ == "__main__":
    main()
