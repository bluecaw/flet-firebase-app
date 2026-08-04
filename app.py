import flet as ft
import json
import urllib.request

# --- ご自身の Firebase 設定 ---
API_KEY = "AIzaSyCoe94vJu0Srjt_yP1Nym5UMMGPt0MWngg"
PROJECT_ID = "flet-user-app"

# Firestore REST API のベースURL
BASE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/users"


def main(page: ft.Page):
    page.title = "ユーザー管理アプリ (Firebase REST API版)"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20

    # 選択中のドキュメントIDを保持する辞書
    selected_data = {"id": None}

    # UIパーツの定義
    name_input = ft.TextField(label="氏名を入力", width=300)
    result_text = ft.Text(value="", color=ft.Colors.BLUE)
    user_list = ft.Column()

    # 1. フォームのリセット
    def clear_form():
        selected_data["id"] = None
        name_input.value = ""
        name_input.label = "氏名を入力（新規登録モード）"
        page.update()

    # 2. データをFirebaseから取得して一覧表示 (GET)
    def load_data():
        user_list.controls.clear()
        try:
            url = f"{BASE_URL}?key={API_KEY}"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req) as res:
                response_data = json.loads(res.read().decode('utf-8'))

            # ドキュメント一覧が存在する場合
            if "documents" in response_data:
                for doc in response_data["documents"]:
                    # FirestoreのパスからIDを抽出 (例: projects/.../documents/users/DOCUMENT_ID)
                    doc_path = doc["name"]
                    doc_id = doc_path.split("/")[-1]

                    # フィールドから "name" を取得
                    fields = doc.get("fields", {})
                    user_name = fields.get("name", {}).get("stringValue", "(名前なし)")

                    # 1行分のUI（編集・削除ボタン付き）を生成
                    user_list.controls.append(
                        ft.Row(
                            controls=[
                                ft.Text(f"ID: {doc_id[:8]}... | {user_name}", expand=True),
                                ft.ElevatedButton(
                                    "編集",
                                    on_click=lambda e, u_id=doc_id, u_name=user_name: select_user(u_id, u_name)
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    icon_color=ft.Colors.RED,
                                    on_click=lambda e, u_id=doc_id: delete_data(u_id)
                                )
                            ]
                        )
                    )
        except Exception as ex:
            result_text.value = f"取得エラー: {ex}"
        page.update()

    # 3. 「編集」ボタンを押した時
    def select_user(user_id, user_name):
        selected_data["id"] = user_id
        name_input.value = user_name
        name_input.label = f"ID: {user_id[:8]}... の氏名を編集（更新モード）"
        result_text.value = f"ID: {user_id[:8]}... を選択中。"
        page.update()

    # 4. 「保存 / 更新」処理 (POST / PATCH)
    def save_data(e):
        name = name_input.value.strip()
        if not name:
            result_text.value = "氏名を入力してください。"
            page.update()
            return

        payload = {"fields": {"name": {"stringValue": name}}}
        data = json.dumps(payload).encode('utf-8')

        try:
            if selected_data["id"] is None:
                # 新規作成 (POST)
                url = f"{BASE_URL}?key={API_KEY}"
                req = urllib.request.Request(
                    url, data=data,
                    headers={'Content-Type': 'application/json'},
                    method='POST'
                )
                with urllib.request.urlopen(req):
                    result_text.value = f"『{name}』を新規登録しました！"
            else:
                # 更新 (PATCH)
                doc_id = selected_data["id"]
                url = f"{BASE_URL}/{doc_id}?key={API_KEY}&updateMask.fieldPaths=name"
                req = urllib.request.Request(
                    url, data=data,
                    headers={'Content-Type': 'application/json'},
                    method='PATCH'
                )
                with urllib.request.urlopen(req):
                    result_text.value = f"データ（{name}）を更新しました！"

            clear_form()
            load_data()
        except Exception as ex:
            result_text.value = f"保存エラー: {ex}"
            page.update()

    # 5. 「削除」処理 (DELETE)
    def delete_data(user_id):
        try:
            url = f"{BASE_URL}/{user_id}?key={API_KEY}"
            req = urllib.request.Request(url, method='DELETE')
            with urllib.request.urlopen(req):
                result_text.value = f"データを削除しました。"

            if selected_data["id"] == user_id:
                clear_form()
            load_data()
        except Exception as ex:
            result_text.value = f"削除エラー: {ex}"
            page.update()

    # 画面の配置
    page.add(
        ft.Text("ユーザー管理アプリ（Firebase REST API完全版）", size=24, weight=ft.FontWeight.BOLD),
        name_input,
        ft.Row([
            ft.ElevatedButton("保存 / 更新", on_click=save_data, icon=ft.Icons.SAVE),
            ft.OutlinedButton("新規入力に戻す", on_click=lambda e: clear_form(), icon=ft.Icons.CLEAR),
            ft.IconButton(icon=ft.Icons.REFRESH, on_click=lambda e: load_data())
        ]),
        result_text,
        ft.Divider(),
        ft.Text("登録済みデータ一覧", size=18, weight=ft.FontWeight.BOLD),
        user_list
    )

    clear_form()
    load_data()

ft.app(target=main)