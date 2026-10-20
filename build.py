# -*- coding: utf-8 -*-
"""
机票.CC 静态站点生成器
------------------------------------------------------------------
单一数据源 -> 生成 SEO 友好的静态 HTML + 前端数据层(data.js)

运行：
    python build.py
输出：
    site/*.html
    site/assets/js/data.js
"""
import json
import re
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
# 站点主域：机票.CC 的正确 punycode 为 xn--nqvq81b.cc（与仓库根目录 CNAME 保持一致）
BASE_URL = "https://xn--nqvq81b.cc"

SITE = {
    "name": "机票.CC",
    "domain_cn": "机票.CC",
    "punycode": "xn--nqvq81b.cc",
    "tagline": "机票资讯 · 航司导航 · 出行攻略",
    "desc": "机票.CC 是聚焦航空公司导航、航线资讯、出行攻略、航司动态与优惠活动的机票资讯站点，帮助出行者判断预订时机、读懂票价规律。",
    "agent_email": "mfujun88@agent.qq.com",
    "updated": "2026-10-21",
    "icp": "备案信息办理中",
}

MAILTO = f"mailto:{SITE['agent_email']}"
# 统一订阅主题（CRO I6：全站 subject 一致，便于归因）
SUBJECT = "订阅机票资讯：机票.CC"
MAILTO_SUB = f"mailto:{SITE['agent_email']}?subject={quote(SUBJECT)}"
# 统一 CTA 文案（CRO I2）
CTA_SUB = "✉ 订阅机票资讯"

NAV = [
    ("index.html", "首页"),
    ("price.html", "航空公司导航"),
    ("routes.html", "航线资讯"),
    ("guides.html", "出行攻略"),
    ("airlines.html", "航司动态"),
    ("deals.html", "优惠活动"),
    ("about.html", "关于我们"),
]

# 站点定位（来自 Phase 1 研究 Brief）
POSITIONING = "不卖票的机票信息站"
POSITIONING_SUB = "把「机票什么时候买、怎么买才不亏」这件事，用可核对的数据和中立的态度讲清楚。"

# E-E-A-T：更新戳与复核周期
STAMP = {
    "updated": SITE["updated"],
    "next_review_price": "2026-11-10",   # 数据页：月度复核
    "next_review_rule": "2027-01-10",    # 规则页：季度复核
}

COLUMNS = [
    {"file": "price.html", "ico": "🧭", "name": "航空公司导航", "short": "航司导航",
     "desc": "48 家国内外航空公司及在线旅行平台的官网入口，卡片式导航，直达官方渠道查询航班与票价。",
     "freq": "每周复核"},
    {"file": "routes.html", "ico": "🗺️", "name": "航线资讯", "short": "航线资讯",
     "desc": "干线、季节性、高原、区域与国际航线的班次结构与运力变化解读。",
     "freq": "每日更新"},
    {"file": "guides.html", "ico": "🧭", "name": "出行攻略", "short": "出行攻略",
     "desc": "购票时机、退改签规则、中转联程、行李额度与出行保障的实操方法。",
     "freq": "每周 2-3 篇"},
    {"file": "airlines.html", "ico": "🛫", "name": "航司动态", "short": "航司动态",
     "desc": "航季调整、航线恢复、行李与会员规则变更的集中梳理。",
     "freq": "每日更新"},
    {"file": "deals.html", "ico": "🎫", "name": "优惠活动", "short": "优惠活动",
     "desc": "早鸟、会员日、联程与人群优惠的规则解读与价值判断框架。",
     "freq": "每周一更新"},
]

# ----------------------------------------------------------------------
# 航空公司导航（price.html 卡片式导航）
# ----------------------------------------------------------------------
# 48 家：国内客运航司 + 中国港澳台地区航司 + 在线旅行平台（携程/同程）。
# 字段：航空公司名称、官网域名、备注（"" 或 "ota" 在线旅行平台）。
# 域名由站长提供；本站仅作官网入口导航，不代售、不导流下单。
AIRLINES_NAV = [
    ("中国国际航空", "www.airchina.com.cn", ""),
    ("中国东方航空", "www.ceair.com", ""),
    ("中国南方航空", "www.csair.cn", ""),
    ("海南航空", "www.hnair.com", ""),
    ("厦门航空", "www.xiamenair.com", ""),
    ("四川航空", "www.sichuanair.com", ""),
    ("山东航空", "www.sda.cn", ""),
    ("深圳航空", "www.shenzhenair.com", ""),
    ("上海航空", "www.ceair.com", ""),
    ("春秋航空", "www.ch.com", ""),
    ("吉祥航空", "www.juneyaoair.com", ""),
    ("中国联合航空", "www.flycua.com", ""),
    ("九元航空", "www.9air.com", ""),
    ("奥凯航空", "www.okair.net", ""),
    ("首都航空", "www.jdair.net", ""),
    ("天津航空", "www.tianjin-air.com", ""),
    ("祥鹏航空", "www.luckyair.net", ""),
    ("西部航空", "www.westair.cn", ""),
    ("福州航空", "www.fuzhou-air.cn", ""),
    ("金鹏航空", "www.yzr.com.cn", ""),
    ("长安航空", "www.airchangan.com", ""),
    ("乌鲁木齐航空", "www.urumqi-air.com", ""),
    ("华夏航空", "www.chinaexpressair.com", ""),
    ("成都航空", "www.cdal.com.cn", ""),
    ("西藏航空", "www.airxizang.com", ""),
    ("青岛航空", "www.qdairlines.com", ""),
    ("湖南航空", "www.redair.cn", ""),
    ("多彩贵州航空", "www.cgzair.com", ""),
    ("江西航空", "www.airjiangxi.com", ""),
    ("北部湾航空", "www.gxairlines.com", ""),
    ("昆明航空", "www.airkunming.com", ""),
    ("龙江航空", "www.longjianghk.com", ""),
    ("河北航空", "www.hbhk.com.cn", ""),
    ("长龙航空", "www.loongair.cn", ""),
    ("东海航空", "www.donghaiair.com", ""),
    ("幸福航空", "www.joy-air.com", ""),
    ("中华航空", "www.china-airlines.com", ""),
    ("长荣航空", "www.evaair.com", ""),
    ("立荣航空", "www.uniair.com.tw", ""),
    ("华信航空", "www.mandarin-airlines.com", ""),
    ("台湾虎航", "www.tigerairtw.com", ""),
    ("星宇航空", "www.starlux-airlines.com", ""),
    ("国泰航空", "www.cathaypacific.com", ""),
    ("香港航空", "www.hongkongairlines.com", ""),
    ("香港快运航空", "www.hkexpress.com", ""),
    ("澳门航空", "www.airmacau.com.mo", ""),
    ("携程", "t.ctrip.cn/wvJ3M20", "ota"),
    ("同程旅行", "www.ly.com", "ota"),
]

ROUTES = [
    ("r1", "京沪空中快线再加密：日班次与时刻分布梳理", "干线", "2026-10-09", 6, True,
     "京沪航线是国内最繁忙的商务干线之一。本文梳理该航线的班次密度、早晚高峰时刻分布，以及不同时段的价格梯度规律。"),
    ("r2", "冬季冰雪航线观察：东北方向运力与票价节奏", "季节性", "2026-10-08", 7, False,
     "每年 11 月至次年 2 月是东北方向出行高峰。航线运力投放、雪季前后的价格拐点，是我们持续跟踪的重点。"),
    ("r3", "进藏航线怎么选：成都、重庆、西安三大中转点对比", "高原", "2026-10-08", 9, True,
     "高原航线受机型、天气与保障能力影响较大。本文对比三个主要中转城市的班次、机型适配与准点表现差异。"),
    ("r4", "粤港澳大湾区航线网络：广州、深圳、珠海如何分工", "区域", "2026-10-07", 8, False,
     "同一目的地，从广州、深圳还是珠海出发更合适？三地航线覆盖的差异，直接决定了你的出行备选方案。"),
    ("r5", "西北长航线盘点：乌鲁木齐、喀什方向的时刻与经停", "长航线", "2026-10-06", 7, False,
     "长距离航线普遍存在直飞与经停两类选择，耗时与价格差异明显。本文整理主要目的地的航线形态。"),
    ("r6", "东南亚短途航线：热门目的地班次与淡旺季差异", "国际", "2026-10-06", 8, False,
     "东南亚短途航线受节假日影响显著。梳理主要目的地的班次密度与价格波动区间，帮助你判断预订窗口。"),
    ("r7", "新开航线追踪：近期新增与复航航线一览", "新航线", "2026-10-05", 5, True,
     "新开航线往往在开航初期有价格优势。我们按月整理新增、复航与加密的航线信息，供你规划行程时参考。"),
    ("r8", "支线机场出行：从二三线城市出发的联程思路", "支线", "2026-10-04", 6, False,
     "支线机场直飞选择有限，联程与中转是常见方案。本文说明联程票与分开购票在改退签上的差异。"),
    ("r9", "中国港澳台地区航线：通关与行程衔接要点", "地区", "2026-10-03", 7, False,
     "中国香港、中国澳门、中国台湾地区航线的行程衔接与证件准备要点梳理，帮助你减少中转等待与误机风险。"),
]

GUIDES = [
    ("g1", "机票什么时候买最划算？基于价格曲线的预订窗口分析", "购票技巧", "2026-10-09", 10, True,
     "同一航线在不同提前期价格差异明显。本文用价格曲线说明「提前多久买」这件事为什么没有统一答案。"),
    ("g2", "特价票的退改签陷阱：低价背后的真实成本", "避坑指南", "2026-10-08", 8, False,
     "低票价不等于低总成本。退改规则、行李额度、选座费用，都会改变一次出行的真实支出。"),
    ("g3", "中转联程怎么买更稳？行李直挂与衔接时间判断", "中转联程", "2026-10-07", 9, True,
     "中转方案的核心风险在衔接。如何判断最小衔接时间是否够用、行李能否直挂，本文给出可操作的判断方法。"),
    ("g4", "带娃出行全流程：婴儿票、儿童票与值机注意事项", "家庭出行", "2026-10-06", 9, False,
     "婴儿票与儿童票的适用年龄、证件要求、行李与座位安排各不相同，出行前需要提前确认清楚。"),
    ("g5", "行李额度避坑：免费托运、超重计费与随身携带规则", "行李规则", "2026-10-05", 7, False,
     "不同舱位、不同航司的免费行李额度差异较大。本文梳理判断方法与常见的超重计费逻辑。"),
    ("g6", "航班延误与取消：旅客可以主张哪些权益", "出行保障", "2026-10-04", 8, False,
     "延误发生后，改签、退票、食宿安排分别适用什么条件？本文梳理旅客常见权益与处理流程。"),
    ("g7", "第一程航班：值机、安检与登机的时间账怎么算", "机场流程", "2026-10-03", 6, False,
     "不同机场、不同时段的通行效率差异明显。给出一个可复用的「倒推时间表」，帮助你留足余量。"),
    ("g8", "里程与积分怎么用？常旅客计划的入门判断", "常旅客", "2026-10-02", 9, False,
     "里程价值取决于兑换场景与航司联盟。本文帮助你判断：对你而言，累积里程到底值不值得。"),
]

AIRLINES = [
    ("2026-10-09", "示例航空 MU", "冬春航季运力调整，多条干线班次加密", "航季调整",
     "进入冬春航季，干线与旅游航线运力投放结构发生变化。旅客可关注航班时刻调整带来的衔接变化。"),
    ("2026-10-07", "示例航空 CZ", "部分国际航线恢复运营，中转方案增加", "航线恢复",
     "随着国际航线逐步恢复，经主要枢纽中转的选择增多，联程方案的组合空间随之扩大。"),
    ("2026-10-05", "示例航空 HU", "行李规则更新：部分舱位免费额度调整", "规则变更",
     "行李规则调整会直接影响出行成本核算，购票前建议以航司官方页面展示的规则为准。"),
    ("2026-10-03", "示例航空 CA", "值机与选座服务线上化率提升", "服务升级",
     "线上值机与选座覆盖范围扩大，旅客可提前完成部分流程，减少机场排队时间。"),
    ("2026-10-01", "示例航空 3U", "高原航线机型调整，保障能力说明", "机队动态",
     "高原航线对机型与运行保障要求较高，机型调整可能影响班次安排，请以实际查询结果为准。"),
    ("2026-09-28", "示例航空 ZH", "会员权益体系调整，里程累积规则变化", "会员计划",
     "常旅客计划的累积与兑换规则调整，会影响里程的实际价值判断。"),
]

DEALS = [
    ("d1", "冬春航季早鸟活动：提前预订的折扣策略观察", "示例航空 MU", "早鸟折扣", "2026-11-15", True,
     "早鸟活动通常附带较严格的退改限制。本文说明如何评估「折扣是否值得锁定」。"),
    ("d2", "会员日价格波动观察：固定促销节点的规律", "多家航司", "会员日", "每月循环", False,
     "会员日是价格波动的常见节点。我们按月跟踪主要航司的会员日安排与价格表现。"),
    ("d3", "中转联程组合优惠：联程票与分开购票的价差分析", "示例航空 CZ", "联程优惠", "2026-12-31", False,
     "联程票在行李直挂与改签保障上有优势，价格未必最低。是否需要为保障多付差价，本文给出判断框架。"),
    ("d4", "错峰出行指南：非高峰日期的价格洼地", "全行业", "错峰出行", "长期有效", True,
     "同一航线在周中与周末的价差往往明显。本文说明如何识别错峰窗口。"),
    ("d5", "信用卡与出行权益：积分兑换机票的适用场景", "多家银行", "权益兑换", "长期有效", False,
     "积分兑换机票的价值取决于兑换比例与可用舱位，并非所有场景都划算。"),
    ("d6", "学生与长者优惠：特殊人群购票的证件与限制", "多家航司", "人群优惠", "长期有效", False,
     "特殊人群优惠通常需要满足年龄与证件条件，且退改限制较多，购票前需逐条确认。"),
]

# ----------------------------------------------------------------------
# 文章注册表
# ----------------------------------------------------------------------
# 日更文章在此登记一条即可，其余（文章页 HTML / 所属栏目列表 / sitemap.xml /
# 站内搜索索引）全部由 build.py 自动处理。沿用既有页面模板与样式，不新增设计。
#
# 字段说明：
#   slug            产出 <slug>.html
#   drafts          草稿候选文件名（相对 ../drafts/，按顺序取第一个存在的）
#   column          所属栏目页文件名（决定面包屑与导航高亮、栏目列表归属）
#   column_name     栏目中文名
#   date            文章发布日期
#   review/scope    E-E-A-T 下次复核日期与复核类别
#   keywords        Article JSON-LD 的 keywords
#   cat_label       栏目列表里显示的标签
#   summary         栏目列表里的一句话摘要
#   about_note      文末「关于本文」段落正文
#   head_desc_extra <title> 之外补充进 meta description 的句子
# ----------------------------------------------------------------------
ARTICLES = [
    {
        "slug": "best-time-to-buy",
        "drafts": ["best-time-to-buy-2026-10-10-v2.md", "best-time-to-buy-2026-10-10.md"],
        "column": "guides.html",
        "column_name": "出行攻略",
        "date": "2026-10-10",
        "review": STAMP["next_review_rule"],
        "scope": "规则与攻略",
        "title_fallback": "机票什么时候买最便宜",
        "head_desc_extra": "本文按国内/国际、淡旺季、周内与日内时段给出完整时间表，并说明价格规律与避坑要点。",
        "keywords": "机票什么时候买最便宜,机票提前多久买,机票价格规律,国内机票,国际机票",
        "cat_label": "购票技巧",
        "summary": "为什么「提前 30 天」不是一个通用答案。",
        "about_note": "本文为机票.CC「出行攻略」栏目的价格规律专题，文中价格为公开渠道整理的参考区间，"
                      "波动频繁，请以航空公司官方渠道实时公示为准。本站不销售机票、不参与任何交易环节。",
    },
    {
        "slug": "post-holiday-low-fares",
        "drafts": ["post-holiday-low-fares-2026-10-11.md"],
        "column": "deals.html",
        "column_name": "优惠活动",
        "date": "2026-10-11",
        "review": STAMP["next_review_price"],
        "scope": "数据",
        "title_fallback": "节后机票价格降三成",
        "meta_title": "节后机票价格降三成：错峰出行低价窗口怎么抓-机票.CC",
        "head_desc_extra": "文中含节后错峰时间结构表、主要客源地低价航线样本、下单前核对清单与错峰购票 FAQ。",
        "keywords": "节后机票价格,错峰出行,低价机票什么时候买,机票淡季,节后特价机票",
        "cat_label": "错峰出行",
        "summary": "平均支付价较十一低三成以上——窗口边界、航线结构与核对清单。",
        "about_note": "本文为机票.CC「优惠活动」栏目的错峰出行专题，文中价格均为公开渠道整理的参考区间，"
                      "标注统计口径与时间范围；价格实时变动，请以航空公司官方渠道实时展示为准。"
                      "本站不销售机票、不参与任何交易环节。",
    },
    {
        "slug": "winter-schedule-2026",
        "drafts": ["winter-schedule-2026-2026-10-11.md"],
        "column": "routes.html",
        "column_name": "航线资讯",
        "date": "2026-10-11",
        "review": STAMP["next_review_rule"],
        "scope": "规则与动态",
        "title_fallback": "冬春航季10月25日换季",
        "meta_title": "冬春航季10月25日换季：新开航线与班次调整怎么影响购票-机票.CC",
        "head_desc_extra": "文中含换季机制说明、新开与加密航线方向表、跨航季购票四个实操建议与 FAQ。",
        "keywords": "冬春航季,航班换季,新开航线,航线加密,换季航班时刻",
        "cat_label": "航季换季",
        "summary": "10 月 25 日换季：直飞保留、班次密度与时刻的三重变化怎么应对。",
        "about_note": "本文为机票.CC「航线资讯」栏目的换季专题，文中航线与班次信息整理自公开渠道，"
                      "以各航司最终执行的航班计划为准。本站不销售机票、不参与任何交易环节。",
    },
    {
        "slug": "flight-vs-train",
        "drafts": ["flight-vs-train-2026-10-11.md"],
        "column": "guides.html",
        "column_name": "出行攻略",
        "date": "2026-10-11",
        "review": STAMP["next_review_rule"],
        "scope": "规则与攻略",
        "title_fallback": "机票比高铁便宜时怎么选",
        "meta_title": "机票比高铁便宜时怎么选：一张决策清单算清总成本-机票.CC",
        "head_desc_extra": "文中含五种成本维度对比表、机票占优场景表与下单前六步决策清单。",
        "keywords": "机票比高铁便宜,机票和高铁怎么选,机票总成本,门到门时间,低价机票攻略",
        "cat_label": "比价决策",
        "summary": "裸价便宜不等于总成本便宜：五个维度、六步清单把账算清。",
        "about_note": "本文为机票.CC「出行攻略」栏目的比价决策专题，文中价格均为公开渠道整理的参考区间，"
                      "标注统计口径与时间范围；机票与高铁价格实时变动，请以官方渠道为准。"
                      "本站不销售机票、不参与任何交易环节。",
    },
    {
        "slug": "winter-airline-capacity",
        "drafts": ["winter-airline-capacity-2026-10-11.md"],
        "column": "airlines.html",
        "column_name": "航司动态",
        "date": "2026-10-11",
        "review": STAMP["next_review_rule"],
        "scope": "规则与动态",
        "title_fallback": "冬春航季航司运力调整",
        "meta_title": "冬春航季航司运力调整：国际航班增长与购票机会在哪-机票.CC",
        "head_desc_extra": "文中含运力变化类型表、国际航线方向表，以及换季动态转化为购票决策的四条思路。",
        "keywords": "冬春航季运力,航司运力调整,国际航班恢复,国际机票什么时候买,换季购票",
        "cat_label": "航季调整",
        "summary": "国内平稳、国际恢复：运力增量在哪，价格洼地就在哪。",
        "about_note": "本文为机票.CC「航司动态」栏目的换季运力专题，文中运力与航线信息整理自公开渠道并标注时间口径，"
                      "各航司最终执行计划可能调整，请以官方渠道为准。本站不销售机票、不参与任何交易环节。",
    },
    {
        "slug": "fuel-surcharge",
        "drafts": ["fuel-surcharge-2026-10-10.md"],
        "column": "guides.html",
        "column_name": "出行攻略",
        "date": "2026-10-10",
        "review": STAMP["next_review_price"],
        "scope": "数据",
        "title_fallback": "机票燃油附加费上调",
        "meta_title": "机票燃油附加费10月10日起上调：机票预定该提前还是再等-机票.CC",
        "head_desc_extra": "文中含新旧征收标准对照、2026 年内调价轨迹、节后票价区间参考，以及「该提前还是再等」的判断清单。",
        "keywords": "机票燃油附加费上调,机票预定,机票预订什么时候买,燃油附加费怎么算,机建燃油费,节后机票价格",
        "cat_label": "价格解读",
        "summary": "附加费涨 10–20 元，基础票价降数百元——净成本账怎么算？",
        "about_note": "本文为机票.CC「出行攻略」栏目的价格构成解读，文中价格与附加费标准均整理自公开渠道，"
                      "并标注统计口径与时间范围；相关政策随时可能调整，请以航空公司官方渠道与出票页面展示为准。"
                      "本站不销售机票、不参与任何交易环节。",
    },
    {
        "slug": "airline-membership-promotions-nov-2026",
        "drafts": ["airline-membership-promotions-nov-2026-10-12.md"],
        "column": "deals.html",
        "column_name": "优惠活动",
        "date": "2026-10-12",
        "review": STAMP["next_review_rule"],
        "scope": "规则与活动",
        "title_fallback": "春秋会员权益调整 + 双 11 机票促销日历",
        "meta_title": "春秋航空会员权益调整 + 双 11 机票促销日历：11 月 4 日起这些购票规则变了-机票.CC",
        "head_desc_extra": "文中含春秋会员权益新旧对照表、双 11 促销航司一览、决策清单与六步净成本核算法。",
        "keywords": "春秋航空会员权益调整,双 11 机票促销,机票优惠活动,11 月机票什么时候买,航司会员折扣",
        "cat_label": "促销日历",
        "summary": "春秋会员权益 11 月 4 日调整，东航/厦航/春秋/深航/吉祥双 11 促销拉开——先搞清规则再下手。",
        "about_note": "本文为机票.CC「优惠活动」栏目的双 11 促销日历专题，文中促销信息整理自公开渠道并标注时间口径；"
                      "各航司活动场次、航线覆盖、退改规则可能随时调整，请以航司或平台活动页实时展示为准。"
                      "本站不销售机票、不参与任何交易环节。",
    },
    {
        "slug": "ticket-price-composition",
        "drafts": ["ticket-price-composition-2026-10-12.md"],
        "column": "guides.html",
        "column_name": "出行攻略",
        "date": "2026-10-12",
        "review": STAMP["next_review_price"],
        "scope": "规则与数据",
        "title_fallback": "一张机票的总价由什么构成",
        "meta_title": "一张机票的总价由什么构成：基础票价、机建、燃油费之外还有什么-机票.CC",
        "head_desc_extra": "文中含机票总价构成表、不同舱位费用对比示例、隐藏成本核算法与下单前六步核对清单及 FAQ。",
        "keywords": "机票总价构成,机建燃油费怎么算,机票票价组成,低价机票行李额,含税总价",
        "cat_label": "价格解读",
        "summary": "基础票价 + 机建 + 燃油 + 可选服务：四件套拆完，才知道省在哪、贵在哪。",
        "about_note": "本文为机票.CC「出行攻略」栏目的总价构成解读，文中价格与收费标准均整理自公开渠道并标注口径，"
                      "实时变动，请以航空公司官方渠道与出票页面展示为准。本站不销售机票、不参与任何交易环节。",
    },
    {
        "slug": "hainan-routes-october",
        "drafts": ["hainan-routes-october-2026-10-12.md"],
        "column": "routes.html",
        "column_name": "航线资讯",
        "date": "2026-10-12",
        "review": STAMP["next_review_rule"],
        "scope": "动态与规则",
        "title_fallback": "三亚、博鳌航线密集上新",
        "meta_title": "三亚、博鳌航线密集上新：10月海南进出港航班变化与购票参考-机票.CC",
        "head_desc_extra": "文中含三亚国际复航航线时刻表、博鳌机场新航季航线一览与新开航线购票核对清单及 FAQ。",
        "keywords": "三亚国际航线复航,博鳌机场新航线,海南机票,三亚吉隆坡航线,第五航权航线",
        "cat_label": "航线动态",
        "summary": "三亚国际线复航提速、博鳌冬春航季批量上新：海南进出港的班期时刻怎么用。",
        "about_note": "本文为机票.CC「航线资讯」栏目的海南航线动态专题，文中航线、班期与时刻信息整理自官方与媒体公开渠道，"
                      "以各航司与机场最终执行的航班计划为准。本站不销售机票、不参与任何交易环节。",
    },
    {
        "slug": "red-eye-early-flights",
        "drafts": ["red-eye-early-flights-2026-10-12.md"],
        "column": "guides.html",
        "column_name": "出行攻略",
        "date": "2026-10-12",
        "review": STAMP["next_review_rule"],
        "scope": "规则与攻略",
        "title_fallback": "红眼航班与早晚班机怎么选",
        "meta_title": "红眼航班与早晚班机怎么选：时刻、价格与接驳的取舍清单-机票.CC",
        "head_desc_extra": "文中含四档时刻得失对照表、隐藏成本核算法与买早晚班机前六步核对清单及 FAQ。",
        "keywords": "红眼航班,早晚班机怎么选,红眼航班便宜吗,早班机赶不上,航班时刻选择",
        "cat_label": "时刻选择",
        "summary": "省下的票价里有一部分会转嫁到接驳、酒店与精力上——四档时刻得失一次算清。",
        "about_note": "本文为机票.CC「出行攻略」栏目的时刻选择专题，文中价格倾向与时段划分为公开信息整理的经验参考，"
                      "具体以各航司实时价格与时刻为准。本站不销售机票、不参与任何交易环节。",
    },
    {
        "slug": "airline-updates-oct-12",
        "drafts": ["airline-updates-oct-12-2026-10-12.md"],
        "column": "airlines.html",
        "column_name": "航司动态",
        "date": "2026-10-12",
        "review": STAMP["next_review_rule"],
        "scope": "动态与规则",
        "title_fallback": "10月中旬航司新动作",
        "meta_title": "北京大兴直飞天水、青岛-温哥华复航：10月中旬航司新动作与购票参考-机票.CC",
        "head_desc_extra": "文中含 10 月中旬航司新开与复航航线一览、新航线首发期购买思路与核对清单及 FAQ。",
        "keywords": "北京大兴天水直飞,青岛温哥华航线,新航线开通,航司新航线怎么买,冬春航季新航线",
        "cat_label": "新开航线",
        "summary": "大兴-天水直飞、青岛-温哥华复航、柳州澜沧上新：首发期的购票思路与核对清单。",
        "about_note": "本文为机票.CC「航司动态」栏目的新航线动态专题，文中航线与班期信息整理自航司及媒体公开渠道，"
                      "以各航司最终执行的航班计划为准。本站不销售机票、不参与任何交易环节。",
    },
    {
        "slug": "budget-fare-true-total",
        "drafts": ["budget-fare-true-total-2026-10-13.md"],
        "column": "guides.html",
        "column_name": "出行攻略",
        "date": "2026-10-13",
        "review": STAMP["next_review_price"],
        "scope": "数据",
        "title_fallback": "两百多元的机票最后要付多少",
        "meta_title": "两百多元的机票最后要付多少：燃油附加费上调后的捡漏总价账-机票.CC",
        "head_desc_extra": "文中含节后低价航线样本表、机建与燃油附加费两档标准、三档含税总价算账示例与下单前隐性成本清单及 FAQ。",
        "keywords": "两百多元机票,机票含税总价,燃油附加费标准,节后特价机票,捡漏机票怎么算",
        "cat_label": "含税总价",
        "summary": "裸票价之外再加 100–140 元税费：机建与燃油两档标准、三笔总价账与隐性成本一次算清。",
        "about_note": "本文为机票.CC「出行攻略」栏目的含税总价专题，文中价格为公开报道样本整理的参考区间并标注口径，"
                      "实时变动，请以航空公司官方渠道与支付页面实时展示为准。本站不销售机票、不参与任何交易环节。",
    },
    {
        "slug": "new-international-routes-mid-oct",
        "drafts": ["new-international-routes-mid-oct-2026-10-13.md"],
        "column": "routes.html",
        "column_name": "航线资讯",
        "date": "2026-10-13",
        "review": STAMP["next_review_rule"],
        "scope": "动态与规则",
        "title_fallback": "近期国际航线上新怎么买",
        "meta_title": "广州直飞亚的斯亚贝巴开航、宁波复航普吉岛：近期国际航线上新怎么买-机票.CC",
        "head_desc_extra": "文中含三条新开复航国际航线的班期时刻表、逐条购票要点与新航线首发期四步购票法及 FAQ。",
        "keywords": "广州亚的斯亚贝巴航线,宁波普吉岛复航,国际新航线怎么买,新航线开航优惠,冬春航季国际航线",
        "cat_label": "国际航线",
        "summary": "亚的斯亚贝巴开航、普吉岛复航、河内—杭州恢复：班期时刻与首发期购票要点。",
        "about_note": "本文为机票.CC「航线资讯」栏目的国际航线动态专题，文中航线、班期与时刻信息整理自航司公告与媒体公开渠道，"
                      "以各航司最终执行的航班计划为准。本站不销售机票、不参与任何交易环节。",
    },
    {
        "slug": "autumn-break-family-booking",
        "drafts": ["autumn-break-family-booking-2026-10-13.md"],
        "column": "guides.html",
        "column_name": "出行攻略",
        "date": "2026-10-13",
        "review": STAMP["next_review_rule"],
        "scope": "规则与攻略",
        "title_fallback": "秋假家庭出游机票怎么买",
        "meta_title": "秋假家庭出游机票怎么买：远期预订量增长四成后的锁票与退改策略-机票.CC",
        "head_desc_extra": "文中含当前窗口三组数据对比、儿童婴儿票价税费表、按行程确定度分档的锁票策略与退改核对清单及 FAQ。",
        "keywords": "秋假机票怎么买,家庭出游机票,儿童机票价格,机票退改规则,远期机票预订",
        "cat_label": "家庭出行",
        "summary": "远期预订量涨四成：按行程确定度分三档锁票，先用舱位差价对冲改期成本。",
        "about_note": "本文为机票.CC「出行攻略」栏目的家庭购票专题，文中数据为公开报道监测口径、票价规则为通行做法整理，"
                      "具体以各航司规则与出票页面展示为准。本站不销售机票、不参与任何交易环节。",
    },
    {
        "slug": "airlines-winter-season-prep",
        "drafts": ["airlines-winter-season-prep-2026-10-13.md"],
        "column": "airlines.html",
        "column_name": "航司动态",
        "date": "2026-10-13",
        "review": STAMP["next_review_rule"],
        "scope": "动态与规则",
        "title_fallback": "冬春航季倒计时：航线与产品调整盘点",
        "meta_title": "冬春航季倒计时：乌鲁木齐航空航线新增复航与航司产品上新盘点-机票.CC",
        "head_desc_extra": "文中含换季机制三影响、乌鲁木齐航空 42 条航线布局观察、航司差异化产品选购要点与跨换季购票核对清单及 FAQ。",
        "keywords": "冬春航季换季,乌鲁木齐航空冬航季,航司产品上新,换季机票怎么买,分人群特惠票",
        "cat_label": "换季前瞻",
        "summary": "10 月 25 日换季前一周：航线新增复航、产品上新与跨换季购票的六步核对清单。",
        "about_note": "本文为机票.CC「航司动态」栏目的换季前瞻专题，文中航线计划与产品信息整理自航司公告及媒体公开渠道，"
                      "以各航司最终执行的航班计划与官方公示为准。本站不销售机票、不参与任何交易环节。",
    },
    {
        "slug": "capital-airlines-transit-perks",
        "drafts": ["capital-airlines-transit-perks-2026-10-14.md"],
        "column": "deals.html",
        "column_name": "优惠活动",
        "date": "2026-10-14",
        "review": STAMP["next_review_rule"],
        "scope": "权益与规则",
        "title_fallback": "国际中转免费住宿与空铁联运补贴怎么用",
        "meta_title": "国际中转免费住宿与空铁联运补贴：冬春航季中转权益怎么用-机票.CC",
        "head_desc_extra": "文中含三类中转权益适用条件表、联程票与分开购票对比、权益使用五步清单与 FAQ。",
        "keywords": "国际中转免费住宿,空铁联运补贴,机票中转权益,国际联程客票,冬春航季新航线",
        "cat_label": "中转权益",
        "summary": "免费住宿一晚、火车票最高报销 400 元：中转权益的适用条件与操作要点。",
        "about_note": "本文为机票.CC「优惠活动」栏目的中转权益专题，文中权益均为航司公告与媒体公开报道口径，"
                      "不同航线、舱位适用条件不同且可能随航季调整，请以各航司官网、官方客服与出票页面实时展示为准。"
                      "本站不销售机票、不参与任何交易环节。",
    },
    {
        "slug": "chengdu-tianfu-winter-new-routes",
        "drafts": ["chengdu-tianfu-winter-new-routes-2026-10-14.md"],
        "column": "routes.html",
        "column_name": "航线资讯",
        "date": "2026-10-14",
        "review": STAMP["next_review_rule"],
        "scope": "动态与规则",
        "title_fallback": "成都天府冬春航季上新怎么买",
        "meta_title": "成都天府冬春航季上新：喀什阿勒泰直飞、柳州邢台新航线怎么买-机票.CC",
        "head_desc_extra": "文中含新开国内航线班期时刻表、国际方向加密解读、新航线首发期四个判断维度与购票核对清单及 FAQ。",
        "keywords": "成都天府新航线,成都飞喀什,成都飞阿勒泰,冬春航季新航线,新航线怎么买",
        "cat_label": "新开航线",
        "summary": "喀什每周三班、阿勒泰天天直飞、伊斯坦布尔天天班：新航线班期时刻与首发期购票法。",
        "about_note": "本文为机票.CC「航线资讯」栏目的新开航线专题，文中航线、班期与时刻信息整理自航司公告及媒体公开渠道，"
                      "以各航司最终执行的航班计划为准。本站不销售机票、不参与任何交易环节。",
    },
    {
        "slug": "canton-fair-flights-guide",
        "drafts": ["canton-fair-flights-guide-2026-10-14.md"],
        "column": "guides.html",
        "column_name": "出行攻略",
        "date": "2026-10-14",
        "review": STAMP["next_review_rule"],
        "scope": "攻略与规则",
        "title_fallback": "广交会期间飞广州怎么买票",
        "meta_title": "广交会期间飞广州怎么买票：商旅错峰、备选机场与通关提速要点-机票.CC",
        "head_desc_extra": "文中含展会期客流结构表、备选机场方案对比、白云机场保障措施盘点与购票核对清单及 FAQ。",
        "keywords": "广交会机票,广交会期间飞广州,展会商旅购票,白云机场广交会,备选机场高铁方案",
        "cat_label": "商旅出行",
        "summary": "10 月 15 日开幕后二十来天：客流高峰结构、错峰买法、备选机场与机场保障一次理清。",
        "about_note": "本文为机票.CC「出行攻略」栏目的展会商旅专题，文中保障措施为机场与媒体公开报道口径，"
                      "可能动态调整，请以白云机场官方渠道实时发布为准。本站不销售机票、不参与任何交易环节。",
    },
    {
        "slug": "baiyun-three-intl-routes-oct",
        "drafts": ["baiyun-three-intl-routes-oct-2026-10-14.md"],
        "column": "airlines.html",
        "column_name": "航司动态",
        "date": "2026-10-14",
        "review": STAMP["next_review_rule"],
        "scope": "动态与规则",
        "title_fallback": "白云机场10月新开三条国际航线",
        "meta_title": "广州白云机场10月新开三条国际航线：班期时刻与购票要点-机票.CC",
        "head_desc_extra": "文中含三条新航线班期一览表、经停长沙的非洲航线时刻表、乘坐新开国际航线核对清单与 FAQ。",
        "keywords": "白云机场新航线,广州雅加达航线,海参崴广州航线,广交会国际航线,新航线购票要点",
        "cat_label": "新开航线",
        "summary": "亚的斯亚贝巴、雅加达、海参崴三条新线的班期时刻与开航初期购票要点。",
        "about_note": "本文为机票.CC「航司动态」栏目的新开航线专题，文中航线、班期与时刻信息整理自新华社、广州日报等公开报道，"
                      "以各航司最终执行的航班计划与官方公示为准。本站不销售机票、不参与任何交易环节。",
    },
    {
        "slug": "flight-booking-tips",
        "drafts": ["flight-booking-tips-2026-10-15.md"],
        "column": "guides.html",
        "column_name": "出行攻略",
        "date": "2026-10-15",
        "review": STAMP["next_review_rule"],
        "scope": "规则与攻略",
        "title_fallback": "机票预订技巧",
        "meta_title": "机票预订技巧：从搜索到出票的 9 个关键动作（2026 实用版）-机票.CC",
        "head_desc_extra": "文中含预订全流程对照表、比价要素表、下单核对清单、常见错误对照与 6 条预订 FAQ。",
        "keywords": "机票预订技巧,机票怎么订,订机票流程,机票预订注意事项,机票出票后要做什么,机票比价看什么",
        "cat_label": "购票技巧",
        "summary": "从搜索、比价、下单到出票验票：9 个能直接照做的动作，避开大多数多花的钱。",
        "about_note": "本文为机票.CC「出行攻略」栏目的机票预订流程专题，文中流程与规则为通用科普整理，"
                      "不同航司与渠道存在差异，请以航空公司官方渠道及实际购票页面实时展示为准。"
                      "本站不销售机票、不参与任何交易环节。",
    },
    {
        "slug": "cheap-flights-how-to",
        "drafts": ["cheap-flights-how-to-2026-10-15.md"],
        "column": "guides.html",
        "column_name": "出行攻略",
        "date": "2026-10-15",
        "review": STAMP["next_review_rule"],
        "scope": "规则与攻略",
        "title_fallback": "特价机票怎么买",
        "meta_title": "特价机票怎么买才靠谱？低价舱、促销节奏与捡漏的正确姿势-机票.CC",
        "head_desc_extra": "文中含低价来源对照表、促销节点节奏表、6 个捡漏动作与隐性成本检查清单及 FAQ。",
        "keywords": "特价机票怎么买,特价机票,便宜机票怎么买,机票促销时间,机票捡漏技巧,低价机票靠谱吗",
        "cat_label": "特价票",
        "summary": "低价舱、促销与清仓三类来源怎么分辨，以及 6 个能做成习惯的捡漏动作。",
        "about_note": "本文为机票.CC「出行攻略」栏目的特价机票专题，文中价格为公开渠道整理的参考区间，"
                      "标注统计口径与时间范围；价格实时变动，请以航空公司官方渠道实时展示为准。"
                      "本站不销售机票、不参与任何交易环节。",
    },
    {
        "slug": "flight-booking-money-saving",
        "drafts": ["flight-booking-money-saving-2026-10-15.md"],
        "column": "guides.html",
        "column_name": "出行攻略",
        "date": "2026-10-15",
        "review": STAMP["next_review_rule"],
        "scope": "规则与攻略",
        "title_fallback": "机票省钱攻略",
        "meta_title": "机票省钱攻略：票价之外的 10 个能省环节与核对清单-机票.CC",
        "head_desc_extra": "文中含机票成本构成表、10 个省钱环节清单、伪省钱风险对照表与不同人群省钱重点。",
        "keywords": "机票省钱攻略,买机票怎么省钱,机票省钱技巧,机票附加费用,机票怎么买最划算,机票行李费怎么省",
        "cat_label": "省钱攻略",
        "summary": "把一张票的总成本拆开，逐项优化，通常比单纯比价更见效。",
        "about_note": "本文为机票.CC「出行攻略」栏目的机票省钱专题，文中成本分类与金额为说明结构的示意，"
                      "不构成报价；实际费用因航司、航线与舱位而异，请以官方渠道实时展示为准。"
                      "本站不销售机票、不参与任何交易环节。",
    },
    {
        "slug": "flight-booking-mistakes",
        "drafts": ["flight-booking-mistakes-2026-10-15.md"],
        "column": "guides.html",
        "column_name": "出行攻略",
        "date": "2026-10-15",
        "review": STAMP["next_review_rule"],
        "scope": "规则与攻略",
        "title_fallback": "订机票常见错误与避坑清单",
        "meta_title": "订机票最容易犯的 12 个错误：从姓名拼写到证件有效期-机票.CC",
        "head_desc_extra": "文中含三环节错误对照表、问题处理紧迫度表、逐项核对清单与出错后处理路径及 FAQ。",
        "keywords": "机票预订注意事项,订机票避坑,机票姓名拼错怎么办,重复购票怎么办,机票退改签陷阱,机票核对清单",
        "cat_label": "避坑指南",
        "summary": "姓名、证件、重复下单、退改规则——12 个高频错误与一份能挡掉它们的核对清单。",
        "about_note": "本文为机票.CC「出行攻略」栏目的订票避坑专题，文中规则与提示为公开信息归纳，"
                      "能否处理与处理结果取决于航司规则和票种，请以航空公司官方答复为准。"
                      "本站不销售机票、不参与任何交易环节。",
    },
    {
        "slug": "round-trip-vs-oneway",
        "drafts": ["round-trip-vs-oneway-2026-10-15.md"],
        "column": "guides.html",
        "column_name": "出行攻略",
        "date": "2026-10-15",
        "review": STAMP["next_review_rule"],
        "scope": "规则与攻略",
        "title_fallback": "往返票还是单程票",
        "meta_title": "往返票还是单程票？多段组合购票的决策方法与场景对照-机票.CC",
        "head_desc_extra": "文中含四种票型对照表、场景决策速查表、中转保障差异说明与组合购票核对清单及 FAQ。",
        "keywords": "往返票还是单程票,往返票和单程票哪个便宜,开口票是什么,联程票和分段买区别,机票组合购票,中转机票行李直挂",
        "cat_label": "购票技巧",
        "summary": "单程、往返、开口、联程四种票型怎么选，以及中转时该选联程还是分段买。",
        "about_note": "本文为机票.CC「出行攻略」栏目的票型选择专题，文中票型与规则为通用科普整理，"
                      "是否提供对应票型及具体价格需按航线查询，请以航空公司官方渠道实时展示为准。"
                      "本站不销售机票、不参与任何交易环节。",
    },
    {
        "slug": "haikou-malaysia-routes",
        "drafts": ["haikou-malaysia-routes-2026-10-16.md"],
        "column": "routes.html",
        "column_name": "航线资讯",
        "date": "2026-10-16",
        "review": STAMP["next_review_rule"],
        "scope": "航线与动态",
        "title_fallback": "海口往返马来西亚航线加密至一周19班",
        "meta_title": "海口往返马来西亚航线加密至一周19班：古晋槟城复航后的购票要点-机票.CC",
        "head_desc_extra": "文中含复航航线班期时刻表、四航点行程定位表、三种购票思路对照表与下单前核对清单及 FAQ。",
        "keywords": "海口飞马来西亚,海口古晋航线,海口槟城航线,九元航空海口,东南亚机票怎么买,马来西亚航线复航",
        "cat_label": "国际航线",
        "summary": "古晋槟城复航后海口联通马来西亚增至4城：班期、时刻与购票思路拆解。",
        "about_note": "本文为机票.CC「航线资讯」栏目的东南亚航线专题，文中航线、班期与时刻信息整理自公开渠道，"
                      "以航空公司最终执行的航班计划为准。本站不销售机票、不参与任何交易环节。",
    },
    {
        "slug": "shandong-airlines-winter-31",
        "drafts": ["shandong-airlines-winter-31-2026-10-16.md"],
        "column": "airlines.html",
        "column_name": "航司动态",
        "date": "2026-10-16",
        "review": STAMP["next_review_rule"],
        "scope": "航线与动态",
        "title_fallback": "山航冬春航季新增加密31条航线",
        "meta_title": "山航冬春航季新增加密31条航线：济青中转升级后的购票要点-机票.CC",
        "head_desc_extra": "文中含航线方向分类表、典型出行场景对照表、换季前后购票时间点表与核对清单及 FAQ。",
        "keywords": "山航冬春航季,山东航空新航线,济南青岛中转,10月25日换季,航线加密,首尔航线加密",
        "cat_label": "航季换季",
        "summary": "31条新增加密航线怎么用：直飞替代、通程中转与换季购票节奏。",
        "about_note": "本文为机票.CC「航司动态」栏目的换季运力专题，文中航线与中转权益信息整理自公开渠道，"
                      "以山东航空官方渠道发布的最终航班计划为准。本站不销售机票、不参与任何交易环节。",
    },
    {
        "slug": "season-change-ticket-guide",
        "drafts": ["season-change-ticket-guide-2026-10-16.md"],
        "column": "guides.html",
        "column_name": "出行攻略",
        "date": "2026-10-16",
        "review": STAMP["next_review_rule"],
        "scope": "规则与攻略",
        "title_fallback": "换季日已出票旅客怎么应对航班时刻变更",
        "meta_title": "10月25日换季日临近：已出票旅客怎么应对航班时刻变更-机票.CC",
        "head_desc_extra": "文中含换季变更类型表、订单风险分级方法、三个核对节点清单与变更处理流程及 FAQ。",
        "keywords": "航班换季时刻变更,航班取消改签,换季机票怎么办,航班时刻变更退票,已出票航班调整",
        "cat_label": "退改指南",
        "summary": "换季变更三类情形、三个核对节点与一套完整的改签退票决策流程。",
        "about_note": "本文为机票.CC「出行攻略」栏目的换季应对专题，文中方法为公开信息归纳整理，"
                      "具体办理标准取决于各航司规则与票种，请以航空公司官方答复为准。"
                      "本站不销售机票、不参与任何交易环节。",
    },
    {
        "slug": "southeast-asia-nov-fares",
        "drafts": ["southeast-asia-nov-fares-2026-10-16.md"],
        "column": "deals.html",
        "column_name": "优惠活动",
        "date": "2026-10-16",
        "review": STAMP["next_review_price"],
        "scope": "数据与活动",
        "title_fallback": "11月错峰东南亚价格窗口解读",
        "meta_title": "11月错峰东南亚：航线密集复航后的价格窗口与优惠解读-机票.CC",
        "head_desc_extra": "文中含错峰供需时段表、三类人群购票策略表、促销核对清单与总成本核算思路及 FAQ。",
        "keywords": "11月机票便宜吗,东南亚机票错峰,复航航线促销,双11机票优惠,东南亚淡季机票,错峰出行攻略",
        "cat_label": "错峰出行",
        "summary": "供给增量遇上需求淡季：识别11月东南亚价格窗口的方法与优惠核对清单。",
        "about_note": "本文为机票.CC「优惠活动」栏目的错峰专题，文中价格表现均为定性规律描述，"
                      "票价实时变动，促销规则以各航司官方渠道发布为准。本站不销售机票、不参与任何交易环节。",
    },
    {
        "slug": "new-routes-before-winter-season",
        "drafts": ["new-routes-before-winter-season-2026-10-17.md"],
        "column": "routes.html",
        "column_name": "航线资讯",
        "date": "2026-10-17",
        "review": STAMP["next_review_rule"],
        "scope": "航线与动态",
        "title_fallback": "换季前一周新航线密集官宣怎么买",
        "meta_title": "换季前一周新航线密集官宣：南宁盐城、合肥揭阳、郑州喀什直飞怎么买-机票.CC",
        "head_desc_extra": "文中含本轮官宣航线班期时刻表、购票时间点表、经停串联行程适配表与核对清单及 FAQ。",
        "keywords": "南宁盐城航线,合肥揭阳航线,郑州喀什直飞,冬春航季新航线,新航线怎么买,换季新航线",
        "cat_label": "新航线上新",
        "summary": "南宁—盐城、合肥—揭阳、郑州—喀什直飞三案例拆解：班期时刻、购票时间点与班期衔接。",
        "about_note": "本文为机票.CC「航线资讯」栏目的换季新航线专题，文中班期与时刻均整理自航司及地方政府"
                      "公开通稿，属计划安排，以航司官方销售系统为准。本站不销售机票、不参与任何交易环节。",
    },
    {
        "slug": "chongqing-airlines-winter-renewal",
        "drafts": ["chongqing-airlines-winter-renewal-2026-10-17.md"],
        "column": "airlines.html",
        "column_name": "航司动态",
        "date": "2026-10-17",
        "review": STAMP["next_review_rule"],
        "scope": "航线与动态",
        "title_fallback": "重庆航空冬春航季焕新62条航线",
        "meta_title": "重庆航空冬春航季焕新62条航线：新开重庆至三明等航线后的购票要点-机票.CC",
        "head_desc_extra": "文中含航线指标解读表、新开航线形态表、新航点接驳表与换季核对清单及 FAQ。",
        "keywords": "重庆航空冬春航季,重庆至三明航线,重庆到芒市复航,经停串联航线,换季购票,重庆航空新航线",
        "cat_label": "航季换季",
        "summary": "62条航线53城的新开、恢复、加密三类调整拆解，附新航点落地接驳思路。",
        "about_note": "本文为机票.CC「航司动态」栏目的换季运力专题，文中航线与班期信息整理自公开报道，"
                      "以重庆航空官方渠道发布的最终航班计划为准。本站不销售机票、不参与任何交易环节。",
    },
    {
        "slug": "ice-snow-warm-winter-booking",
        "drafts": ["ice-snow-warm-winter-booking-2026-10-17.md"],
        "column": "guides.html",
        "column_name": "出行攻略",
        "date": "2026-10-17",
        "review": STAMP["next_review_price"],
        "scope": "规则与攻略",
        "title_fallback": "冰雪游避寒游航班加密后的购票攻略",
        "meta_title": "冰雪游避寒游航班加密：乌鲁木齐哈尔滨三亚航线怎么买更划算-机票.CC",
        "head_desc_extra": "文中含运力增投方向表、冰雪游出行窗口表、避寒方案对比表与决策清单及 FAQ。",
        "keywords": "乌鲁木齐机票,哈尔滨机票什么时候买,三亚机票攻略,避寒游航线,冰雪游航班,冬春航季运力",
        "cat_label": "购票时机",
        "summary": "运力增量方向拆解：冰雪游与避寒游两类目的地的窗口、方案与提前量决策。",
        "about_note": "本文为机票.CC「出行攻略」栏目的冬春出行专题，运力数据为公开报道的计划航班量口径，"
                      "票价实时变动，时段与窗口为定性归纳。本站不销售机票、不参与任何交易环节。",
    },
    {
        "slug": "eastair-air-rail-booking-deal",
        "drafts": ["eastair-air-rail-booking-deal-2026-10-17.md"],
        "column": "deals.html",
        "column_name": "优惠活动",
        "date": "2026-10-17",
        "review": STAMP["next_review_price"],
        "scope": "数据与活动",
        "title_fallback": "东航空铁联订规则与使用要点",
        "meta_title": "东航空铁联订怎么用：机票火车票一次下单，联订惠价规则与使用要点-机票.CC",
        "head_desc_extra": "文中含联订与分段购票对比表、国内国际场景表、适用人群清单与使用核对要点及 FAQ。",
        "keywords": "空铁联订,空铁联运,东航联订惠价,机票火车票一起买,中转联运产品,空铁组合出行",
        "cat_label": "联运优惠",
        "summary": "一次下单买机票和火车票：联订惠价规则、适用场景与分段购票的对比决策。",
        "about_note": "本文为机票.CC「优惠活动」栏目的联运产品专题，产品规则与覆盖数据整理自公开报道，"
                      "减免幅度为官方公布规则上限，以航司官方渠道实时显示为准。本站不销售机票、不参与任何交易环节。",
    },
    {
        "slug": "hochiminh-shanghai-daily-flight",
        "drafts": ["hochiminh-shanghai-daily-flight-2026-10-18.md"],
        "column": "routes.html",
        "column_name": "航线资讯",
        "date": "2026-10-18",
        "review": STAMP["next_review_rule"],
        "scope": "航线与动态",
        "title_fallback": "上海直飞胡志明市每日一班怎么买",
        "meta_title": "上海直飞胡志明市开航：每日一班时刻表与购票要点-机票.CC",
        "head_desc_extra": "文中含航线信息表、促销核对表、换季时间点表、红眼时刻适配分析、下单核对清单与 FAQ。",
        "keywords": "上海直飞胡志明市,胡志明市机票,上海浦东胡志明航线,越南航线,新航线开航,国际直飞怎么买",
        "cat_label": "国际航线上新",
        "summary": "每日直飞新航线拆解：班期时刻、开航促销口径与红眼时刻的适配判断。",
        "about_note": "本文为机票.CC「航线资讯」栏目的国际航线上新专题，航线班期、时刻与促销规则整理自"
                      "中国民航网公开报道，以航司官方销售系统为准。本站不销售机票、不参与任何交易环节。",
    },
    {
        "slug": "xian-zhanjiang-direct-flight",
        "drafts": ["xian-zhanjiang-direct-flight-2026-10-18.md"],
        "column": "airlines.html",
        "column_name": "航司动态",
        "date": "2026-10-18",
        "review": STAMP["next_review_rule"],
        "scope": "航线与动态",
        "title_fallback": "东航新开西安至湛江直飞航线购票要点",
        "meta_title": "东航新开西安至湛江直飞航线：10月25日起每日一班，购票要点-机票.CC",
        "head_desc_extra": "文中含去返程时刻表、三个使用场景、购票四要点表、换季窗口建议与下单核对清单及 FAQ。",
        "keywords": "西安到湛江机票,湛江吴川机场,东航新航线,西安湛江直飞,冬春航季新航线,避寒游机票",
        "cat_label": "航季换季",
        "summary": "10月25日起每日一班：时刻形态、避寒与中转三个场景、新航线购票要点与时间窗。",
        "about_note": "本文为机票.CC「航司动态」栏目的换季新航线专题，航班号、班期与时刻整理自西安日报"
                      "公开报道，以东方航空官方渠道为准。本站不销售机票、不参与任何交易环节。",
    },
    {
        "slug": "stopover-vs-direct-flight",
        "drafts": ["stopover-vs-direct-flight-2026-10-18.md"],
        "column": "guides.html",
        "column_name": "出行攻略",
        "date": "2026-10-18",
        "review": STAMP["next_review_rule"],
        "scope": "规则与攻略",
        "title_fallback": "经停航班怎么买值不值",
        "meta_title": "经停航班怎么买：换季新开的经停航线，比直飞慢多久、值不值-机票.CC",
        "head_desc_extra": "文中含直飞经停中转对比表、场景选择表、时刻表解读三细节、下单核对清单与 FAQ。",
        "keywords": "经停航班,经停和直飞区别,经停要下飞机吗,经停航班行李,换季经停航线,经停和中转",
        "cat_label": "购票技巧",
        "summary": "经停航班的运行逻辑与判断框架：覆盖、价格、行李三个维度决定值不值。",
        "about_note": "本文为机票.CC「出行攻略」栏目的购票知识专题，文中航线案例整理自航司及地方媒体"
                      "公开报道，班期时刻以航司官方渠道为准。本站不销售机票、不参与任何交易环节。",
    },
    {
        "slug": "member-day-calendar-oct",
        "drafts": ["member-day-calendar-oct-2026-10-18.md"],
        "column": "deals.html",
        "column_name": "优惠活动",
        "date": "2026-10-18",
        "review": STAMP["next_review_price"],
        "scope": "数据与活动",
        "title_fallback": "航司会员日日历与开航特惠核对方法",
        "meta_title": "航司会员日怎么用：换季前后的优惠日历与核对方法-机票.CC",
        "head_desc_extra": "文中含会员日日历表、近期开航特惠口径表、优惠叠加顺序、抢票实务要点与 FAQ。",
        "keywords": "航司会员日,东航会员日,南航会员日,开航特惠,机票优惠叠加,换季促销",
        "cat_label": "会员日",
        "summary": "会员日日历与三组开航特惠口径：叠加顺序、实务要点与下单核对方法。",
        "about_note": "本文为机票.CC「优惠活动」栏目的会员日专题，会员日日期与促销口径整理自公开报道，"
                      "「起价」均为官方公布促销起点价，数量有限、实时变动，以各航司官方渠道为准。"
                      "本站不销售机票、不参与任何交易环节。",
    },
    {
        "slug": "chengdu-altay-three-daily",
        "drafts": ["chengdu-altay-three-daily-2026-10-19.md"],
        "column": "routes.html",
        "column_name": "航线资讯",
        "date": "2026-10-19",
        "review": STAMP["next_review_price"],
        "scope": "航线与票价",
        "title_fallback": "成都直飞阿勒泰航线加密后的购票要点",
        "meta_title": "成都直飞阿勒泰航线加密：换季后最多一天三班，购票要点全梳理-机票.CC",
        "head_desc_extra": "文中含三家承运方航线结构表、票价口径说明、班次密度分析、下单核对清单与 FAQ。",
        "keywords": "成都直飞阿勒泰,阿勒泰机票,冬春航季新航线,直飞阿勒泰航班,阿勒泰雪季购票,换季航线加密",
        "cat_label": "新航线",
        "summary": "换季后成都最多一天三班直飞阿勒泰：航线结构、票价区间口径与下单核对要点。",
        "about_note": "本文为机票.CC「航线资讯」栏目的换季新航线专题，航线与票价信息整理自公开报道，"
                      "票价为查询时点样本区间、不含税费、实时变动，以航司官方渠道为准。"
                      "本站不销售机票、不参与任何交易环节。",
    },
    {
        "slug": "hefei-winter-new-routes",
        "drafts": ["hefei-winter-new-routes-2026-10-19.md"],
        "column": "airlines.html",
        "column_name": "航司动态",
        "date": "2026-10-19",
        "review": STAMP["next_review_rule"],
        "scope": "航司与航线",
        "title_fallback": "合肥新桥机场冬春航季新航线梳理",
        "meta_title": "合肥新桥机场冬春航季上新：东航新开运城惠州柳州、海航揭阳直飞购票要点-机票.CC",
        "head_desc_extra": "文中含东航安徽航线变化表、合肥—揭阳时刻表、购票要点与截载时间提醒、FAQ。",
        "keywords": "合肥新桥机场,冬春航季新航线,东航合肥航线,海航合肥揭阳,合肥直飞,换季航班计划",
        "cat_label": "航司动态",
        "summary": "东航安徽5机场47条航线的新增与加密、海航合肥—揭阳每日班时刻与购票要点。",
        "about_note": "本文为机票.CC「航司动态」栏目的换季航司盘点专题，班期与时刻整理自公开报道的新航季计划，"
                      "可能动态调整，以航司官方销售系统实时显示为准。"
                      "本站不销售机票、不参与任何交易环节。",
    },
    {
        "slug": "checkin-cutoff-time-change",
        "drafts": ["checkin-cutoff-time-change-2026-10-19.md"],
        "column": "guides.html",
        "column_name": "出行攻略",
        "date": "2026-10-19",
        "review": STAMP["next_review_rule"],
        "scope": "乘机规则",
        "title_fallback": "航班截载时间变化与晚到旅客应对方法",
        "meta_title": "航班截载时间怎么看：咸阳改25分钟、晚到旅客怎么办-机票.CC",
        "head_desc_extra": "文中含截载/登机口/起飞三概念对照表、晚到自救清单、误机处理路径与 FAQ。",
        "keywords": "航班截载时间,值机截止时间,西安咸阳机场值机,晚到旅客,误机怎么办,登机口关闭时间",
        "cat_label": "乘机攻略",
        "summary": "截载时间因机场航司而异且正在变化：三概念对照、自救清单与误机处理路径。",
        "about_note": "本文为机票.CC「出行攻略」栏目的乘机规则专题，截载时间信息整理自公开报道，"
                      "因机场、航司与航班类型而异且可能调整，出行前以官方公示为准。"
                      "本站不销售机票、不参与任何交易环节。",
    },
    {
        "slug": "airport-promo-fares-guide",
        "drafts": ["airport-promo-fares-guide-2026-10-19.md"],
        "column": "deals.html",
        "column_name": "优惠活动",
        "date": "2026-10-19",
        "review": STAMP["next_review_price"],
        "scope": "促销与规则",
        "title_fallback": "换季机场特价航线的解读与核对方法",
        "meta_title": "换季机场促销怎么看：特价航线样本解读与下单核对清单-机票.CC",
        "head_desc_extra": "文中含机场公告与航司活动对照表、特价航线样本数据、隐藏成本三笔账、六步核对清单与 FAQ。",
        "keywords": "机场特价机票,换季促销,特价航线,起价什么意思,特价票退改,新航线优惠",
        "cat_label": "促销解读",
        "summary": "机场换季特价公告的读法：两类促销来源、起价口径、隐藏成本与下单核对清单。",
        "about_note": "本文为机票.CC「优惠活动」栏目的促销解读专题，特价口径整理自机场公告等公开渠道，"
                      "「起价」均为公布价格下限，不含税费、数量有限、实时变动，以航司官方渠道为准。"
                      "本站不销售机票、不参与任何交易环节。",
    },
    {
        "slug": "spring-festival-flight-booking-2027",
        "drafts": ["spring-festival-flight-booking-2027-2026-10-20.md"],
        "column": "guides.html",
        "column_name": "出行攻略",
        "date": "2026-10-20",
        "review": STAMP["next_review_rule"],
        "scope": "购票策略",
        "title_fallback": "2027春运机票什么时候买",
        "meta_title": "2027春运机票什么时候买：春节2月6日，三个预订窗口与锁票策略-机票.CC",
        "head_desc_extra": "文中含2027春运关键日期表、U型价格曲线三窗口对照、高峰日替代日对照表、六步核对清单与 FAQ。",
        "keywords": "2027春运机票,春运机票什么时候买,春节机票预订,2027春节是哪天,春运抢票,春节机票价格规律",
        "cat_label": "节假日购票",
        "summary": "2027春节2月6日：U型价格曲线下三个预订窗口、高峰日替代日对照与锁票清单。",
        "about_note": "本文为机票.CC「出行攻略」栏目的春运购票专题，春节日期为公开历法信息，"
                      "放假与春运安排以有关部门公布为准；文中规律整理自历年公开报道，价格实时变动，以官方渠道为准。"
                      "本站不销售机票、不参与任何交易环节。",
    },
    {
        "slug": "spring-airlines-intl-winter-2026",
        "drafts": ["spring-airlines-intl-winter-2026-2026-10-20.md"],
        "column": "routes.html",
        "column_name": "航线资讯",
        "date": "2026-10-20",
        "review": STAMP["next_review_rule"],
        "scope": "航线与班期",
        "title_fallback": "春秋航空冬春航季国际线加密",
        "meta_title": "春秋航空冬春航季国际线加密：济州曼谷天天班与12月新航线购票要点-机票.CC",
        "head_desc_extra": "文中含换季后国际班期结构表、12月新开航线时点表、出港点比价对照与三步核对清单、FAQ。",
        "keywords": "春秋航空国际航线,冬春航季国际航班,济州天天班,曼谷直飞,石家庄飞济州,12月新开航线,普吉槟城直飞",
        "cat_label": "国际航线",
        "summary": "换季后济州曼谷胡志明转天天班、12月槟城普吉新线开航与石家庄出港起价的读法。",
        "about_note": "本文为机票.CC「航线资讯」栏目的国际航线换季专题，班期与开航日期整理自公开报道的新航季计划，"
                      "可能动态调整，以航司官方销售系统实时查询为准；「起价」不含税、数量有限。"
                      "本站不销售机票、不参与任何交易环节。",
    },
    {
        "slug": "tianjin-air-winter-season-2026",
        "drafts": ["tianjin-air-winter-season-2026-2026-10-20.md"],
        "column": "airlines.html",
        "column_name": "航司动态",
        "date": "2026-10-20",
        "review": STAMP["next_review_rule"],
        "scope": "航司与航线",
        "title_fallback": "天津航空冬春航季新开恢复加密59条航线",
        "meta_title": "天津航空冬春航季新开恢复加密59条航线：通航点扩至115个后的购票要点-机票.CC",
        "head_desc_extra": "文中含59条航线变化总表、出行场景核对表、换季购票时间节奏与四步核对清单、FAQ。",
        "keywords": "天津航空冬春航季,天津航空新航线,安阳丹东通航,天津直飞,支线航线购票,换季航班计划,避寒航线",
        "cat_label": "航司动态",
        "summary": "新开安阳丹东、重开8城、210余条航线115个通航点：航线结构变化与购票核对要点。",
        "about_note": "本文为机票.CC「航司动态」栏目的换季航司盘点专题，航线与通航点信息源自中国民航网2026年10月19日报道，"
                      "以航司官方销售系统实时查询为准。本站不销售机票、不参与任何交易环节。",
    },
    {
        "slug": "double11-flight-card-2026",
        "drafts": ["double11-flight-card-2026-2026-10-20.md"],
        "column": "deals.html",
        "column_name": "优惠活动",
        "date": "2026-10-20",
        "review": STAMP["next_review_price"],
        "scope": "促销与规则",
        "title_fallback": "双11机票次卡上新怎么用",
        "meta_title": "双11机票次卡上新怎么用：航司次卡、随心飞与红包返场的规则解读-机票.CC",
        "head_desc_extra": "文中含次卡品类结构表、两类出行者比价演算表、下单前后操作节奏与四条条款核对要点、FAQ。",
        "keywords": "双11机票次卡,机票次卡是什么,随心飞怎么买,双11机票优惠,次卡退改规则,机票券包",
        "cat_label": "促销解读",
        "summary": "次卡三段式权益与两个风险、什么人适合买、与会员日新航线促销怎么搭配比较。",
        "about_note": "本文为机票.CC「优惠活动」栏目的促销规则解读专题，品类与条款信息整理自公开报道，"
                      "各商品价格与规则以活动页实时展示为准，不含任何购买链接。"
                      "本站不销售机票、不参与任何交易环节。",
    },
    {
        "slug": "fuzhou-air-winter-new-routes",
        "drafts": ["fuzhou-air-winter-new-routes-2026-10-21.md"],
        "column": "routes.html",
        "column_name": "航线资讯",
        "date": "2026-10-21",
        "review": STAMP["next_review_rule"],
        "scope": "航线与班期",
        "title_fallback": "福州航空冬春航季新开六条航线",
        "meta_title": "福州航空冬春航季新开六条航线：福州直飞哈尔滨复航后怎么买票-机票.CC",
        "head_desc_extra": "文中含六条新开与重开航线结构表、经停与替代方案对照表、冰雪季购票时点判断与下单核对清单、FAQ。",
        "keywords": "福州航空新航线,福州直飞哈尔滨,冬春航季新航线,福州飞长春,经停航班,冰雪机票什么时候买,福州机票",
        "cat_label": "航线扩容",
        "summary": "六条新线打通福建至东北西北走廊、直飞哈尔滨复航与经停结构的读法。",
        "about_note": "本文为机票.CC「航线资讯」栏目的换季航线扩容专题，航线与加密方向整理自东南网2026年10月20日报道，"
                      "班期与时刻以航司官方销售系统实时查询为准。本站不销售机票、不参与任何交易环节。",
    },
    {
        "slug": "hunan-airlines-winter-11-routes",
        "drafts": ["hunan-airlines-winter-11-routes-2026-10-21.md"],
        "column": "airlines.html",
        "column_name": "航司动态",
        "date": "2026-10-21",
        "review": STAMP["next_review_rule"],
        "scope": "航司与航线",
        "title_fallback": "湖南航空冬航季新开11条航线",
        "meta_title": "湖南航空冬航季新开11条航线：长沙始发扩容后的购票要点-机票.CC",
        "head_desc_extra": "文中含11条新开航线场景表、冬游方向购票节奏表、初期票价窗口读法与四个核对动作、FAQ。",
        "keywords": "湖南航空新航线,长沙飞海口,长沙飞西双版纳,冬航季机票,新航线初期票价,客舱携宠,爱宠同行",
        "cat_label": "航司动态",
        "summary": "11条新线扩容长沙始发、换季初期价格窗口的读法与客舱携宠服务升级要点。",
        "about_note": "本文为机票.CC「航司动态」栏目的换季航司扩容专题，航线与服务信息整理自华声在线2026年10月20日报道，"
                      "以航司官方销售系统实时查询为准。本站不销售机票、不参与任何交易环节。",
    },
    {
        "slug": "pet-in-cabin-flight-booking",
        "drafts": ["pet-in-cabin-flight-booking-2026-10-21.md"],
        "column": "guides.html",
        "column_name": "出行攻略",
        "date": "2026-10-21",
        "review": STAMP["next_review_rule"],
        "scope": "规则与攻略",
        "title_fallback": "宠物能带上飞机吗",
        "meta_title": "宠物能带上飞机吗：客舱携宠服务的购票流程与核对清单-机票.CC",
        "head_desc_extra": "文中含客舱携宠与有氧托运对比表、五步申请流程、常见误区清单与携宠购票FAQ。",
        "keywords": "宠物能带上飞机吗,客舱携宠,宠物托运机票,带宠物坐飞机流程,宠物乘机证明,爱宠同行,宠物航空箱要求",
        "cat_label": "特殊出行",
        "summary": "客舱携宠与有氧托运两条路径的选择、五步申请流程与下单前核对清单。",
        "about_note": "本文为机票.CC「出行攻略」栏目的携宠出行专题，服务信息引自公开报道，"
                      "各航司宠物运输政策差异较大且可能调整，请以拟乘航司官方公示为准。"
                      "本站不销售机票、不参与任何交易环节。",
    },
    {
        "slug": "winter-season-new-route-promo",
        "drafts": ["winter-season-new-route-promo-2026-10-21.md"],
        "column": "deals.html",
        "column_name": "优惠活动",
        "date": "2026-10-21",
        "review": STAMP["next_review_price"],
        "scope": "促销与规律",
        "title_fallback": "换季首周机票怎么捡漏",
        "meta_title": "换季首周机票怎么捡漏：新航线促销价的规律与核对清单-机票.CC",
        "head_desc_extra": "文中含换季时间节点与市场特征表、三类促销形态解读、四步比价节奏与下单前核对清单、FAQ。",
        "keywords": "换季机票捡漏,新航线促销价,冬春航季机票优惠,11月机票什么时候买,低价机票规律,机票促销怎么核对",
        "cat_label": "促销规律",
        "summary": "新航线头几周的促销规律、三类促销形态的核对方法与11月比价节奏。",
        "about_note": "本文为机票.CC「优惠活动」栏目的换季促销规律专题，航季数据与促销提示整理自财联社、川观新闻等公开报道，"
                      "不提供任何精确票价，实际价格以官方渠道实时查询为准。本站不销售机票、不参与任何交易环节。",
    },
]


def articles_of(column_file: str):
    """取某栏目下已登记的文章，按日期倒序（最新的排前面）。"""
    return sorted([a for a in ARTICLES if a["column"] == column_file],
                  key=lambda a: a["date"], reverse=True)


def column_articles_section(column_file: str, head_title: str, head_desc: str):
    """栏目页的「本栏目专题」文章列表，与 price 页的专题区块使用同一套标记与样式。"""
    arts = articles_of(column_file)
    if not arts:
        return ""
    items = "\n".join(f"""        <li class="list-item">
          <span class="list-num">{i+1}</span>
          <div class="list-main">
            <h4><a href="{article_url(a['slug'])}">{e(a.get('resolved_title') or a['slug'])}</a></h4>
            <p>{e(a['summary'])}</p>
          </div>
          <div class="list-side"><span class="badge badge-gray">{e(a['cat_label'])}</span><br>{a['date']}</div>
        </li>""" for i, a in enumerate(arts))
    return f"""
    <section class="section">
      <div class="section-head">
        <div>
          <h2><span class="bar"></span>{e(head_title)}</h2>
          <p>{e(head_desc)}</p>
        </div>
      </div>
      <ul class="list">
{items}
      </ul>
    </section>
"""


def article_url(slug: str) -> str:
    return f"{slug}.html"


FAQ = [
    ("机票.CC 是购票平台吗？可以直接在这里买票吗？",
     "不是。机票.CC 是机票资讯与攻略类内容站点，我们不直接出票，也不参与交易。站内提供的价格信息用于帮助你了解行情与判断预订时机，实际购票请前往航空公司官方渠道或正规票务平台。"),
    ("站内的机票价格是实时的吗？",
     "航线、班次、规则与价格类信息均来自公开渠道整理，并非实时报价。机票价格受舱位、日期、余票与促销影响波动频繁，请在购票渠道以实际查询结果为准。页面上会标注每份内容的更新日期与来源。"),
    ("怎样订阅机票.CC 的内容更新？",
     "在页脚的「订阅与联系」栏，或在首页订阅横幅填写邮箱即可；也可以直接向站点智能体邮箱发一封邮件。订阅后每周最多 2 封，内容为机票资讯与航线资讯；不发广告、不转卖邮箱，回信写「退订」即可停止。详见关于我们页的隐私与退订说明。"),
    ("网站会推荐具体的购票渠道吗？",
     "我们提供的是判断方法与信息对比，不针对具体票务机构做导流推荐。若内容中出现外部参考链接，均会注明来源，便于你自行核验。"),
    ("为什么有的内容没有给出精确数字？",
     "机票价格与航班时刻变动频繁，无法长期稳定的数据我们不做精确断言，只提供区间与判断方法，避免误导。"),
]


# ----------------------------------------------------------------------
# 工具函数
# ----------------------------------------------------------------------
def e(text: str) -> str:
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def head(title, desc, active, canonical, jsonld):
    nav_js = "\n".join(
        f'      <li><a href="{f}"{" class=\"is-active\"" if f == active else ""}>{e(n)}</a></li>'
        for f, n in NAV
    )
    ld = "\n".join(
        '  <script type="application/ld+json">' + json.dumps(s, ensure_ascii=False) + "</script>"
        for s in jsonld
    )
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(title)}</title>
  <meta name="description" content="{e(desc)}">
  <meta name="keywords" content="机票,机票价格,机票资讯,航线资讯,出行攻略,航司动态,优惠活动,机票.CC">
  <meta name="author" content="{SITE['name']}">
  <meta name="robots" content="index,follow,max-image-preview:large">
  <link rel="canonical" href="{canonical}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="{SITE['name']}">
  <meta property="og:title" content="{e(title)}">
  <meta property="og:description" content="{e(desc)}">
  <meta property="og:url" content="{canonical}">
  <meta name="theme-color" content="#0b63c5">
  <link rel="stylesheet" href="assets/css/style.css">
{ld}
</head>
<body>
"""


def header(active):
    links = "\n".join(
        f'        <li><a href="{f}"{" class=\"is-active\"" if f == active else ""}>{e(n)}</a></li>'
        for f, n in NAV
    )
    return f"""<header class="site-header">
  <div class="container header-inner">
    <a class="brand" href="index.html" aria-label="{SITE['name']} 首页">
      <span class="brand-mark" aria-hidden="true">机</span>
      <span class="brand-text">
        <span class="brand-name">机票<span class="tld">.CC</span></span>
        <span class="brand-sub">FLIGHT INFO</span>
      </span>
    </a>
    <button class="nav-toggle" id="navToggle" aria-label="展开导航" aria-expanded="false">☰</button>
    <nav class="nav" id="siteNav" aria-label="主导航">
      <ul>
{links}
      </ul>
    </nav>
    <div class="header-actions">
      <a class="btn btn-accent btn-sm" href="{MAILTO_SUB}">{CTA_SUB}</a>
    </div>
  </div>
</header>
"""


def subscribe_band():
    return f"""<section class="section" id="subscribe">
  <div class="container">
    <div class="subscribe-band">
      <div>
        <h2>航线资讯与出行提醒，我们替你盯着</h2>
        <p><b>每周最多 2 封</b>：新增与复航航线、航司规则变更、出行攻略要点。不发广告、不转卖邮箱，回信写「退订」即可停止。</p>
        <p class="sub-note">订阅后你会收到什么：一条本周值得关注的航线 + 一份出行决策提醒。我们不卖票、不导流，只做信息。</p>
      </div>
      <div>
        <form class="sub-form" id="subForm" novalidate>
          <label class="sr-only" for="subEmail">订阅邮箱</label>
          <input type="email" id="subEmail" name="email" placeholder="你的邮箱地址" required>
          <button class="btn btn-accent" type="submit">订阅机票资讯</button>
        </form>
        <div class="sub-msg" id="subMsg" role="status"></div>
        <p class="sub-note">我们会唤起你的邮件客户端，发送到站点智能体邮箱 {SITE['agent_email']}。
          查看<a href="about.html#privacy" style="color:#dff0ff;text-decoration:underline;">隐私与退订说明</a>。</p>
      </div>
    </div>
  </div>
</section>
"""


def footer():
    col_links = "\n".join(
        f'          <li><a href="{c["file"]}">{e(c["name"])}</a></li>' for c in COLUMNS
    )
    return f"""<footer class="site-footer">
  <div class="container">
    <div class="footer-top">
      <div class="footer-brand">
        <span class="brand-name">机票<span class="tld">.CC</span></span>
        <span class="brand-sub">FLIGHT INFO</span>
        <p>{e(SITE['desc'])}</p>
      </div>

      <div class="footer-col">
        <h4>内容栏目</h4>
        <ul>
{col_links}
        </ul>
      </div>

      <div class="footer-col">
        <h4>关于与规范</h4>
        <ul>
          <li><a href="about.html">关于我们</a></li>
          <li><a href="about.html#standards">内容与数据规范</a></li>
          <li><a href="about.html#disclaimer">免责声明</a></li>
          <li><a href="about.html#faq">常见问题</a></li>
        </ul>
      </div>

      <div class="footer-col">
        <h4>用户服务</h4>
        <ul>
          <li><a href="{MAILTO_SUB}">邮件订阅</a></li>
          <li><a href="price.html">航空公司导航</a></li>
          <li><a href="guides.html">出行攻略索引</a></li>
          <li><a href="about.html#contact">内容纠错与投稿</a></li>
        </ul>
      </div>

      <div class="footer-col">
        <div class="agent-mail-card">
          <h4><span class="ai-dot" aria-hidden="true"></span>订阅与联系</h4>
          <p>站点智能体邮箱，接受订阅申请、内容纠错与合作咨询，通常 1 个工作日内回复。</p>
          <a class="mail-addr" href="{MAILTO}" title="点击发送邮件">{SITE['agent_email']}</a>
          <div class="mail-actions">
            <a class="btn btn-ghost btn-sm" href="{MAILTO_SUB}">✉ 订阅机票资讯</a>
            <button class="btn btn-ghost btn-sm" type="button" id="copyMail" data-mail="{SITE['agent_email']}">⧉ 复制邮箱</button>
          </div>
        </div>
      </div>
    </div>

    <p class="footer-disclaimer">
      免责声明：本站为机票信息聚合与资讯平台，<b>不提供机票销售、出票及任何交易服务</b>。站内价格、活动、规则等信息均来源于公开渠道，仅供参考；
      机票价格实时变动，实际价格与规则请以航空公司/官方售票渠道实时公示为准。本站不对因使用本站信息产生的决策结果承担责任。
      站内演示用示例数据已明确标注。如含导流或合作链接，将显式标注「广告 / 合作」。
    </p>

    <div class="footer-bottom">
      <span>© 2026 {SITE['name']} · {SITE['domain_cn']}（{SITE['punycode']}）</span>
      <span>
        <a href="about.html">关于我们</a> ·
        <a href="about.html#standards">内容规范</a> ·
        <a href="about.html#disclaimer">免责声明</a> ·
        <a href="{MAILTO}">{SITE['agent_email']}</a>
      </span>
      <span>{SITE['icp']}</span>
    </div>
  </div>
</footer>
<script src="assets/js/data.js"></script>
<script src="assets/js/main.js"></script>
</body>
</html>
"""


def breadcrumb(items, canonical):
    """items: [(name, url)] 最后一项为当前页"""
    parts = []
    for i, (name, url) in enumerate(items):
        if i == len(items) - 1:
            parts.append(f'<span aria-current="page">{e(name)}</span>')
        else:
            parts.append(f'<a href="{url}">{e(name)}</a>')
    return (
        '  <nav class="breadcrumb" aria-label="面包屑">'
        + '<span class="sep">/</span>'.join(parts)
        + "</nav>\n"
    )


def page_hero(items, h1, lead, next_review=None, scope=None):
    bc = breadcrumb(items, "")
    return f"""<section class="page-hero">
  <div class="container">
{bc}    <h1>{e(h1)}</h1>
    <p class="lead">{e(lead)}</p>
  </div>
</section>
"""


def stamp(next_review, scope="数据"):
    """E-E-A-T：页面级更新戳（最后更新 + 下次复核）"""
    return f"""    <div class="stamp">
      <span>🕘 最后更新：<b>{STAMP['updated']}</b></span>
      <span>🔁 下次复核：<b>{next_review}</b>（{scope}类内容按周期复核，过期内容将更新或归档）</span>
    </div>
"""


def source_note(extra="", next_review=None):
    nr = next_review or STAMP["next_review_price"]
    return f"""    <div class="source-note">
      <b>信息来源与口径：</b>本页航线、班次、规则与活动信息整理自航司官方渠道及媒体公开报道，并标注更新时间；
      具体航班、价格与规则以各航司及官方售票渠道实时公示为准。
      本站不销售机票、不代收票款、不参与任何交易。本页最后更新 {STAMP['updated']}，下次复核 {nr}。{extra}
    </div>
"""


def write(path: Path, content: str):
    path.write_text(content, encoding="utf-8")
    print("generated:", path.name)


# ----------------------------------------------------------------------
# 首页
# ----------------------------------------------------------------------
def build_index():
    ld = [
        {"@context": "https://schema.org", "@type": "WebSite", "name": SITE["name"],
         "url": BASE_URL + "/", "inLanguage": "zh-CN",
         "description": SITE["desc"],
         "potentialAction": {"@type": "SearchAction",
                             "target": BASE_URL + "/index.html?q={search_term_string}",
                             "query-input": "required name=search_term_string"}},
        {"@context": "https://schema.org", "@type": "Organization", "name": SITE["name"],
         "url": BASE_URL + "/", "email": SITE["agent_email"],
         "description": "机票资讯类内容站点，提供航空公司导航、航线资讯、出行攻略、航司动态与优惠活动信息。"},
    ]
    title = "机票.CC｜不卖票的机票信息站·价格规律与出行攻略"
    desc = "机票.CC 是中立机票信息平台：查机票价格规律、看航线资讯、学乘机攻略、盯航司与优惠动态。本站不卖票，只帮你做对出行决定。"

    col_cards = "\n".join(f"""        <a class="col-card" href="{c['file']}">
          <span class="col-ico" aria-hidden="true">{c['ico']}</span>
          <h3>{e(c['name'])}</h3>
          <p>{e(c['desc'])}</p>
          <span class="col-meta">{e(c['freq'])} →</span>
        </a>""" for c in COLUMNS)

    route_cards = "\n".join(f"""        <article class="card">
          <div class="card-cover" aria-hidden="true">🗺️</div>
          <div class="card-body">
            <span class="badge badge-brand">{e(r[2])}</span>
            <h3><a href="routes.html">{e(r[1])}</a></h3>
            <p>{e(r[6][:64])}…</p>
            <div class="card-foot"><span>{r[3]}</span><span>约 {r[4]} 分钟</span></div>
          </div>
        </article>""" for r in ROUTES if r[5])

    guide_items = "\n".join(f"""        <li class="list-item">
          <span class="list-num">{i+1}</span>
          <div class="list-main">
            <h4><a href="guides.html">{e(g[1])}</a></h4>
            <p>{e(g[6])}</p>
          </div>
          <div class="list-side"><span class="badge badge-gray">{e(g[2])}</span><br>{g[3]}</div>
        </li>""" for i, g in enumerate(GUIDES[:5]))

    tl_items = "\n".join(f"""        <div class="tl-item">
          <div class="tl-date">{a[0]} · {e(a[1])} · <span class="badge badge-brand">{e(a[3])}</span></div>
          <h4>{e(a[2])}</h4>
          <p>{e(a[4])}</p>
        </div>""" for a in AIRLINES[:4])

    deal_cards = "\n".join(f"""        <article class="card">
          <div class="card-body">
            <span class="badge badge-accent">{e(d[3])}</span>
            <h3><a href="deals.html">{e(d[1])}</a></h3>
            <p>{e(d[6])}</p>
            <div class="card-foot"><span>{e(d[2])}</span><span>截止：{e(d[4])}</span></div>
          </div>
        </article>""" for d in DEALS[:3])

    faq_html = "\n".join(f"""      <div class="faq-item">
        <button class="faq-q" type="button" aria-expanded="false">{e(q)}<span class="ico">+</span></button>
        <div class="faq-a">{e(a)}</div>
      </div>""" for q, a in FAQ[:3])

    tags = "".join(f'<a class="tag" href="{c["file"]}">#{e(c["short"])}</a>' for c in COLUMNS)

    body = header("index.html") + f"""
<main>
  <section class="hero">
    <div class="container hero-grid">
      <div>
        <h1>不卖票的机票信息站，<span class="hl">只帮你做对出行决定</span></h1>
        <p class="hero-lead">
          机票.CC 是机票资讯与信息聚合站点：汇总航空公司官网导航、解读航线资讯、拆解出行攻略、汇总航司动态与优惠活动。
          我们不提供购票与交易，只把「机票什么时候买、怎么买才不亏」用可核对的数据和中立的态度讲清楚。
        </p>
        <div class="hero-tags">
          <span class="tag tag-solid">✈ 中立信息站 · 不卖票 · 不导流</span>
          <span class="tag">📅 数据更新：{SITE['updated']}</span>
          <span class="tag">✉ {SITE['agent_email']}</span>
        </div>
        <div class="hero-tags">{tags}</div>
      </div>
      <div class="search-card">
        <h3>站内搜索</h3>
        <p class="hint">输入航线、城市或关键词，快速定位相关内容</p>
        <form class="search-box" id="searchForm" role="search" onsubmit="return false;">
          <label class="sr-only" for="searchInput">站内搜索</label>
          <input type="search" id="searchInput" placeholder="例如：上海 北京 / 中转 / 行李" autocomplete="off">
          <button class="btn btn-primary" type="submit">搜索</button>
        </form>
        <div class="search-results" id="searchResults">
          <p class="search-empty">试试搜索「北京」「行李」「会员日」等关键词。</p>
        </div>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="container">
      <div class="section-head">
        <div>
          <h2><span class="bar"></span>网站五大内容板块</h2>
          <p>围绕「价格—航线—攻略—航司—优惠」五个维度组织内容，覆盖出行决策全链路</p>
        </div>
      </div>
      <div class="col-grid">
{col_cards}
      </div>
    </div>
  </section>

{subscribe_band()}

  <section class="section">
    <div class="container">
      <div class="section-head">
        <div>
          <h2><span class="bar"></span>热门航线资讯</h2>
          <p>班次结构、运力变化与价格节奏的航线级解读</p>
        </div>
        <a class="more-link" href="routes.html">进入航线资讯 →</a>
      </div>
      <div class="grid-3">
{route_cards}
      </div>
    </div>
  </section>

  <section class="section">
    <div class="container">
      <div class="section-head">
        <div>
          <h2><span class="bar"></span>出行攻略</h2>
          <p>购票时机、退改签、中转联程与行李规则的实操方法</p>
        </div>
        <a class="more-link" href="guides.html">全部攻略 →</a>
      </div>
      <ul class="list">
{guide_items}
      </ul>
    </div>
  </section>

  <section class="section">
    <div class="container">
      <div class="layout-split">
        <div>
          <div class="section-head">
            <div>
              <h2><span class="bar"></span>航司动态</h2>
              <p>航季调整、规则变更与会员计划的集中梳理</p>
            </div>
            <a class="more-link" href="airlines.html">更多动态 →</a>
          </div>
          <div class="timeline">
{tl_items}
          </div>
        </div>
        <aside>
          <div class="side-box">
            <h3><span class="bar"></span>优惠活动</h3>
            <ul class="side-list">
{''.join(f'<li><a href="deals.html">{e(d[1])}</a></li>' for d in DEALS[:5])}
            </ul>
          </div>
          <div class="side-box">
            <h3><span class="bar"></span>订阅与联系</h3>
            <p class="muted" style="margin-bottom:10px;">订阅机票资讯，或向我们反馈内容问题。</p>
            <a class="btn btn-primary btn-block btn-sm" href="{MAILTO_SUB}">✉ 订阅机票资讯</a>
            <p class="muted" style="margin:10px 0 0;font-size:12.5px;word-break:break-all;">{SITE['agent_email']}</p>
          </div>
        </aside>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="container">
      <div class="section-head">
        <div>
          <h2><span class="bar"></span>优惠活动</h2>
          <p>促销节点的规则解读与价值判断</p>
        </div>
        <a class="more-link" href="deals.html">全部活动 →</a>
      </div>
      <div class="grid-3">
{deal_cards}
      </div>
    </div>
  </section>

  <section class="section">
    <div class="container">
      <div class="section-head">
        <div>
          <h2><span class="bar"></span>常见问题</h2>
          <p>关于本站定位、数据与订阅方式</p>
        </div>
        <a class="more-link" href="about.html#faq">全部问题 →</a>
      </div>
{faq_html}
    </div>
  </section>
</main>
{footer()}"""
    write(ROOT / "index.html", head(title, desc, "index.html", BASE_URL + "/", ld) + body)


# ----------------------------------------------------------------------
# 栏目页
# ----------------------------------------------------------------------
def build_price():
    ld = [
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "首页", "item": BASE_URL + "/"},
            {"@type": "ListItem", "position": 2, "name": "航空公司导航", "item": BASE_URL + "/price.html"}]},
        {"@context": "https://schema.org", "@type": "ItemList", "name": "航空公司官网导航",
         "itemListElement": [
             {"@type": "ListItem", "position": i + 1, "name": n, "url": "https://" + u}
             for i, (n, u, t) in enumerate(AIRLINES_NAV, 1)]},
    ]
    title = "航空公司导航｜48 家国内外航司与平台官网入口-机票.CC"
    desc = "卡片式航空公司导航：48 家国内外客运航司及携程、同程等平台官网入口，直达官方渠道查询航班、票价与规则。"

    # 分组：中国大陆 / 中国港澳台地区 / 在线旅行平台
    HK_MO_TW = {
        "中华航空", "长荣航空", "立荣航空", "华信航空", "台湾虎航",
        "星宇航空", "国泰航空", "香港航空", "香港快运航空", "澳门航空",
    }
    groups = [
        ("中国大陆航空公司", "36 家客运航司",
         [x for x in AIRLINES_NAV if x[2] != "ota" and x[0] not in HK_MO_TW]),
        ("中国港澳台地区航空公司", "10 家地区航司",
         [x for x in AIRLINES_NAV if x[0] in HK_MO_TW]),
        ("在线旅行平台", "OTA 官方入口",
         [x for x in AIRLINES_NAV if x[2] == "ota"]),
    ]

    def card_html(n, u, t, idx):
        cls = "air-c" + str(idx % 6 + 1)
        ota = '<span class="airline-ota">平台</span>' if t == "ota" else ""
        note = f'<span class="airline-note">{e(t)}</span>' if t and t != "ota" else ""
        search = (n + " " + u).lower()
        return f"""        <a class="airline-card {cls}" href="https://{u}" target="_blank" rel="noopener" data-search="{e(search)}">
          <span class="airline-avatar" aria-hidden="true">{e(n[0])}</span>
          <span class="airline-body">
            <span class="airline-name">{e(n)}{ota}</span>
            <span class="airline-url">{e(u)}</span>
            {note}
          </span>
          <span class="airline-go" aria-hidden="true">↗</span>
        </a>"""

    groups_html = ""
    gi = 0
    for gname, gsub, items in groups:
        cards = "\n".join(card_html(n, u, t, gi + i) for i, (n, u, t) in enumerate(items))
        gi += len(items)
        groups_html += f"""
      <div class="airline-group">
        <div class="grid-4 airline-grid">
{cards}
        </div>
      </div>"""

    search_box = """
    <div class="airline-search">
      <span class="ic" aria-hidden="true">🔍</span>
      <input id="airlineSearch" type="search" placeholder="搜索航司或平台名称、域名，如：国航 / cathay / ctrip" autocomplete="off" aria-label="搜索航空公司">
      <span class="airline-count" id="airlineCount">共 48 家</span>
    </div>
    <p class="airline-empty" id="airlineEmpty">没有匹配的航司或平台，换个关键词试试。</p>"""

    nav_section = f"""
    <section class="section">
      {search_box}
{groups_html}
      <div class="source-note" style="margin-top:18px;">
        <b>入口说明：</b>本导航仅提供航空公司及在线旅行平台的官网入口，方便你直达官方渠道查询航班、票价与规则；
        标注「平台」的为在线旅行服务商（OTA），并非航空公司。<b>本站不销售机票、不代收票款、不参与任何交易、不为任何机构导流下单</b>，
        域名信息由站长整理提供，如发现变更欢迎邮件反馈：{SITE['agent_email']}。
      </div>
    </section>
"""

    body = header("price.html") + page_hero(
        [("首页", "index.html"), ("航空公司导航", "price.html")],
        "航空公司导航",
        "48 家国内外航空公司及在线旅行平台的官网入口，卡片式直达；点击卡片跳转官方渠道查询航班、票价与退改规则。",
        next_review=False
    ) + nav_section + f"""
<main class="layout-main">
  <div class="container">
    <section class="section">
      <div class="section-head">
        <div>
          <h2><span class="bar"></span>相关攻略</h2>
          <p>关于买票与航司，这些攻略能帮上忙</p>
        </div>
        <a class="more-link" href="guides.html">全部攻略 →</a>
      </div>
      <ul class="list">
        <li class="list-item"><span class="list-num">1</span><div class="list-main">
          <h4><a href="best-time-to-buy.html">机票什么时候买最划算？基于价格曲线的预订窗口分析</a></h4>
          <p>为什么「提前 30 天」不是一个通用答案。</p></div>
          <div class="list-side"><span class="badge badge-gray">购票技巧</span></div></li>
        <li class="list-item"><span class="list-num">2</span><div class="list-main">
          <h4><a href="guides.html">特价票的退改签陷阱：低价背后的真实成本</a></h4>
          <p>把退改规则折进总成本再做比较。</p></div>
          <div class="list-side"><span class="badge badge-gray">避坑指南</span></div></li>
        <li class="list-item"><span class="list-num">3</span><div class="list-main">
          <h4><a href="guides.html">错峰出行指南：非高峰日期的价格洼地</a></h4>
          <p>周中与周末的价差，往往比促销更实在。</p></div>
          <div class="list-side"><span class="badge badge-gray">错峰出行</span></div></li>
      </ul>
    </section>
  </div>
</main>
{subscribe_band()}
<script>
(function () {{
  var inp = document.getElementById('airlineSearch');
  if (!inp) return;
  var cards = Array.prototype.slice.call(document.querySelectorAll('.airline-card'));
  var groups = Array.prototype.slice.call(document.querySelectorAll('.airline-group'));
  var empty = document.getElementById('airlineEmpty');
  var count = document.getElementById('airlineCount');
  function filter() {{
    var q = inp.value.trim().toLowerCase();
    var shown = 0;
    groups.forEach(function (g) {{
      var gc = g.querySelectorAll('.airline-card');
      var vis = 0;
      gc.forEach(function (c) {{
        var match = !q || c.getAttribute('data-search').indexOf(q) > -1;
        c.style.display = match ? '' : 'none';
        if (match) vis++;
      }});
      g.style.display = vis ? '' : 'none';
      shown += vis;
    }});
    if (count) count.textContent = '共 ' + shown + ' 家';
    if (empty) empty.classList.toggle('show', shown === 0);
  }}
  inp.addEventListener('input', filter);
}})();
</script>
{footer()}"""
    write(ROOT / "price.html", head(title, desc, "price.html", BASE_URL + "/price.html", ld) + body)


def build_routes():
    ld = [
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "首页", "item": BASE_URL + "/"},
            {"@type": "ListItem", "position": 2, "name": "航线资讯", "item": BASE_URL + "/routes.html"}]},
        {"@context": "https://schema.org", "@type": "ItemList", "name": "航线资讯列表",
         "itemListElement": [
             {"@type": "ListItem", "position": i + 1, "name": r[1]} for i, r in enumerate(ROUTES)]},
    ]
    title = "航线资讯｜新开航线·直飞航线·中转与机场对比-机票.CC"
    desc = "查最新航线资讯：新开与复航航线、直飞/中转/经停怎么选、首都大兴虹桥浦东机场对比，出行前先看航线再订票。"

    cats = ["全部"] + list(dict.fromkeys(r[2] for r in ROUTES))
    chip_html = "".join(
        f'      <button class="chip{" is-active" if c == "全部" else ""}" type="button" data-filter="{c}">{c}</button>\n'
        for c in cats
    )
    cards = "\n".join(f"""        <article class="card js-item" data-cat="{r[2]}">
          <div class="card-cover" aria-hidden="true">🗺️</div>
          <div class="card-body">
            <span class="badge badge-brand">{e(r[2])}</span>
            <h3><a href="routes.html">{e(r[1])}</a></h3>
            <p>{e(r[6])}</p>
            <div class="card-foot"><span>{r[3]}</span><span>约 {r[4]} 分钟阅读{' · 🔥 热门' if r[5] else ''}</span></div>
          </div>
        </article>""" for r in ROUTES)

    body = header("routes.html") + page_hero(
        [("首页", "index.html"), ("航线资讯", "routes.html")],
        "航线资讯",
        "同一个目的地，出发地、班次密度与中转点的选择会显著改变出行成本与体验。本栏目按航线类型整理可复用的判断依据。",
        STAMP["next_review_price"], "数据"
    ) + f"""
<main class="layout-main">
  <div class="container">
    <div class="filter-bar">
{chip_html}
    </div>
    <div class="grid-3">
{cards}
    </div>

    <section class="section">
      <div class="section-head">
        <div>
          <h2><span class="bar"></span>航线资讯的写法说明</h2>
          <p>我们希望这个栏目解决什么问题</p>
        </div>
      </div>
      <div class="prose">
        <h2>为什么不做「某航线特价只要 X 元」</h2>
        <p>具体到某个价格的内容生命周期极短：文章发出去的第二天，价格可能已经变了。与其生产一批很快失效的内容，我们更倾向于输出<b>可复用的判断结构</b>——这条航线在什么季节紧、在什么时段有价格洼地、有哪些替代出发地。</p>
        <h2>一条航线资讯通常包含什么</h2>
        <ol class="nums">
          <li><b>航线画像</b>：航程距离、主要承运航司、典型班次密度。</li>
          <li><b>需求节奏</b>：旺季窗口、节假日影响、工作日与周末的差异。</li>
          <li><b>价格区间</b>：给出区间而非单点，说明区间形成的原因。</li>
          <li><b>替代方案</b>：邻近出发地、中转点或相邻日期，是否有更优选择。</li>
          <li><b>数据来源与更新时间</b>：标注引用口径，便于你自行复核。</li>
        </ol>
        <div class="callout">
          <b>提示：</b>本条栏目中的航线与班次为示例说明，用于展示内容结构与页面形态；正式上线后每条内容都将附数据来源与更新日期。
        </div>
      </div>
    </section>
{column_articles_section("routes.html", "航线专题", "把换季与航线结构变化转化为购票判断的深度解读")}
  </div>
</main>
{subscribe_band()}
{footer()}"""
    write(ROOT / "routes.html", head(title, desc, "routes.html", BASE_URL + "/routes.html", ld) + body)


def build_guides():
    ld = [
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "首页", "item": BASE_URL + "/"},
            {"@type": "ListItem", "position": 2, "name": "出行攻略", "item": BASE_URL + "/guides.html"}]},
        {"@context": "https://schema.org", "@type": "ItemList", "name": "出行攻略列表",
         "itemListElement": [
             {"@type": "ListItem", "position": i + 1, "name": g[1]} for i, g in enumerate(GUIDES)]},
    ]
    title = "坐飞机攻略｜第一次坐飞机流程·行李·安检-机票.CC"
    desc = "从买票到登机的完整出行攻略：新手乘机流程、行李托运规定、安检与转机注意事项，一看就懂、照做不迷路。"

    cats = ["全部"] + list(dict.fromkeys(g[2] for g in GUIDES))
    chip_html = "".join(
        f'      <button class="chip{" is-active" if c == "全部" else ""}" type="button" data-filter="{c}">{c}</button>\n'
        for c in cats
    )
    items = "\n".join(f"""        <li class="list-item js-item" data-cat="{g[2]}">
          <span class="list-num">{i+1}</span>
          <div class="list-main">
            <h4><a href="{'best-time-to-buy.html' if g[0] == 'g1' else 'guides.html'}">{e(g[1])}</a></h4>
            <p>{e(g[6])}</p>
          </div>
          <div class="list-side"><span class="badge badge-gray">{e(g[2])}</span><br>{g[3]} · {g[4]} 分钟</div>
        </li>""" for i, g in enumerate(GUIDES))

    body = header("guides.html") + page_hero(
        [("首页", "index.html"), ("出行攻略", "guides.html")],
        "出行攻略",
        "机票只是出行成本的一部分。这个栏目关注「买之前要知道什么」：什么时候买、低价票有什么代价、中转能不能接上、行李怎么算。",
        STAMP["next_review_rule"], "规则与攻略"
    ) + f"""
<main class="layout-main">
  <div class="container">
    <div class="filter-bar">
{chip_html}
    </div>
    <div class="layout-split">
      <div>
        <ul class="list">
{items}
        </ul>
      </div>
      <aside>
        <div class="side-box">
          <h3><span class="bar"></span>本栏目常用概念</h3>
          <ul class="side-list">
            <li><b>最小衔接时间</b><br><span class="muted">两段航班之间机场允许的最短中转时间。</span></li>
            <li><b>行李直挂</b><br><span class="muted">行李从起点托运至终点，中转不需重新提取。</span></li>
            <li><b>舱位等级</b><br><span class="muted">同舱位下的不同票价档位，退改规则各不相同。</span></li>
            <li><b>环比变化</b><br><span class="muted">相对上一更新周期的价格移动方向。</span></li>
          </ul>
        </div>
        <div class="side-box">
          <h3><span class="bar"></span>订阅与联系</h3>
          <p class="muted" style="margin-bottom:10px;">有想看的选题？回信告诉我们。</p>
          <a class="btn btn-primary btn-block btn-sm" href="{MAILTO_SUB}">✉ 订阅机票资讯</a>
          <p class="muted" style="margin:10px 0 0;font-size:12.5px;word-break:break-all;">{SITE['agent_email']}</p>
        </div>
      </aside>
    </div>
{column_articles_section("guides.html", "出行攻略专题", "把购票决策拆成可操作的判断清单与成本账")}
  </div>
</main>
{subscribe_band()}
{footer()}"""
    write(ROOT / "guides.html", head(title, desc, "guides.html", BASE_URL + "/guides.html", ld) + body)


def build_airlines():
    ld = [
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "首页", "item": BASE_URL + "/"},
            {"@type": "ListItem", "position": 2, "name": "航司动态", "item": BASE_URL + "/airlines.html"}]},
        {"@context": "https://schema.org", "@type": "ItemList", "name": "航司动态时间线",
         "itemListElement": [
             {"@type": "ListItem", "position": i + 1, "name": a[2]} for i, a in enumerate(AIRLINES)]},
    ]
    title = "航司动态｜航空公司会员日·新开航线·里程政策-机票.CC"
    desc = "跟踪各航司动态：会员日一览、新开与复航航线、行李额度与里程政策变化，帮你在合适的航司与合适的时间下手。"

    tl = "\n".join(f"""          <div class="tl-item js-item" data-cat="{a[3]}">
            <div class="tl-date">{a[0]} · {e(a[1])} · <span class="badge badge-brand">{e(a[3])}</span></div>
            <h4>{e(a[2])}</h4>
            <p>{e(a[4])}</p>
          </div>""" for a in AIRLINES)

    body = header("airlines.html") + page_hero(
        [("首页", "index.html"), ("航司动态", "airlines.html")],
        "航司动态",
        "航季调整、规则变更、会员计划改动，是影响出行成本的高频变量。本栏目按时间线汇总公开信息，并说明它与旅客的实际关系。",
        STAMP["next_review_rule"], "规则与动态"
    ) + f"""
<main class="layout-main">
  <div class="container">
    <div class="layout-split">
      <div>
        <div class="timeline">
{tl}
        </div>
      </div>
      <aside>
        <div class="side-box">
          <h3><span class="bar"></span>为什么会关注这些变化</h3>
          <ul class="side-list">
            <li><b>航季调整</b>：冬春与夏秋航季切换时，班次与时刻会成批变化。</li>
            <li><b>规则变更</b>：行李额度、退改条件调整直接影响总成本。</li>
            <li><b>航线恢复</b>：国际与地区航线恢复会带来新的中转组合。</li>
            <li><b>会员计划</b>：里程累积与兑换规则调整改变里程的实际价值。</li>
          </ul>
        </div>
        <div class="side-box">
          <h3><span class="bar"></span>订阅与联系</h3>
          <p class="muted" style="margin-bottom:10px;">规则变更提醒，一封邮件说清。</p>
          <a class="btn btn-primary btn-block btn-sm" href="{MAILTO_SUB}">✉ 订阅机票资讯</a>
          <p class="muted" style="margin:10px 0 0;font-size:12.5px;word-break:break-all;">{SITE['agent_email']}</p>
        </div>
      </aside>
    </div>
{source_note(' 航司动态内容整理自航司及公开信息渠道，涉及具体规则请以航司官方公告为准。')}
{column_articles_section("airlines.html", "航司动态专题", "从运力与规则变化中读出购票机会的深度梳理")}
  </div>
</main>
{subscribe_band()}
{footer()}"""
    write(ROOT / "airlines.html", head(title, desc, "airlines.html", BASE_URL + "/airlines.html", ld) + body)


def build_deals():
    ld = [
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "首页", "item": BASE_URL + "/"},
            {"@type": "ListItem", "position": 2, "name": "优惠活动", "item": BASE_URL + "/deals.html"}]},
        {"@context": "https://schema.org", "@type": "ItemList", "name": "优惠活动列表",
         "itemListElement": [
             {"@type": "ListItem", "position": i + 1, "name": d[1]} for i, d in enumerate(DEALS)]},
    ]
    title = "机票优惠活动｜特价机票·促销日历·规则解读-机票.CC"
    desc = "解读机票优惠的适用规则与限制条件：早鸟、会员日、促销日历与错峰出行，帮你在合适的时间下手，也帮你识别不划算的促销。"

    cats = ["全部", "早鸟折扣", "会员日", "联程优惠", "错峰出行", "权益兑换", "人群优惠"]
    chip_html = "".join(
        f'      <button class="chip{" is-active" if c == "全部" else ""}" type="button" data-filter="{c}">{c}</button>\n'
        for c in cats
    )
    cards = "\n".join(f"""        <article class="card js-item" data-cat="{d[3]}">
          <div class="card-body">
            <span class="badge badge-accent">{e(d[3])}</span>
            <h3><a href="deals.html">{e(d[1])}</a></h3>
            <p>{e(d[6])}</p>
            <div class="card-foot"><span>{e(d[2])}</span><span>截止：{e(d[4])}</span></div>
          </div>
        </article>""" for d in DEALS)

    body = header("deals.html") + page_hero(
        [("首页", "index.html"), ("优惠活动", "deals.html")],
        "优惠活动",
        "促销信息真正需要的不是罗列，而是判断：限制条件是什么、和你的行程是否匹配、为了折扣要多付出什么。",
        STAMP["next_review_rule"], "规则与活动"
    ) + f"""
<main class="layout-main">
  <div class="container">
    <div class="filter-bar">
{chip_html}
    </div>
    <div class="grid-3">
{cards}
    </div>

    <section class="section">
      <div class="section-head">
        <div>
          <h2><span class="bar"></span>判断一次促销是否划算：四步法</h2>
          <p>先看限制，再看价格</p>
        </div>
      </div>
      <div class="prose">
        <ol class="nums">
          <li><b>先看退改规则。</b>折扣票通常退改费用高甚至不可退。如果你的行程有变动可能，把退改成本算进去再比较。</li>
          <li><b>再看行李额度。</b>部分低价产品不含免费托运行李，加上行李费后总价可能反超普通票价。</li>
          <li><b>然后看日期匹配度。</b>促销往往限定特定出行日期段。如果你的日期不在范围内，这个活动的价值为零。</li>
          <li><b>最后和均价比，而不是和原价比。</b>「原价」的参考意义有限，与你所在航线的实际均价对比才有判断价值。</li>
        </ol>
        <div class="callout callout-warn">
          <b>注意：</b>本站不代为发放或核销任何优惠，也不销售机票。所有活动信息仅作规则解读与信息整理，具体条款、适用范围与有效期请以发布方官方页面为准。
        </div>
      </div>
    </section>
{column_articles_section("deals.html", "优惠解读专题", "把促销与价格窗口转化为「是否值得下手」的判断框架")}
{source_note()}
  </div>
</main>
{subscribe_band()}
{footer()}"""
    write(ROOT / "deals.html", head(title, desc, "deals.html", BASE_URL + "/deals.html", ld) + body)


def build_about():
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q,
                              "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}
    ld = [
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "首页", "item": BASE_URL + "/"},
            {"@type": "ListItem", "position": 2, "name": "关于我们", "item": BASE_URL + "/about.html"}]},
        {"@context": "https://schema.org", "@type": "AboutPage", "name": "关于机票.CC",
         "url": BASE_URL + "/about.html",
         "description": "机票.CC 的站点定位、内容与数据规范、免责声明、联系方式与订阅入口。"},
        faq_ld,
    ]
    title = "关于我们｜定位、内容规范与联系方式-机票.CC"
    desc = "了解机票.CC 的站点定位（不卖票的机票信息站）、内容与数据规范、免责声明，以及订阅与联系方式（智能体邮箱）。"

    faq_html = "\n".join(f"""      <div class="faq-item">
        <button class="faq-q" type="button" aria-expanded="false">{e(q)}<span class="ico">+</span></button>
        <div class="faq-a">{e(a)}</div>
      </div>""" for q, a in FAQ)

    body = header("about.html") + page_hero(
        [("首页", "index.html"), ("关于我们", "about.html")],
        "关于我们",
        "机票.CC 是一个机票资讯类内容站点。我们把「不做什么」写清楚，和写清楚「做什么」一样重要。",
        False
    ) + f"""
<main class="layout-main">
  <div class="container">
    <div class="layout-split">
      <div>
        <div class="prose" id="about">
          <h2>我们是谁</h2>
          <p>机票.CC 是一个中文机票资讯站点，域名启用于 <b>机票.CC</b>（{SITE['punycode']}）。我们不做票务交易，只做一件相对窄的事：<b>把机票相关的信息整理清楚，并说明它和你的出行决策有什么关系</b>。</p>
          <p>机票信息的特点是「变动快、口径杂、误导多」。同一张票的价格随日期与舱位波动，同一个促销在不同航线的价值完全不同。我们的价值不在于告诉你「现在最低价是多少」，而在于帮你建立一套判断方法。</p>

          <h2>我们做什么</h2>
          <ul class="dots">
            <li><b>航空公司导航</b>：48 家国内外航司与平台官网入口卡片导航，直达官方渠道。</li>
            <li><b>航线资讯</b>：解读航线的班次结构、需求节奏与替代方案。</li>
            <li><b>出行攻略</b>：购票时机、退改签、中转联程、行李与出行保障的实操方法。</li>
            <li><b>航司动态</b>：航季调整、规则变更与会员计划的公开信息汇总。</li>
            <li><b>优惠活动</b>：促销规则的解读与「是否划算」的判断框架。</li>
          </ul>

          <h2>我们不做什么</h2>
          <ul class="dots">
            <li><b>不销售机票</b>，不代收票款，不参与任何交易环节。</li>
            <li><b>不为具体票务机构做导流推荐</b>，内容中不设置以成交为目的的推广位。</li>
            <li><b>不发布无法长期稳定的精确数字</b>，不确定的数据只给区间与方法。</li>
            <li><b>不做关键词堆砌、隐藏文本</b>等以欺骗搜索引擎为目的的优化。</li>
          </ul>

          <h2 id="standards">内容与数据规范</h2>
          <p>为了让内容可被核查，我们遵循以下四条规则：</p>
          <ol class="nums">
            <li><b>标注来源与更新时间。</b>价格、班次、规则类信息均注明数据来源与更新日期，便于你自行复核。</li>
            <li><b>区分事实与判断。</b>事实性描述给出出处，趋势性说法明确标注为分析或判断，不与事实混写。</li>
            <li><b>区间优于单点。</b>波动频繁的数据给区间与影响因素，避免单点数字被误读为承诺。</li>
            <li><b>定期复核与修订。</b>过期内容会更新修订日期；无法继续核验的内容予以归档，而不是留在站内继续被引用。</li>
          </ol>
          <div class="callout">
            <b>时效提示：</b>机票价格、航班时刻、行李与退改规则均可能随时调整。站内内容反映的是更新日期当时的信息，请在购票渠道以实际展示结果为准。
          </div>

          <h2 id="disclaimer">免责声明</h2>
          <p>本站所有内容仅为机票资讯与出行参考，<b>不构成任何形式的报价、预订承诺或交易建议</b>。本站不销售机票、不代收票款、不承担任何因依赖站内信息而产生的直接或间接损失。站内演示性质的示例数据均已明确标注，请勿作为购票依据。涉及具体航司规则、政策与价格的最终解释权归相应航司与发布方所有。</p>

          <h2 id="contact">订阅与联系</h2>
          <p>站点的订阅与联系入口统一使用以下<b>智能体邮箱</b>。你可以用它来：订阅航线资讯与出行提醒、反馈内容错误、提出选题建议，或咨询内容合作。</p>
          <div class="agent-mail-card" style="background:#0d1b31;margin:16px 0;">
            <h4><span class="ai-dot"></span>智能体邮箱 · 订阅与联系</h4>
            <p>接受订阅申请、内容纠错与合作咨询，通常 1 个工作日内回复。</p>
            <a class="mail-addr" href="{MAILTO}">{SITE['agent_email']}</a>
            <div class="mail-actions">
              <a class="btn btn-ghost btn-sm" href="{MAILTO_SUB}">✉ 订阅机票资讯</a>
              <button class="btn btn-ghost btn-sm" type="button" data-copy-mail data-mail="{SITE['agent_email']}">⧉ 复制邮箱</button>
            </div>
          </div>
          <table>
            <thead><tr><th>用途</th><th>邮件主题建议</th></tr></thead>
            <tbody>
              <tr><td class="td-strong">订阅内容更新</td><td class="muted">订阅机票资讯：机票.CC</td></tr>
              <tr><td class="td-strong">内容纠错</td><td class="muted">纠错：页面标题 + 问题说明</td></tr>
              <tr><td class="td-strong">选题建议</td><td class="muted">选题：希望看到的内容方向</td></tr>
              <tr><td class="td-strong">内容合作</td><td class="muted">合作：机构名称 + 合作诉求</td></tr>
            </tbody>
          </table>

          <h2 id="privacy">隐私与退订说明</h2>
          <p>订阅只涉及一件事：<b>你的邮箱地址</b>。我们把规则写清楚，你可以据此决定是否订阅。</p>
          <ul class="dots">
            <li><b>我们收集什么</b>：仅你主动发来的邮箱地址与关注方向，不含其他个人信息。</li>
            <li><b>我们怎么用</b>：只用于发送内容更新，不做广告推销，不转卖、不出租、不共享给第三方。</li>
            <li><b>发送频率</b>：每周最多 2 封。没有值得说的事就不发，不做凑数推送。</li>
            <li><b>怎么退订</b>：回信写「退订」即可，无需理由，我们会立即移除你的邮箱。</li>
            <li><b>技术说明</b>：本站为静态站点，订阅通过你的邮件客户端发送；我们不使用追踪像素或行为分析脚本。</li>
          </ul>
        </div>

        <section class="section" id="faq">
          <div class="section-head">
            <div>
              <h2><span class="bar"></span>常见问题</h2>
              <p>关于定位、数据与订阅</p>
            </div>
          </div>
{faq_html}
        </section>
      </div>

      <aside>
        <div class="side-box">
          <h3><span class="bar"></span>快速导航</h3>
          <ul class="side-list">
            <li><a href="#about">我们是谁</a></li>
            <li><a href="#standards">内容与数据规范</a></li>
            <li><a href="#disclaimer">免责声明</a></li>
            <li><a href="#contact">订阅与联系</a></li>
            <li><a href="#privacy">隐私与退订说明</a></li>
            <li><a href="#faq">常见问题</a></li>
          </ul>
        </div>
        <div class="side-box">
          <h3><span class="bar"></span>智能体邮箱</h3>
          <p class="muted" style="margin-bottom:10px;word-break:break-all;">{SITE['agent_email']}</p>
          <a class="btn btn-primary btn-block btn-sm" href="{MAILTO_SUB}">✉ 订阅机票资讯</a>
        </div>
        <div class="side-box">
          <h3><span class="bar"></span>站点信息</h3>
          <ul class="side-list">
            <li>域名：{SITE['domain_cn']}</li>
            <li>Punycode：{SITE['punycode']}</li>
            <li>语言：简体中文</li>
            <li>更新日期：{SITE['updated']}</li>
            <li>{SITE['icp']}</li>
          </ul>
        </div>
      </aside>
    </div>
  </div>
</main>
{subscribe_band()}
{footer()}"""
    write(ROOT / "about.html", head(title, desc, "about.html", BASE_URL + "/about.html", ld) + body)


# ----------------------------------------------------------------------
# 前端数据层
# ----------------------------------------------------------------------
def build_data_js():
    payload = {
        "SITE": SITE,
        "ROUTES": [{"id": r[0], "title": r[1], "cat": r[2], "date": r[3]} for r in ROUTES],
        "GUIDES": [{"id": g[0], "title": g[1], "cat": g[2], "date": g[3]} for g in GUIDES],
        "AIRLINES": [{"date": a[0], "airline": a[1], "title": a[2], "cat": a[3]} for a in AIRLINES],
        "DEALS": [{"id": d[0], "title": d[1], "brand": d[2], "type": d[3], "deadline": d[4]} for d in DEALS],
        "FAQ": [{"q": q, "a": a} for q, a in FAQ],
    }
    index = (
        [{"title": a["resolved_title"],
          "meta": f"{a['column_name']} · {a['cat_label']}",
          "url": article_url(a["slug"])}
         for a in ARTICLES if a.get("resolved_title")]
        + [{"title": r[1], "meta": "航线资讯 · " + r[2], "url": "routes.html"} for r in ROUTES]
        + [{"title": g[1], "meta": "出行攻略 · " + g[2], "url": "guides.html"} for g in GUIDES]
        + [{"title": a[2], "meta": "航司动态 · " + a[1], "url": "airlines.html"} for a in AIRLINES]
        + [{"title": d[1], "meta": "优惠活动 · " + d[3], "url": "deals.html"} for d in DEALS]
    )
    payload["SEARCH_INDEX"] = index
    js = (
        "/* 本文件由 build.py 自动生成，请勿手工修改；数据源见 build.py */\n"
        "const SITE = " + json.dumps(payload["SITE"], ensure_ascii=False, indent=2) + ";\n\n"
        "const ROUTES = " + json.dumps(payload["ROUTES"], ensure_ascii=False, indent=2) + ";\n\n"
        "const GUIDES = " + json.dumps(payload["GUIDES"], ensure_ascii=False, indent=2) + ";\n\n"
        "const AIRLINES = " + json.dumps(payload["AIRLINES"], ensure_ascii=False, indent=2) + ";\n\n"
        "const DEALS = " + json.dumps(payload["DEALS"], ensure_ascii=False, indent=2) + ";\n\n"
        "const FAQ = " + json.dumps(payload["FAQ"], ensure_ascii=False, indent=2) + ";\n\n"
        "const SEARCH_INDEX = " + json.dumps(payload["SEARCH_INDEX"], ensure_ascii=False, indent=2) + ";\n"
    )
    write(ROOT / "assets" / "js" / "data.js", js)


# ----------------------------------------------------------------------
# 极简 Markdown -> HTML（仅覆盖撰稿人产出的语法子集）
# ----------------------------------------------------------------------
def _inline(t: str) -> str:
    t = (t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)
    t = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", t)
    return t


def md_to_html(md: str):
    lines = md.replace("\r\n", "\n").split("\n")
    out, toc = [], []
    i, n = 0, len(lines)

    def flush_para(buf):
        if buf:
            out.append("        <p>" + _inline(" ".join(buf)) + "</p>")
            buf.clear()

    para = []
    while i < n:
        ln = lines[i]
        s = ln.strip()

        # 表格
        if s.startswith("|") and i + 1 < n and re.match(r"^\|[\s:\-|]+\|$", lines[i + 1].strip()):
            flush_para(para)
            head = [c.strip() for c in s.strip("|").split("|")]
            rows, j = [], i + 2
            while j < n and lines[j].strip().startswith("|"):
                rows.append([c.strip() for c in lines[j].strip().strip("|").split("|")])
                j += 1
            t = ['        <div class="table-wrap"><table>', "          <thead><tr>"]
            t += [f"<th>{_inline(h)}</th>" for h in head]
            t.append("</tr></thead>\n          <tbody>")
            for r in rows:
                t.append("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in r) + "</tr>")
            t.append("</tbody>\n        </table></div>")
            out.append("\n".join(t))
            i = j
            continue

        # 标题
        m = re.match(r"^(#{1,4})\s+(.*)$", s)
        if m:
            flush_para(para)
            lvl, txt = len(m.group(1)), m.group(2)
            if lvl == 1:
                out.append(f"        <h2>{_inline(txt)}</h2>")
            elif lvl == 2:
                anchor = "sec-" + str(len(toc) + 1)
                toc.append((anchor, txt))
                out.append(f'        <h2 id="{anchor}">{_inline(txt)}</h2>')
            elif lvl == 3:
                out.append(f"        <h3>{_inline(txt)}</h3>")
            else:
                out.append(f"        <h4>{_inline(txt)}</h4>")
            i += 1
            continue

        # 分隔线
        if re.match(r"^(\*\*\*|___|---)$", s):
            flush_para(para)
            out.append("        <hr>")
            i += 1
            continue

        # 引用
        if s.startswith(">"):
            flush_para(para)
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip().lstrip(">").strip())
                i += 1
            out.append('        <div class="callout">' + _inline(" ".join(buf)) + "</div>")
            continue

        # 无序列表
        if re.match(r"^[-*+]\s+", s):
            flush_para(para)
            items = []
            while i < n and re.match(r"^[-*+]\s+", lines[i].strip()):
                items.append(re.sub(r"^[-*+]\s+", "", lines[i].strip()))
                i += 1
            out.append('        <ul class="dots">')
            out += [f"          <li>{_inline(x)}</li>" for x in items]
            out.append("        </ul>")
            continue

        # 有序列表
        if re.match(r"^\d+[.、]\s+", s):
            flush_para(para)
            items = []
            while i < n and re.match(r"^\d+[.、]\s+", lines[i].strip()):
                items.append(re.sub(r"^\d+[.、]\s+", "", lines[i].strip()))
                i += 1
            out.append('        <ol class="nums">')
            out += [f"          <li>{_inline(x)}</li>" for x in items]
            out.append("        </ol>")
            continue

        if not s:
            flush_para(para)
            i += 1
            continue

        para.append(s)
        i += 1

    flush_para(para)
    return "\n".join(out), toc


def read_article(spec):
    f = None
    for name in spec["drafts"]:
        p = ROOT.parent / "drafts" / name
        if p.exists():
            f = p
            break
    if f is None:
        return None
    md = f.read_text(encoding="utf-8")
    # 去掉构建期注释（Meta 信息块）
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    h1 = ""
    m = re.search(r"^#\s+(.+)$", md, re.M)
    if m:
        h1 = m.group(1).strip()
        md = md[:m.start()] + md[m.end():]
    paras = [p.strip() for p in md.split("\n")
             if p.strip() and not p.strip().startswith(("#", "|", ">", "-", "*", "1.", "["))]
    desc = re.sub(r"[*`\[\]]|\(([^)]+)\)", "", paras[0])[:110] if paras else ""
    return {"h1": h1, "md": md, "desc": desc}


def build_articles():
    for spec in ARTICLES:
        build_article(spec)


def build_article(spec):
    art = read_article(spec)
    if not art:
        print("skip: 文章草稿尚未就绪 ->", spec["slug"])
        return
    body_html, toc = md_to_html(art["md"])
    title = art["h1"] or spec.get("title_fallback", "机票资讯")
    spec["resolved_title"] = title          # 供栏目列表 / 站内搜索索引复用
    desc = art["desc"]
    url = article_url(spec["slug"])
    col = spec["column"]
    col_name = spec["column_name"]
    # 优先用登记的 meta_title（人工控好长度与关键词前置），否则按标题自动截断
    ttl = spec.get("meta_title") or (
        (title[:24] + "-机票.CC") if len(title) > 18 else (title + "-机票.CC"))

    ld = [
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "首页", "item": BASE_URL + "/"},
            {"@type": "ListItem", "position": 2, "name": col_name, "item": BASE_URL + "/" + col},
            {"@type": "ListItem", "position": 3, "name": title, "item": BASE_URL + "/" + url}]},
        {"@context": "https://schema.org", "@type": "Article", "headline": title,
         "description": desc, "inLanguage": "zh-CN",
         "datePublished": spec["date"], "dateModified": spec["date"],
         "author": {"@type": "Organization", "name": SITE["name"]},
         "publisher": {"@type": "Organization", "name": SITE["name"]},
         "mainEntityOfPage": BASE_URL + "/" + url,
         "keywords": spec["keywords"]},
    ]

    toc_html = "\n".join(
        f'            <li><a href="#{a}">{e(t)}</a></li>' for a, t in toc)

    body = header(col) + page_hero(
        [("首页", "index.html"), (col_name, col), (title, url)],
        title,
        desc + "……",
        spec["review"], spec["scope"]
    ) + f"""
<main class="layout-main">
  <div class="container">
    <div class="layout-split">
      <div>
        <article class="prose">
{body_html}
        </article>
        <div class="source-note" style="margin-top:18px;">
          <b>关于本文：</b>{spec['about_note']}
          发现内容问题欢迎邮件反馈：{SITE['agent_email']}
        </div>
      </div>
      <aside>
        <div class="side-box">
          <h3><span class="bar"></span>本文目录</h3>
          <ul class="side-list">
{toc_html}
          </ul>
        </div>
        <div class="side-box">
          <h3><span class="bar"></span>相关栏目</h3>
          <ul class="side-list">
            <li><a href="price.html">航空公司导航</a></li>
            <li><a href="routes.html">航线资讯</a></li>
            <li><a href="guides.html">出行攻略</a></li>
            <li><a href="deals.html">优惠活动</a></li>
          </ul>
        </div>
        <div class="side-box">
          <h3><span class="bar"></span>订阅与联系</h3>
          <p class="muted" style="margin-bottom:10px;">订阅机票资讯与攻略更新。</p>
          <a class="btn btn-primary btn-block btn-sm" href="{MAILTO_SUB}">✉ 订阅机票资讯</a>
          <p class="muted" style="margin:10px 0 0;font-size:12.5px;word-break:break-all;">{SITE['agent_email']}</p>
        </div>
      </aside>
    </div>
  </div>
</main>
{subscribe_band()}
{footer()}"""
    write(ROOT / url,
          head(ttl, desc + spec["head_desc_extra"],
               col, BASE_URL + "/" + url, ld) + body)


# ----------------------------------------------------------------------
# robots.txt / sitemap.xml
# ----------------------------------------------------------------------
def build_seo_files():
    pages = ["index.html", "price.html", "routes.html", "guides.html",
             "airlines.html", "deals.html", "about.html"]
    # 已登记且已生成的文章页一并进 sitemap
    article_pages = [article_url(a["slug"]) for a in ARTICLES
                     if (ROOT / article_url(a["slug"])).exists()]
    for p in article_pages:
        pages.insert(2, p)

    (ROOT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\n"
        f"Sitemap: {BASE_URL}/sitemap.xml\n", encoding="utf-8")

    urls = []
    for p in pages:
        loc = BASE_URL + "/" + ("" if p == "index.html" else p)
        pri = "1.0" if p == "index.html" else ("0.9" if p in
              ("price.html", "guides.html", "best-time-to-buy.html") else "0.7")
        urls.append(f"""  <url>
    <loc>{loc}</loc>
    <lastmod>{STAMP['updated']}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>{pri}</priority>
  </url>""")
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls) + "\n</urlset>\n", encoding="utf-8")
    print("generated: robots.txt / sitemap.xml")


if __name__ == "__main__":
    # 先解析文章标题：栏目列表与站内搜索索引都复用 resolved_title
    build_articles()
    build_index()
    build_price()
    build_routes()
    build_guides()
    build_airlines()
    build_deals()
    build_about()
    build_data_js()
    build_seo_files()
    print("\n✅ 站点构建完成")
