"""
Performax Hub - 플랫폼 서버
- Flask 로컬 서버
- 네이버 API 프록시
- 브라우저 자동 오픈
"""

import threading
import webbrowser
import requests
from flask import Flask, request, jsonify, render_template
import os
import sys
import sqlite3
import json
from datetime import datetime

# ── API 키 설정 ───────────────────────────────────────
# 네이버 데이터랩
NAVER_CLIENT_ID     = ""
NAVER_CLIENT_SECRET = ""

# 네이버 검색광고
SEARCHAD_API_KEY      = ""
SEARCHAD_SECRET_KEY   = ""
SEARCHAD_CUSTOMER_ID  = ""
# ─────────────────────────────────────────────────────

PORT = 5000

# ── DB 초기화 ─────────────────────────────────────────
DB_PATH = os.path.join(os.path.expanduser('~'), 'performax_hub.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS trend_history (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            keywords  TEXT,
            mode      TEXT,
            start_date TEXT,
            end_date  TEXT,
            time_unit TEXT,
            device    TEXT,
            gender    TEXT,
            ages      TEXT,
            created_at TEXT
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS query_history (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            keywords   TEXT,
            show_detail INTEGER,
            created_at TEXT
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key   TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    conn.commit()
    conn.close()
init_db()

# PyInstaller 경로 처리
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static'),
)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# ── 히스토리 API ──────────────────────────────────────

# ── 히스토리: 키워드 트렌드 분석 ─────────────────────────────
@app.route('/history/trend', methods=['GET'])
def get_trend_history():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        'SELECT * FROM trend_history ORDER BY created_at DESC LIMIT 20'
    ).fetchall()
    conn.close()
    cols = ['id','keywords','mode','start_date','end_date','time_unit','device','gender','ages','created_at']
    return jsonify([dict(zip(cols, r)) for r in rows])

@app.route('/history/trend', methods=['POST'])
def save_trend_history():
    data = request.get_json()
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
        INSERT INTO trend_history (keywords, mode, start_date, end_date, time_unit, device, gender, ages, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        json.dumps(data.get('keywords'), ensure_ascii=False),
        data.get('mode'),
        data.get('start_date'),
        data.get('end_date'),
        data.get('time_unit'),
        data.get('device', ''),
        data.get('gender', ''),
        data.get('ages', ''),
        datetime.now().strftime('%Y-%m-%d %H:%M'),
    ))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})

@app.route('/history/trend/<int:id>', methods=['DELETE'])
def delete_trend_history(id):
    conn = sqlite3.connect(DB_PATH)
    conn.execute('DELETE FROM trend_history WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})

# ── 히스토리: 키워드 쿼리 조회 ─────────────────────────────
@app.route('/history/query', methods=['GET'])
def get_query_history():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        'SELECT * FROM query_history ORDER BY created_at DESC LIMIT 20'
    ).fetchall()
    conn.close()
    cols = ['id','keywords','show_detail','created_at']
    return jsonify([dict(zip(cols, r)) for r in rows])

@app.route('/history/query', methods=['POST'])
def save_query_history():
    data = request.get_json()
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
        INSERT INTO query_history (keywords, show_detail, created_at)
        VALUES (?, ?, ?)
    ''', (
        json.dumps(data.get('keywords'), ensure_ascii=False),
        data.get('show_detail', 0),
        datetime.now().strftime('%Y-%m-%d %H:%M'),
    ))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})

@app.route('/history/query/<int:id>', methods=['DELETE'])
def delete_query_history(id):
    conn = sqlite3.connect(DB_PATH)
    conn.execute('DELETE FROM query_history WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})

# ── 페이지 라우팅 ─────────────────────────────────────
@app.route('/')
def index():
    return render_template('keyword_trend.html')

@app.route('/keyword-trend')
def keyword_trend():
    return render_template('keyword_trend.html')

@app.route('/keyword-query')
def keyword_query():
    return render_template('keyword_query.html')

@app.route('/utm-builder')
def utm_builder():
    return render_template('utm_builder.html')

# ── 구글 시트 읽기 ────────────────────────────────────
@app.route('/gsheet', methods=['POST'])
def gsheet():
    try:
        data       = request.get_json()
        sheet_url  = data.get('url', '')
        sheet_name = data.get('sheet', '')

        # 구글 시트 URL → CSV export URL 변환
        import re
        match = re.search(r'/d/([a-zA-Z0-9_-]+)', sheet_url)
        if not match:
            return jsonify({'error': '올바른 구글 시트 URL이 아닙니다.'}), 400

        sheet_id = match.group(1)
        csv_url  = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'

        res = requests.get(csv_url, timeout=10, verify=False)
        if res.status_code != 200:
            return jsonify({'error': '시트를 불러올 수 없습니다. 공유 설정을 확인해주세요.'}), 400

        return (res.text, 200, {'Content-Type': 'text/csv; charset=utf-8'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/settings', methods=['GET'])
def get_settings():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute('SELECT key, value FROM settings').fetchall()
    conn.close()
    return jsonify({r[0]: r[1] for r in rows})

@app.route('/settings', methods=['POST'])
def save_settings():
    data = request.get_json()
    conn = sqlite3.connect(DB_PATH)
    for key, value in data.items():
        conn.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (key, value))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})

# ── API 프록시: 네이버 데이터랩 ──────────────────────
@app.route('/datalab', methods=['POST'])
def datalab():
    try:
        res = requests.post(
            'https://openapi.naver.com/v1/datalab/search',
            headers={
                'Content-Type':          'application/json',
                'X-Naver-Client-Id':     NAVER_CLIENT_ID,
                'X-Naver-Client-Secret': NAVER_CLIENT_SECRET,
            },
            data=request.get_data(),
            timeout=10,
            verify=False,
        )
        return (res.text, res.status_code, {'Content-Type': 'application/json'})
    except requests.exceptions.ConnectionError:
        return jsonify({'error': '네트워크 연결을 확인해주세요.'}), 503
    except requests.exceptions.Timeout:
        return jsonify({'error': '요청 시간이 초과됐습니다. 다시 시도해주세요.'}), 504
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@app.route('/searchad/rel-kwd', methods=['POST'])
def rel_kwd():
    import hmac
    import hashlib
    import base64
    import time

    data        = request.get_json()
    keywords    = data.get('keywords', [])
    show_detail = data.get('showDetail', 0)

    def make_headers(method, path):
        timestamp = str(int(time.time() * 1000))
        message   = f"{timestamp}.{method}.{path}"
        signature = base64.b64encode(
            hmac.new(
                SEARCHAD_SECRET_KEY.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256,
            ).digest()
        ).decode('utf-8')
        return {
            'Content-Type': 'application/json; charset=UTF-8',
            'X-Timestamp':  timestamp,
            'X-API-KEY':    SEARCHAD_API_KEY,
            'X-Customer':   str(SEARCHAD_CUSTOMER_ID),
            'X-Signature':  signature,
        }

    try:
        all_keywords = []
        for i in range(0, len(keywords), 5):
            chunk   = keywords[i:i+5]
            headers = make_headers('GET', '/keywordstool')
            params  = {
                'hintKeywords': ','.join(chunk),
                'showDetail':   1,
            }
            res = requests.get(
                'https://api.naver.com/keywordstool',
                headers=headers,
                params=params,
                timeout=10,
                verify=False,
            )
            if res.status_code == 200:
                all_keywords.extend(res.json().get('keywordList', []))

        return jsonify({'keywordList': all_keywords}), 200

    except requests.exceptions.ConnectionError:
        return jsonify({'error': '네트워크 연결을 확인해주세요.'}), 503
    except requests.exceptions.Timeout:
        return jsonify({'error': '요청 시간이 초과됐습니다. 다시 시도해주세요.'}), 504
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ── API 프록시: 네이버 검색광고 ──────────────────────
@app.route('/searchad', methods=['GET', 'POST'])
def searchad():
    import hmac
    import hashlib
    import base64
    import time

    timestamp = str(int(time.time() * 1000))
    method    = request.method
    path      = request.args.get('path', '')

    # 서명 생성
    message   = f"{timestamp}.{method}.{path}"
    signature = base64.b64encode(
        hmac.new(
            SEARCHAD_SECRET_KEY.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256,
        ).digest()
    ).decode('utf-8')

    headers = {
        'Content-Type':        'application/json; charset=UTF-8',
        'X-Timestamp':         timestamp,
        'X-API-KEY':           SEARCHAD_API_KEY,
        'X-Customer':          str(SEARCHAD_CUSTOMER_ID),
        'X-Signature':         signature,
    }

    try:
        url = f'https://api.naver.com{path}'
        if method == 'GET':
            res = requests.get(url, headers=headers, params=request.args, timeout=10, verify=False)
        else:
            res = requests.post(url, headers=headers, data=request.get_data(), timeout=10, verify=False)
        return (res.text, res.status_code, {'Content-Type': 'application/json'})
    except requests.exceptions.ConnectionError:
        return jsonify({'error': '네트워크 연결을 확인해주세요.'}), 503
    except requests.exceptions.Timeout:
        return jsonify({'error': '요청 시간이 초과됐습니다. 다시 시도해주세요.'}), 504
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def open_browser():
    webbrowser.open(f'http://localhost:{PORT}')


if __name__ == '__main__':
    timer = threading.Timer(1.0, open_browser)
    timer.start()
    print(f'Performax Hub 실행 중 → http://localhost:{PORT}')
    print('종료하려면 이 창을 닫으세요.')
    app.run(port=PORT, debug=False)
