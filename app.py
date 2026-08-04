import flet as ft
import httpx

# --- ご自身の Firebase 設定 ---
API_KEY = "AIzaSyCoe94vJu0Srjt_yP1Nym5UMMGPt0MWngg"
PROJECT_ID = "flet-user-app"

BASE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/users"


def main(page: ft.Page):
    page.title = "ユーザー管理アプリ (Firebase REST API)"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20

    selected_data = {"id": None}

    name_input = ft.TextField(label="氏名を入力", width=300)
    result_text = ft.Text(value="", color=ft.Colors.BLUE)
    user_list = ft.Column()

    def clear_form():
        selected_data["id"] = None
        name_input.value = ""
        name_input.label = "氏名を入力（新規登録モード）"
        page.update()

    # 1. データ読み込み (httpx 使用)
    def load_data(e=None):
        user_list.controls.clear()
        try:
            url = f"{BASE_URL}?key={API_KEY}"
            # httpx を使用（Web環境でも動作）
            with httpx.Client() as client:
                res = client.get(url)
                response_data = res.json()

            if "documents" in response_data:
                for doc in response_data["documents"]:
                    doc_path = doc["name"]
                    doc_id = doc_path.split("/")[-1]
                    fields = doc.get("fields", {})
                    user_name = fields.get("name", {}).get("stringValue", "(名前なし)")

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
            result_text.value = "データを読み込みました。"
        except Exception as ex:
            result_text.value = f"取得エラー: {ex}"
        page.update()

    def select_user(user_id, user_name):
        selected_data["id"] = user_id
        name_input.value = user_name
        name_input.label = f"ID: {user_id[:8]}... の氏名を編集"
        page.update()

    # 2. 保存 / 更新 (httpx 使用)
    def save_data(e):
        name = name_input.value.strip()
        if not name:
            result_text.value = "氏名を入力してください。"
            page.update()
            return

        payload = {"fields": {"name": {"stringValue": name}}}

        try:
            with httpx.Client() as client:
                if selected_data["id"] is None:
                    # 新規登録
                    url = f"{BASE_URL}?key={API_KEY}"
                    client.post(url, json=payload)
                    result_text.value = f"『{name}』を新規登録しました！"
                else:
                    # 更新
                    doc_id = selected_data["id"]
                    url = f"{BASE_URL}/{doc_id}?key={API_KEY}&updateMask.fieldPaths=name"
                    client.patch(url, json=payload)
                    result_text.value = f"データを更新しました！"

            clear_form()
            load_data()
        except Exception as ex:
            result_text.value = f"保存エラー: {ex}"
            page.update()

    # 3. 削除 (httpx 使用)
    def delete_data(user_id):
        try:
            url = f"{BASE_URL}/{user_id}?key={API_KEY}"
            with httpx.Client() as client:
                client.delete(url)
            result_text.value = "データを削除しました。"

            if selected_data["id"] == user_id:
                clear_form()
            load_data()
        except Exception as ex:
            result_text.value = f"削除エラー: {ex}"
            page.update()

    # 画面レイアウト
    page.add(
        ft.Text("ユーザー管理アプリ (Firebase REST API)", size=24, weight=ft.FontWeight.BOLD),
        name_input,
        ft.Row([
            ft.ElevatedButton("保存 / 更新", on_click=save_data, icon=ft.Icons.SAVE),
            ft.OutlinedButton("新規入力に戻す", on_click=lambda e: clear_form(), icon=ft.Icons.CLEAR),
            ft.IconButton(icon=ft.Icons.REFRESH, on_click=load_data)
        ]),
        result_text,
        ft.Divider(),
        ft.Text("登録済みデータ一覧", size=18, weight=ft.FontWeight.BOLD),
        user_list
    )

    clear_form()
    load_data()

ft.app(target=main)