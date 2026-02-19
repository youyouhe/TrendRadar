#!/usr/bin/env python3
# coding=utf-8
"""基础功能测试 - 不需要真实网站访问"""

def test_imports():
    """测试模块导入"""
    print("测试1: 模块导入...")
    try:
        from trendradar.crawler import AgentBrowser
        from trendradar.crawler.tender import TenderData, TenderSource
        from trendradar.crawler.tender import get_tender_source
        print("  ✓ 所有模块导入成功")
        return True
    except Exception as e:
        print(f"  ✗ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_structure():
    """测试数据结构"""
    print("\n测试2: TenderData 数据结构...")
    try:
        from trendradar.crawler.tender import TenderData, TenderStatus
        from datetime import datetime

        tender = TenderData(
            title="山东省XX单位软件开发项目采购公告",
            url="http://ggzy.shandong.gov.cn/test/123",
            source="shandong",
            source_name="山东省政府采购网",
            publish_date=datetime.now(),
            deadline=None,
            project_no="SDCG-2024-001",
            amount="100万元",
            category="服务",
            status=TenderStatus.ACTIVE,
            keywords=["软件", "开发"],
        )

        print(f"  ✓ 创建 TenderData: {tender.title}")
        print(f"  ✓ 状态: {tender.status.value}")
        print(f"  ✓ 金额: {tender.amount}")
        print(f"  ✓ 类别: {tender.category}")
        print(f"  ✓ 关键词: {tender.keywords}")

        # 测试关键词匹配
        assert tender.matches_keywords(["软件"], match_mode="any") == True, "any 匹配失败"
        assert tender.matches_keywords(["软件", "开发"], match_mode="all") == True, "all 匹配失败"
        assert tender.matches_keywords(["山东省XX单位软件开发项目采购公告"], match_mode="exact") == True, "exact 匹配失败"

        # 测试不匹配的情况
        assert tender.matches_keywords(["硬件"], match_mode="any") == False, "应该不匹配"
        assert tender.matches_keywords(["软件", "硬件"], match_mode="all") == False, "应该不匹配"

        print("  ✓ 关键词匹配功能正常（any/all/exact 三种模式）")

        # 测试 to_dict 方法
        tender_dict = tender.to_dict()
        assert "title" in tender_dict, "to_dict 缺少 title"
        assert "status" in tender_dict, "to_dict 缺少 status"
        print("  ✓ to_dict() 方法正常")

        return True
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_source_registry():
    """测试数据源注册"""
    print("\n测试3: 数据源注册...")
    try:
        from trendradar.crawler.tender import get_tender_source, PROVINCE_SOURCES

        print(f"  ✓ 已注册省份: {list(PROVINCE_SOURCES.keys())}")

        source = get_tender_source("shandong")
        print(f"  ✓ 山东数据源: {source.source_name}")
        print(f"  ✓ 省份代码: {source.source_code}")
        print(f"  ✓ 网站: {source.base_url}")

        # 测试错误处理
        try:
            get_tender_source("unknown_province")
            print("  ✗ 应该抛出异常")
            return False
        except ValueError as e:
            print(f"  ✓ 错误处理正常: {e}")

        return True
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_agent_browser():
    """测试 AgentBrowser 基础功能"""
    print("\n测试4: AgentBrowser 初始化...")
    try:
        from trendradar.crawler import AgentBrowser

        # 只测试初始化，不实际启动浏览器
        browser = AgentBrowser(
            session_name="test_session",
            headless=True,
            timeout=30000
        )

        print(f"  ✓ AgentBrowser 实例: {browser}")
        print(f"  ✓ 会话名称: {browser.session_name}")
        print(f"  ✓ 无头模式: {browser.headless}")
        print(f"  ✓ 超时设置: {browser.timeout}ms")

        # 测试定位器构建
        locator1 = browser._build_locator(ref="@e1")
        assert locator1 == "@e1", "ref 定位器错误"

        locator2 = browser._build_locator(placeholder="请输入关键词")
        assert locator2 == 'placeholder="请输入关键词"', "placeholder 定位器错误"

        locator3 = browser._build_locator(role="button", name="查询")
        assert locator3 == 'role="button" name="查询"', "role+name 定位器错误"

        print("  ✓ 定位器构建功能正常")

        return True
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_shandong_source():
    """测试山东数据源类"""
    print("\n测试5: 山东数据源类...")
    try:
        from trendradar.crawler.tender import ShandongTenderSource

        source = ShandongTenderSource(captcha_service="http://localhost:5000")

        print(f"  ✓ 数据源初始化: {source.source_name}")
        print(f"  ✓ 省份代码: {source.source_code}")
        print(f"  ✓ 基础URL: {source.base_url}")
        print(f"  ✓ 验证码服务: {source.captcha_service}")

        # 测试 _extract_ref_from_url 方法
        url1 = "http://ggzy.shandong.gov.cn/?ref=@e10"
        ref1 = source._extract_ref_from_url(url1)
        assert ref1 == "@e10", "ref 提取失败"
        print(f"  ✓ URL ref 提取: {url1} → {ref1}")

        url2 = "http://example.com/test"
        ref2 = source._extract_ref_from_url(url2)
        assert ref2 is None, "应该返回 None"
        print(f"  ✓ 无 ref 的 URL 处理正常")

        return True
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys

    print("=" * 60)
    print("TrendRadar 招标监控 - 基础功能测试")
    print("=" * 60)
    print()
    print("说明: 此测试不需要网络访问或验证码服务")
    print("      仅测试模块导入和数据结构功能")
    print()

    results = []
    results.append(("模块导入", test_imports()))
    results.append(("数据结构", test_data_structure()))
    results.append(("数据源注册", test_source_registry()))
    results.append(("AgentBrowser", test_agent_browser()))
    results.append(("山东数据源", test_shandong_source()))

    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name:20s} {status}")

    passed = sum(r for _, r in results)
    total = len(results)

    print("=" * 60)
    print(f"总计: {passed}/{total} 通过 ({passed*100//total}%)")
    print("=" * 60)

    if passed == total:
        print("\n🎉 所有测试通过！Phase 1 基础功能正常。")
        print("\n下一步:")
        print("  - 启动验证码服务: cd captcha-service && uvicorn app:app --port 5000")
        print("  - 运行完整测试: python3 test_tender_shandong.py")
        sys.exit(0)
    else:
        print(f"\n⚠️  {total - passed} 个测试失败，请检查错误信息。")
        sys.exit(1)
