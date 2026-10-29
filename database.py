import json
import base64
import requests
import streamlit as st
from datetime import date, timedelta
from pathlib import Path

# GitHub設定（Secretsから取得）
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")
GITHUB_REPO = st.secrets.get("GITHUB_REPO", "akkun-yamato/toilet-gacha")
HISTORY_FILE_PATH = "data/history.json"

GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{HISTORY_FILE_PATH}"
MEMBERS_FILE = Path("members.json")


# ========== GitHub API ヘルパー ==========

def _github_get():
    """GitHubから history.json を取得"""
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    r = requests.get(GITHUB_API_URL, headers=headers, timeout=10)
    r.raise_for_status()
    data = r.json()
    content = base64.b64decode(data["content"]).decode("utf-8")
    return json.loads(content), data["sha"]


def _github_put(content_dict, sha, message="Update history"):
    """GitHubに history.json を書き込み"""
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    content_str = json.dumps(content_dict, ensure_ascii=False, indent=2)
    encoded = base64.b64encode(content_str.encode("utf-8")).decode("utf-8")
    payload = {
        "message": message,
        "content": encoded,
        "sha": sha
    }
    r = requests.put(GITHUB_API_URL, headers=headers, json=payload, timeout=10)
    r.raise_for_status()


@st.cache_data(ttl=60)
def _load_data():
    """GitHubから最新データ取得（60秒キャッシュ）"""
    try:
        data, sha = _github_get()
        return data, sha
    except Exception as e:
        st.error(f"データ取得エラー: {e}")
        return {"history": [], "round_status": {"Men": {}, "Guest": {}, "Women": {}}}, None


def _save_data(data, sha, message="Update history"):
    """GitHubに保存＋キャッシュクリア"""
    _github_put(data, sha, message)
    st.cache_data.clear()


# ========== メンバー関連（members.jsonから直接読む） ==========

def init_db():
    """ダミー関数（互換性維持用）"""
    pass


def get_members(gender=None):
    """members.jsonからメンバー取得"""
    with open(MEMBERS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if gender == "M":
        return data["men"]
    elif gender == "F":
        return data["women"]
    else:
        return [(name, "M") for name in data["men"]] + [(name, "F") for name in data["women"]]


# ========== 履歴・round_status関連（GitHub保存） ==========

def _get_role_members(role):
    """役割別のメンバーリスト（members.jsonから）"""
    with open(MEMBERS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    if role in ("Men", "Guest"):
        return data["men"]
    elif role == "Women":
        return data["women"]
    return []


def get_recent_winners(role, days):
    """直近N日間の当選者を取得"""
    data, _ = _load_data()
    threshold = (date.today() - timedelta(days=days)).isoformat()
    winners = set()
    for h in data["history"]:
        if h["role"] == role and h["date"] > threshold:
            winners.add(h["member_name"])
    return list(winners)


def get_round_done(role):
    """今周当選済みのメンバー"""
    data, _ = _load_data()
    status = data["round_status"].get(role, {})
    return [name for name, done in status.items() if done]


def get_round_counts(role):
    """今周の進捗（済み/全体）"""
    data, _ = _load_data()
    members = _get_role_members(role)
    status = data["round_status"].get(role, {})
    total = len(members)
    done = sum(1 for name in members if status.get(name, False))
    return done, total


def save_result(winners):
    """抽選結果を保存＋round_status更新"""
    data, sha = _load_data()
    today = date.today().isoformat()
    
    # 当日の履歴を削除（上書き対応）
    data["history"] = [h for h in data["history"] if h["date"] != today]
    
    # 新しい履歴を追加
    for role, name in winners.items():
        if name:
            data["history"].append({
                "date": today,
                "role": role,
                "member_name": name
            })
            # round_status更新
            if role not in data["round_status"]:
                data["round_status"][role] = {}
            data["round_status"][role][name] = True
    
    # 全員当選済みチェック→リセット
    for role in ["Men", "Guest", "Women"]:
        members = _get_role_members(role)
        status = data["round_status"].get(role, {})
        all_done = all(status.get(name, False) for name in members)
        if all_done and members:
            data["round_status"][role] = {name: False for name in members}
    
    _save_data(data, sha, message=f"Save result {today}")


def get_history(limit=7):
    """直近N日の履歴（date, role, member_name のタプルリスト）"""
    data, _ = _load_data()
    sorted_history = sorted(data["history"], key=lambda x: x["date"], reverse=True)
    unique_dates = []
    seen_dates = set()
    for h in sorted_history:
        if h["date"] not in seen_dates:
            seen_dates.add(h["date"])
            unique_dates.append(h["date"])
        if len(unique_dates) >= limit:
            break
    
    result = []
    for h in sorted_history:
        if h["date"] in unique_dates:
            result.append((h["date"], h["role"], h["member_name"]))
    return result


def reset_round(role=None):
    """今周リセット"""
    data, sha = _load_data()
    if role:
        data["round_status"][role] = {}
    else:
        data["round_status"] = {"Men": {}, "Guest": {}, "Women": {}}
    _save_data(data, sha, message="Reset round")


def rename_member(old_name, new_name):
    """履歴内のメンバー名変更"""
    data, sha = _load_data()
    for h in data["history"]:
        if h["member_name"] == old_name:
            h["member_name"] = new_name
    for role, status in data["round_status"].items():
        if old_name in status:
            status[new_name] = status.pop(old_name)
    _save_data(data, sha, message=f"Rename {old_name} to {new_name}")


def clear_history():
    """全履歴を削除"""
    data, sha = _load_data()
    data["history"] = []
    data["round_status"] = {"Men": {}, "Guest": {}, "Women": {}}
    _save_data(data, sha, message="Clear history")
