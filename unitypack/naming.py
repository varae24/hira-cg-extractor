"""资源命名与分类。

不同游戏命名习惯不同。这里提供一份「通用前缀」规则作为默认，
以及针对特定游戏的 profile 来给出更贴切的分组名。
"""

import re

_PFX = re.compile(r"^([A-Za-z]+?)(?=[0-9_]|$)")


def prefix_of(name):
    """取名字的字母前缀：ev002_a1 -> ev，chapter_m01 -> chapter"""
    m = _PFX.match(name or "")
    return (m.group(1) if m else (name or "")[:4]).lower()


def natural_key(name):
    """自然排序键：ev2 排在 ev10 前面。"""
    m = re.match(r"^([A-Za-z_]*)(\d*)(.*)$", name or "")
    if m and m.group(2):
        return (m.group(1), int(m.group(2)), m.group(3))
    return (name or "", 0, "")


# 通用默认：把最常见的视觉资源类别按前缀映射
DEFAULT_PREFIX_LABELS = {
    "ev": "事件 CG",
    "cg": "事件 CG",
    "bg": "场景背景",
    "background": "场景背景",
    "chara": "角色立绘",
    "character": "角色立绘",
    "chapter": "章节标题",
    "title": "标题画面",
}


class Profile:
    """一个命名 profile：把资源名字前缀归类到人读的中文分组。"""

    def __init__(self, name, labels=None, extra=None):
        self.name = name
        self.labels = dict(DEFAULT_PREFIX_LABELS)
        if labels:
            self.labels.update(labels)
        # extra: 额外的前缀 -> 分组，覆盖 labels
        if extra:
            self.labels.update(extra)

    def classify(self, asset_name):
        """返回 (分组名, 是否小图/缩略图)。"""
        p = prefix_of(asset_name)
        return self.labels.get(p, "UI / 特效"), False


# 针对 Hira Hira Hihiru 的 profile
PROFILE_HIHIRU = Profile(
    name="hihiru",
    labels={
        "ev": "CG",
        "bg": "场景背景",
        "chapter": "章节标题",
        "sactx": "UI Sprite 图集",
    },
)


PROFILES = {
    "hihiru": PROFILE_HIHIRU,
}


def get_profile(name):
    if not name or name == "generic":
        return Profile("generic")
    if name in PROFILES:
        return PROFILES[name]
    raise ValueError("未知 profile %r，可选：generic, %s"
                     % (name, ", ".join(sorted(PROFILES))))