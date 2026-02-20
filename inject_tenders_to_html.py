#!/usr/bin/env python3
"""
将招标信息注入到已生成的TrendRadar HTML报告中
"""

import json
import re
from pathlib import Path
from typing import List, Dict


def html_escape(text: str) -> str:
    """HTML转义"""
    if not text:
        return ""
    return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def generate_tender_html(tenders: List[Dict]) -> str:
    """生成招标信息的HTML"""
    if not tenders:
        return ""

    html = f"""
                <div class="standalone-section">
                    <div class="standalone-section-header">
                        <div class="standalone-section-title">🏢 招标信息</div>
                        <div class="standalone-section-count">{len(tenders)} 条</div>
                    </div>
                    <div class="standalone-group">
                        <div class="standalone-header">
                            <div class="standalone-name">政府采购招标</div>
                            <div class="standalone-count">{len(tenders)} 条</div>
                        </div>"""

    for j, tender in enumerate(tenders, 1):
        title = tender.get("title", "")
        url = tender.get("url", "")
        source_name = tender.get("source_name", "")
        budget = tender.get("amount") or tender.get("budget")
        deadline = tender.get("deadline", "")
        contact_person = tender.get("contact") or tender.get("contact_person")
        contact_phone = tender.get("phone") or tender.get("contact_phone")
        purchaser = tender.get("purchaser", "")
        publish_date = tender.get("publish_date", "")

        html += f"""
                        <div class="news-item">
                            <div class="news-number">{j}</div>
                            <div class="news-content">
                                <div class="news-header">"""

        # 来源
        if source_name:
            html += f'<span class="source-name">{html_escape(source_name)}</span>'

        # 发布时间
        if publish_date:
            if "T" in str(publish_date):
                try:
                    time_display = str(publish_date)[:10]
                except:
                    time_display = str(publish_date)[:10]
            else:
                time_display = str(publish_date)[:10]
            html += f'<span class="time-info">{html_escape(time_display)}</span>'

        # 预算（高亮）
        if budget:
            html += f'<span class="rank-num top">💰 {html_escape(str(budget))}万</span>'

        # 截止日期
        if deadline:
            deadline_str = str(deadline)
            deadline_display = deadline_str[:16] if len(deadline_str) > 16 else deadline_str
            html += f'<span class="count-info">⏰ {html_escape(deadline_display)}</span>'

        html += """
                                </div>
                                <div class="news-title">"""

        # 标题链接
        escaped_title = html_escape(title)
        if url:
            escaped_url = html_escape(url)
            html += f'<a href="{escaped_url}" target="_blank" class="news-link">{escaped_title}</a>'
        else:
            html += escaped_title

        # 附加信息
        meta_info = []
        if purchaser:
            meta_info.append(f"采购人: {html_escape(purchaser)}")
        if contact_person:
            meta_info.append(f"联系: {html_escape(contact_person)}")
        if contact_phone:
            meta_info.append(f"📞 {html_escape(contact_phone)}")

        if meta_info:
            html += f"""
                                    <div style="font-size: 12px; color: #666; margin-top: 4px;">
                                        {" | ".join(meta_info)}
                                    </div>"""

        html += """
                                </div>
                            </div>
                        </div>"""

    html += """
                    </div>
                </div>"""

    return html


def inject_tenders_to_html(html_file: Path, tenders: List[Dict]) -> bool:
    """将招标信息注入到HTML文件中"""
    if not html_file.exists():
        print(f"[招标] HTML文件不存在: {html_file}")
        return False

    # 读取HTML
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # 生成招标HTML
    tender_html = generate_tender_html(tenders)

    if not tender_html:
        print("[招标] 没有招标数据，跳过注入")
        return False

    # 查找注入位置（在 </body> 之前或 AI分析区域之后）
    # 尝试多个注入点
    injection_patterns = [
        (r'<div class="ai-section">', 'before_ai'),  # AI区域之前
        (r'</body>', 'before_body'),  # body结束前
    ]

    injected = False
    for pattern, position in injection_patterns:
        if pattern in html_content:
            if position == 'before_body':
                html_content = html_content.replace('</body>', f'{tender_html}\n</body>')
            elif position == 'before_ai':
                html_content = html_content.replace(
                    '<div class="ai-section">',
                    f'{tender_html}\n<div class="ai-section">'
                )
            injected = True
            print(f"[招标] 已注入到位置: {position}")
            break

    if not injected:
        print("[招标] 未找到合适的注入位置")
        return False

    # 写回文件
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"[招标] 已注入 {len(tenders)} 条招标信息到: {html_file}")
    return True


def main():
    """主函数"""
    # 查找最新的招标数据
    tender_dir = Path("output/tenders")
    if not tender_dir.exists():
        print("[招标] 招标数据目录不存在")
        return

    tender_files = sorted(tender_dir.glob("*.json"))
    if not tender_files:
        print("[招标] 没有招标数据文件")
        return

    latest_tender_file = tender_files[-1]
    print(f"[招标] 使用招标数据: {latest_tender_file}")

    # 加载招标数据
    with open(latest_tender_file, 'r', encoding='utf-8') as f:
        tenders = json.load(f)

    if not tenders:
        print("[招标] 招标数据为空")
        return

    print(f"[招标] 加载了 {len(tenders)} 条招标信息")

    # 找到最新的HTML报告
    html_file = Path("output/html/latest/current.html")
    if not html_file.exists():
        print(f"[招标] HTML报告不存在: {html_file}")
        return

    # 注入招标信息
    inject_tenders_to_html(html_file, tenders)

    print(f"[招标] 完成！请刷新浏览器查看: {html_file.absolute()}")


if __name__ == "__main__":
    main()
