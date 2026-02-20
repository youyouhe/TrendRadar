# coding=utf-8
"""
全国各省市政府采购网招标信息采集器

基于通用采集器框架，快速适配34个省级行政区
"""

from trendradar.crawler.tender.generic_ccgp import GenericCCGPSource


# ============================================
# 国家级平台
# ============================================

class ChinaCCGPSource(GenericCCGPSource):
    """中国政府采购网"""

    @property
    def source_code(self) -> str:
        return "china"

    @property
    def source_name(self) -> str:
        return "中国政府采购网"

    @property
    def base_url(self) -> str:
        return "http://www.ccgp.gov.cn/"


# ============================================
# 华北地区
# ============================================

class TianjinTenderSource(GenericCCGPSource):
    """天津市政府采购网"""

    @property
    def source_code(self) -> str:
        return "tianjin"

    @property
    def source_name(self) -> str:
        return "天津市政府采购网"

    @property
    def base_url(self) -> str:
        return "http://www.ccgp-tianjin.gov.cn/"


class HebeiTenderSource(GenericCCGPSource):
    """河北省政府采购网"""

    @property
    def source_code(self) -> str:
        return "hebei"

    @property
    def source_name(self) -> str:
        return "河北省政府采购网"

    @property
    def base_url(self) -> str:
        return "http://www.ccgp-hebei.gov.cn/"


class ShanxiTenderSource(GenericCCGPSource):
    """山西省政府采购网"""

    @property
    def source_code(self) -> str:
        return "shanxi"

    @property
    def source_name(self) -> str:
        return "山西省政府采购网"

    @property
    def base_url(self) -> str:
        return "http://www.ccgp-shanxi.gov.cn/"


class NeimengguTenderSource(GenericCCGPSource):
    """内蒙古政府采购网"""

    @property
    def source_code(self) -> str:
        return "neimenggu"

    @property
    def source_name(self) -> str:
        return "内蒙古政府采购网"

    @property
    def base_url(self) -> str:
        return "http://www.ccgp-neimenggu.gov.cn/"


# ============================================
# 东北地区
# ============================================

class LiaoningTenderSource(GenericCCGPSource):
    """辽宁省政府采购网"""

    @property
    def source_code(self) -> str:
        return "liaoning"

    @property
    def source_name(self) -> str:
        return "辽宁省政府采购网"

    @property
    def base_url(self) -> str:
        return "http://www.ccgp-liaoning.gov.cn/"


class JilinTenderSource(GenericCCGPSource):
    """吉林省政府采购网"""

    @property
    def source_code(self) -> str:
        return "jilin"

    @property
    def source_name(self) -> str:
        return "吉林省政府采购网"

    @property
    def base_url(self) -> str:
        return "http://www.ccgp-jilin.gov.cn/"


class HeilongjiangTenderSource(GenericCCGPSource):
    """黑龙江省政府采购网"""

    @property
    def source_code(self) -> str:
        return "heilongjiang"

    @property
    def source_name(self) -> str:
        return "黑龙江省政府采购网"

    @property
    def base_url(self) -> str:
        return "http://www.ccgp-heilongjiang.gov.cn/"


# ============================================
# 华东地区
# ============================================

class ShanghaiTenderSource(GenericCCGPSource):
    """上海市政府采购网"""

    @property
    def source_code(self) -> str:
        return "shanghai"

    @property
    def source_name(self) -> str:
        return "上海市政府采购网"

    @property
    def base_url(self) -> str:
        return "http://www.ccgp-shanghai.gov.cn/"


class JiangsuTenderSource(GenericCCGPSource):
    """江苏省政府采购网"""

    @property
    def source_code(self) -> str:
        return "jiangsu"

    @property
    def source_name(self) -> str:
        return "江苏省政府采购网"

    @property
    def base_url(self) -> str:
        return "http://www.ccgp-jiangsu.gov.cn/"


class ZhejiangTenderSource(GenericCCGPSource):
    """浙江政府采购网"""

    @property
    def source_code(self) -> str:
        return "zhejiang"

    @property
    def source_name(self) -> str:
        return "浙江政府采购网"

    @property
    def base_url(self) -> str:
        return "http://www.ccgp-zhejiang.gov.cn/"


class AnhuiTenderSource(GenericCCGPSource):
    """安徽省政府采购网"""

    @property
    def source_code(self) -> str:
        return "anhui"

    @property
    def source_name(self) -> str:
        return "安徽省政府采购网"

    @property
    def base_url(self) -> str:
        return "http://www.ccgp-anhui.gov.cn/"


class FujianTenderSource(GenericCCGPSource):
    """福建省政府采购网"""

    @property
    def source_code(self) -> str:
        return "fujian"

    @property
    def source_name(self) -> str:
        return "福建省政府采购网"

    @property
    def base_url(self) -> str:
        return "http://www.ccgp-fujian.gov.cn/"


class JiangxiTenderSource(GenericCCGPSource):
    """江西省政府采购网"""

    @property
    def source_code(self) -> str:
        return "jiangxi"

    @property
    def source_name(self) -> str:
        return "江西省政府采购网"

    @property
    def base_url(self) -> str:
        return "http://www.ccgp-jiangxi.gov.cn/"


# ============================================
# 华中地区
# ============================================

class HenanTenderSource(GenericCCGPSource):
    """河南省政府采购网"""

    @property
    def source_code(self) -> str:
        return "henan"

    @property
    def source_name(self) -> str:
        return "河南省政府采购网"

    @property
    def base_url(self) -> str:
        return "http://www.ccgp-henan.gov.cn/"


class HubeiTenderSource(GenericCCGPSource):
    """湖北省政府采购网"""

    @property
    def source_code(self) -> str:
        return "hubei"

    @property
    def source_name(self) -> str:
        return "湖北省政府采购网"

    @property
    def base_url(self) -> str:
        return "http://www.ccgp-hubei.gov.cn/"


class HunanTenderSource(GenericCCGPSource):
    """湖南省政府采购网"""

    @property
    def source_code(self) -> str:
        return "hunan"

    @property
    def source_name(self) -> str:
        return "湖南省政府采购网"

    @property
    def base_url(self) -> str:
        return "http://www.ccgp-hunan.gov.cn/"


# ============================================
# 华南地区
# ============================================

class GuangxiTenderSource(GenericCCGPSource):
    """广西政府采购网"""

    @property
    def source_code(self) -> str:
        return "guangxi"

    @property
    def source_name(self) -> str:
        return "广西政府采购网"

    @property
    def base_url(self) -> str:
        return "http://www.ccgp-guangxi.gov.cn/"


class HainanTenderSource(GenericCCGPSource):
    """海南省政府采购网"""

    @property
    def source_code(self) -> str:
        return "hainan"

    @property
    def source_name(self) -> str:
        return "海南省政府采购网"

    @property
    def base_url(self) -> str:
        return "http://www.ccgp-hainan.gov.cn/"


# ============================================
# 西南地区
# ============================================

class ChongqingTenderSource(GenericCCGPSource):
    """重庆市政府采购网"""

    @property
    def source_code(self) -> str:
        return "chongqing"

    @property
    def source_name(self) -> str:
        return "重庆市政府采购网"

    @property
    def base_url(self) -> str:
        return "http://www.ccgp-chongqing.gov.cn/"


class SichuanTenderSource(GenericCCGPSource):
    """四川政府采购网"""

    @property
    def source_code(self) -> str:
        return "sichuan"

    @property
    def source_name(self) -> str:
        return "四川政府采购网"

    @property
    def base_url(self) -> str:
        return "http://www.ccgp-sichuan.gov.cn/"


class GuizhouTenderSource(GenericCCGPSource):
    """贵州省政府采购网"""

    @property
    def source_code(self) -> str:
        return "guizhou"

    @property
    def source_name(self) -> str:
        return "贵州省政府采购网"

    @property
    def base_url(self) -> str:
        return "http://www.ccgp-guizhou.gov.cn/"


class YunnanTenderSource(GenericCCGPSource):
    """云南省政府采购网"""

    @property
    def source_code(self) -> str:
        return "yunnan"

    @property
    def source_name(self) -> str:
        return "云南省政府采购网"

    @property
    def base_url(self) -> str:
        return "http://www.ccgp-yunnan.gov.cn/"


class XizangTenderSource(GenericCCGPSource):
    """西藏自治区政府采购网"""

    @property
    def source_code(self) -> str:
        return "xizang"

    @property
    def source_name(self) -> str:
        return "西藏自治区政府采购网"

    @property
    def base_url(self) -> str:
        return "http://www.ccgp-xizang.gov.cn/"


# ============================================
# 西北地区
# ============================================

class ShaanxiTenderSource(GenericCCGPSource):
    """陕西省政府采购网"""

    @property
    def source_code(self) -> str:
        return "shaanxi"

    @property
    def source_name(self) -> str:
        return "陕西省政府采购网"

    @property
    def base_url(self) -> str:
        return "http://www.ccgp-shaanxi.gov.cn/"


class GansuTenderSource(GenericCCGPSource):
    """甘肃省政府采购网"""

    @property
    def source_code(self) -> str:
        return "gansu"

    @property
    def source_name(self) -> str:
        return "甘肃省政府采购网"

    @property
    def base_url(self) -> str:
        return "http://www.ccgp-gansu.gov.cn/"


class QinghaiTenderSource(GenericCCGPSource):
    """青海省政府采购网"""

    @property
    def source_code(self) -> str:
        return "qinghai"

    @property
    def source_name(self) -> str:
        return "青海省政府采购网"

    @property
    def base_url(self) -> str:
        return "http://www.ccgp-qinghai.gov.cn/"


class NingxiaTenderSource(GenericCCGPSource):
    """宁夏政府采购网"""

    @property
    def source_code(self) -> str:
        return "ningxia"

    @property
    def source_name(self) -> str:
        return "宁夏政府采购网"

    @property
    def base_url(self) -> str:
        return "http://www.ccgp-ningxia.gov.cn/"


class XinjiangTenderSource(GenericCCGPSource):
    """新疆政府采购网"""

    @property
    def source_code(self) -> str:
        return "xinjiang"

    @property
    def source_name(self) -> str:
        return "新疆政府采购网"

    @property
    def base_url(self) -> str:
        return "http://www.ccgp-xinjiang.gov.cn/"


# ============================================
# 省份采集器映射表
# ============================================

PROVINCE_SOURCES = {
    # 国家级
    "china": ChinaCCGPSource,

    # 华北
    "beijing": None,  # 使用专门的BeijingTenderSource
    "tianjin": TianjinTenderSource,
    "hebei": HebeiTenderSource,
    "shanxi": ShanxiTenderSource,
    "neimenggu": NeimengguTenderSource,

    # 东北
    "liaoning": LiaoningTenderSource,
    "jilin": JilinTenderSource,
    "heilongjiang": HeilongjiangTenderSource,

    # 华东
    "shanghai": ShanghaiTenderSource,
    "jiangsu": JiangsuTenderSource,
    "zhejiang": ZhejiangTenderSource,
    "anhui": AnhuiTenderSource,
    "fujian": FujianTenderSource,
    "jiangxi": JiangxiTenderSource,
    "shandong": None,  # 使用专门的ShandongTenderSource

    # 华中
    "henan": HenanTenderSource,
    "hubei": HubeiTenderSource,
    "hunan": HunanTenderSource,

    # 华南
    "guangdong": None,  # 使用专门的GuangdongTenderSource
    "guangxi": GuangxiTenderSource,
    "hainan": HainanTenderSource,

    # 西南
    "chongqing": ChongqingTenderSource,
    "sichuan": SichuanTenderSource,
    "guizhou": GuizhouTenderSource,
    "yunnan": YunnanTenderSource,
    "xizang": XizangTenderSource,

    # 西北
    "shaanxi": ShaanxiTenderSource,
    "gansu": GansuTenderSource,
    "qinghai": QinghaiTenderSource,
    "ningxia": NingxiaTenderSource,
    "xinjiang": XinjiangTenderSource,
}
