"""Unity TextureFormat 枚举 -> 可读名称。

数值严格对应 Unity 官方 TextureFormat 枚举（Texture2D.m_TextureFormat）。
BC1/BC3 等是 DXT1/DXT5 的等价别名，标注在括号里便于检索。

注意：早期版本的本项目曾把 3/4/1/25 误标为 RGBA32/ARGB32/ARGB4444/DXT1Crunched，
实际分别是 RGB24/RGBA32/Alpha8/RGBDst16。已用「格式值 vs 导出图 alpha 通道」
交叉验证修正。
"""

# —— 未压缩 ——
UNCOMPRESSED = {
    1: "Alpha8", 2: "ARGB4444", 3: "RGB24", 4: "RGBA32", 5: "ARGB32",
    6: "ARGBFloat", 7: "RGB565", 8: "BGR565", 9: "R16",
    13: "RGBA4444", 14: "BGRA32", 15: "RHalf", 16: "RGHalf", 17: "RGBAHalf",
    18: "RFloat", 19: "RGFloat", 20: "RGBAFloat", 21: "YUY2", 22: "RGB9e5",
    23: "RGBFloat", 24: "YCbCr420", 25: "RGBDst16",
    62: "RG16", 63: "R8", 64: "RGB9e5Float", 65: "RGBHalf", 66: "RGFloat",
    67: "RGHalf", 68: "RFloat", 69: "BGRA32_SRGB", 70: "R16_SFLOAT",
    71: "RG32_SFLOAT", 72: "RGB32_SFLOAT", 73: "RGBA32_SFLOAT",
}

# —— 块压缩（D3D / BCn / ETC / ASTC）——
BLOCK_COMPRESSED = {
    10: "DXT1 (BC1)", 11: "DXT3 (BC2)", 12: "DXT5 (BC3)",
    26: "DXT1Crunched", 27: "DXT5Crunched",
    28: "PVRTC_RGB2", 29: "PVRTC_RGBA2", 30: "PVRTC_RGB4", 31: "PVRTC_RGBA4",
    32: "ETC_RGB4", 33: "ATC_RGB4", 34: "ATC_RGBA8",
    41: "EAC_R", 42: "EAC_R_SIGNED", 43: "EAC_RG", 44: "EAC_RG_SIGNED",
    45: "ETC2_RGB", 46: "ETC2_RGBA1", 47: "ETC2_RGBA8",
    60: "ETC_RGB4_3DS", 61: "ETC_RGBA8_3DS",
    74: "BC4", 75: "BC4_SIGNED", 76: "BC5", 77: "BC5_SIGNED",
    78: "BC6H", 79: "BC6H_SFLOAT", 80: "BC7", 81: "BC7_SFLOAT",
}

_ASTC_BLOCKS = {4, 5, 6, 8, 10, 12}
for _i, _b in enumerate(sorted(_ASTC_BLOCKS)):
    BLOCK_COMPRESSED[48 + _i] = "ASTC_RGB_%dx%d" % (_b, _b)
    BLOCK_COMPRESSED[54 + _i] = "ASTC_RGBA_%dx%d" % (_b, _b)

_TABLE = {}
for _t in (UNCOMPRESSED, BLOCK_COMPRESSED):
    _TABLE.update(_t)

_COMPRESSED_PREFIXES = (
    "DXT", "BC", "ASTC", "ETC", "ATC", "EAC", "PVRTC",
)


def texture_format_name(value):
    """把 m_TextureFormat 整数转成可读名称。"""
    if value is None:
        return ""
    if value in _TABLE:
        return _TABLE[value]
    return "Unknown(%s)" % value


def is_gpu_compressed(name):
    """是否是需要解码的 GPU 压缩格式（与 is_gpu_compressed 同义，便于外部调用）。"""
    return bool(name) and name.startswith(_COMPRESSED_PREFIXES)


def has_alpha(name):
    """该格式理论上是否带 alpha 通道。"""
    return not name.startswith(("RGB24", "RGB565", "BGR565", "YUY2", "YCbCr420"))