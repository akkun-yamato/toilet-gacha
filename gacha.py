import random
from database import get_members, get_recent_winners, get_round_done

NG_DAYS = {"Men": 7, "Guest": 7, "Women": 3}

def draw(role, absent_names):
    """
    指定役割の抽選
    """
    if role == "Women":
        pool = get_members("F")
    else:
        pool = get_members("M")
    
    available = [p for p in pool if p not in absent_names]
    if not available:
        return None
    
    done = get_round_done(role)
    not_done = [p for p in available if p not in done]
    
    recent = get_recent_winners(role, NG_DAYS[role])
    
    candidates = [p for p in not_done if p not in recent]
    if candidates:
        return random.choice(candidates)
    
    if not_done:
        return random.choice(not_done)
    
    return random.choice(available)

def draw_all(absent_names):
    """3役一気に抽選（同じ人が同日に2役兼任しないよう調整）"""
    results = {}
    extra_absent = list(absent_names)
    
    for role in ["Men", "Guest", "Women"]:
        winner = draw(role, extra_absent)
        results[role] = winner
        if winner:
            extra_absent.append(winner)
    
    return results
