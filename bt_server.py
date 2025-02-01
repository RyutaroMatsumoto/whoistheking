from flask import Flask, request, jsonify
import gspread
import pandas as pd
import numpy as np
from oauth2client.service_account import ServiceAccountCredentials
#from google.cloud import storage
import threading

app = Flask(__name__)

# --- 設定値 ---
# スプレッドシートのID（URL中の "1LX05LorDm5K-CzIhtGjDB0fZUkoCqk6jKXZ6eNAkjXw"）
SPREADSHEET_ID = "1LX05LorDm5K-CzIhtGjDB0fZUkoCqk6jKXZ6eNAkjXw"
# 対象のワークシート名
WORKSHEET_NAME = "2_1-7"
# eFootball の各プレイヤーの名前（表示順を決める）
EXPECTED_TEAMS = ["フジ", "ひかる", "たなちん", "まつりゅう", "なお"]

# --- Google Sheets API 接続 ---
def get_sheet():
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('efootball-bradley-terry-608153bca6d4.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet(WORKSHEET_NAME)
    return sheet

# --- Bradley–Terry モデルの推定 ---
def compute_bradley_terry(data):
    """
    data: シートから読み込んだ2行目以降のリスト（各行は [team1, team2, winner]）
    戻り値: { team名: β 値 } の辞書
    """
    # まず、データからすべてのチーム名を集める
    teams = set()
    for row in data:
        if len(row) < 3:
            continue
        team1 = row[0].strip()
        team2 = row[1].strip()
        winner = row[2].strip()
        if team1: teams.add(team1)
        if team2: teams.add(team2)
        if winner: teams.add(winner)
    teams = list(teams)
    teams.sort()  # 内部処理用にアルファベット順（または日本語順）にソート
    team_index = {team: i for i, team in enumerate(teams)}
    n_teams = len(teams)
    
    # 勝数行列と対戦数行列を初期化
    wins = [[0 for _ in range(n_teams)] for _ in range(n_teams)]
    matches = [[0 for _ in range(n_teams)] for _ in range(n_teams)]
    
    # 各行（試合）のデータを処理
    for row in data:
        if len(row) < 3:
            continue
        team1 = row[0].strip()
        team2 = row[1].strip()
        winner = row[2].strip()
        if team1 == "" or team2 == "" or winner == "":
            continue
        i = team_index[team1]
        j = team_index[team2]
        # 両チームの対戦数をカウント
        matches[i][j] += 1
        matches[j][i] += 1
        # 勝利した方の勝数をカウント
        if winner == team1:
            wins[i][j] += 1
        elif winner == team2:
            wins[j][i] += 1
        else:
            # 勝者がどちらとも一致しない場合はスキップ
            continue
    
    # 各チームの総勝利数
    total_wins = [sum(wins[i]) for i in range(n_teams)]
    
    # β の初期値をすべて 1.0 に設定
    beta = [1.0 for _ in range(n_teams)]
    
    # MMアルゴリズムによる反復更新
    max_iter = 1000
    tol = 1e-6
    for iteration in range(max_iter):
        beta_new = beta.copy()
        max_change = 0.0
        for i in range(n_teams):
            denominator = 0.0
            for j in range(n_teams):
                if i == j:
                    continue
                if matches[i][j] > 0:
                    denominator += matches[i][j] / (beta[i] + beta[j])
            if denominator > 0:
                beta_new[i] = total_wins[i] / denominator
            else:
                beta_new[i] = beta[i]
            change = abs(beta_new[i] - beta[i])
            if change > max_change:
                max_change = change
        beta = beta_new
        if max_change < tol:
            break
    
    # 正規化：最も高い β を 1.0 にする
    max_beta = max(beta)
    if max_beta > 0:
        beta = 10*[b / max_beta for b in beta]
    
    # チーム名と β の辞書を返す
    result = {team: beta[team_index[team]] for team in teams}
    return result

# --- シートのデータ取得＋β更新処理 ---
def process_sheet_data():
    try:
        sheet = get_sheet()
        # 1行目はヘッダーなので、2行目以降の全データを取得
        all_values = sheet.get_all_values()
        data = all_values[1:]  # ヘッダを除く
        print("取得データ件数:", len(data))
        
        # Bradley–Terry モデルで β を推定
        bt_result = compute_bradley_terry(data)
        print("BT推定結果:", bt_result)
        
        # 表示用に、EXPECTED_TEAMS の順序で β を抽出（各セルは小数点第4位まで）
        update_values = []
        for team in EXPECTED_TEAMS:
            if team in bt_result:
                update_values.append(round(bt_result[team], 4))
            else:
                update_values.append("N/A")
        
        # シート内のセル E2:I2（＝2行目の5列目～9列目）に更新
        update_range = "E2:I2"
        # gspread の update() では、1 行分のリストを内包するリストを渡す
        sheet.update(update_range, [update_values])
        print("シート更新完了:", update_values)
    except Exception as e:
        print("処理中エラー:", e)

# --- Flask エンドポイント ---
@app.route('/update', methods=['POST'])
def update():
    data = request.get_json()
    print("Apps Script から更新通知受信:", data)
    # シート処理は別スレッドで実行（応答を素早く返すため）
    threading.Thread(target=process_sheet_data).start()
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    # 外部からアクセス可能にするため、host='0.0.0.0' として起動（ngrok等で公開）
    app.run(host='0.0.0.0', port=5050)
