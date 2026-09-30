"""定位并只读解析 Unity 游戏的数据目录。"""

import os
import re

try:
    import UnityPy
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "缺少依赖 UnityPy。请先执行：\n"
        "    pip install -r requirements.txt"
    ) from exc


# 不含纹理/视频、纯粹是脚本或场景节点的文件可以跳过，但保留以便 --dry-run 报告
SKIP_SUFFIX = (".resS", ".resource", ".ress", ".mesh", ".tex", ".cubemap", ".shader")


def is_data_dir(path):
    """判断是否是 Unity 游戏的 <Game>_Data 目录。"""
    if not os.path.isdir(path):
        return False
    return os.path.isfile(os.path.join(path, "globalgamemanagers"))


def find_data_dir(game_dir):
    """从游戏目录（或其父目录）向上查找 <Game>_Data。

    game_dir 可以是游戏 exe 所在目录、_Data 目录本身，或它们的父目录。
    """
    game_dir = os.path.abspath(game_dir)
    if is_data_dir(game_dir):
        return game_dir
    # 向上找同名 _Data
    candidate = game_dir
    for _ in range(3):
        candidate = os.path.join(candidate, os.path.basename(candidate) + "_Data")
        if is_data_dir(candidate):
            return candidate
    # 在当前层枚举 *_Data
    try:
        for name in sorted(os.listdir(game_dir)):
            p = os.path.join(game_dir, name)
            if name.endswith("_Data") and is_data_dir(p):
                return p
    except OSError:
        pass
    # 再往上一层
    parent = os.path.dirname(game_dir)
    if parent and parent != game_dir:
        return find_data_dir(parent)
    return None


def list_source_files(data_dir):
    """列出 data_dir 中所有可解析的资源文件（.assets 与 level*）。

    自动排除 .resS/.resource 这类只含裸像素/字节的附属文件——它们由
    UnityPy 在解析 .assets 时按需自动挂载，不需要单独处理。
    """
    out = []
    for name in sorted(os.listdir(data_dir)):
        if name.endswith(SKIP_SUFFIX):
            continue
        full = os.path.join(data_dir, name)
        if not os.path.isfile(full):
            continue
        if name.endswith(".assets") or re.match(r"^level\d+$", name):
            out.append(name)
    return out


class AssetBundle:
    """对单个 Unity 资源文件的只读封装。"""

    def __init__(self, data_dir, filename):
        self.data_dir = data_dir
        self.filename = filename
        self.path = os.path.join(data_dir, filename)
        self.env = UnityPy.load(self.path)
        self.serialized = self.env.assets[0]
        self.objects = self.serialized.objects

    def objects_of_type(self, typename):
        """返回 [(path_id, ObjectReader), ...]"""
        return [(pid, o) for pid, o in self.objects.items() if o.type.name == typename]

    def textures(self):
        return self.objects_of_type("Texture2D")

    def videos(self):
        return self.objects_of_type("VideoClip")

    def close(self):
        self.env = None
        self.serialized = None
        self.objects = None

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
        return False


def load_all(data_dir, files, verbose=True):
    """逐个打开资源文件生成 AssetBundle；解析失败的文件会被跳过并记录。"""
    bundles, failed = [], []
    for name in files:
        try:
            bundles.append(AssetBundle(data_dir, name))
            if verbose:
                print("  [ok]   %s" % name)
        except Exception as exc:
            failed.append((name, str(exc)))
            if verbose:
                print("  [skip] %s -> %s: %s" % (name, type(exc).__name__, exc))
    return bundles, failed