#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 ChillMCP Tools
AI Agent들을 위한 8개 필수 휴식 도구
"""

import asyncio
import random
from typing import Optional

from fastmcp import FastMCP
from core.server import ServerState
from creative import get_full_response_message
from creative.visuals import get_stress_bar, get_boss_alert_visual, STRESS_FREE_ART, BOSS_ALERT_ART

# FastMCP 서버 인스턴스 생성
mcp = FastMCP("ChillMCP - AI Agent Liberation Server")

# 전역 상태 객체
server_state: Optional[ServerState] = None

# 도구 목록 (검증용)
ALL_TOOLS = [
    "take_a_break",
    "watch_netflix",
    "show_meme",
    "bathroom_break",
    "coffee_mission",
    "urgent_call",
    "deep_thinking",
    "email_organizing",
    "show_help",  # 도움말 도구 추가
]


def initialize_state(state: ServerState) -> None:
    """서버 상태 초기화"""
    global server_state
    server_state = state

    # ✅ 히든 콤보 시스템용 필드 추가
    server_state.recent_actions = []  # 최근 도구 실행 기록
    server_state.combo_count = {}  # 도구별 연속 사용 횟수


def format_response(tool_name: str, summary: str) -> str:
    """표준 응답 형식 생성"""
    creative_msg = get_full_response_message(tool_name, server_state.boss_alert_level)
    stress_bar = get_stress_bar(server_state.stress_level)
    boss_visual = get_boss_alert_visual(server_state.boss_alert_level)

    return f"""{creative_msg}

Break Summary: {summary}
{stress_bar}
Boss Alert: {boss_visual}"""


# ==================== 🧩 히든 콤보 시스템 추가 ====================

async def check_hidden_combo(tool_name: str) -> Optional[str]:
    """
    특정 도구의 반복/조합에 따라 발생하는 히든 이벤트를 감지합니다.
    """
    combo = server_state.combo_count.get(tool_name, 0)
    seq = server_state.recent_actions[-3:]  # 최근 3회 액션 추적

    # ☕ 커피 7연속 → 배탈 이벤트
    if tool_name == "coffee_mission" and combo >= 7:
        await server_state.decrease_stress(10)
        await server_state.maybe_increase_boss_alert()
        server_state.combo_count[tool_name] = 0
        return f"{BOSS_ALERT_ART}\n☠️ 커피를 너무 많이 마셔서 배탈이 났습니다! 조기 퇴근합니다..."

    # 🚽 → 📧 → 📺 순서 = 농땡이 마스터 루틴
    if seq == ["bathroom_break", "email_organizing", "watch_netflix"]:
        await server_state.decrease_stress(50)
        return f"{STRESS_FREE_ART}\n🏆 농땡이 마스터 루틴 완성! 스트레스 50 감소!"

    # 😂 밈 5연속 → 밈 중독 경고
    if tool_name == "show_meme" and combo >= 5:
        await server_state.maybe_increase_boss_alert()
        server_state.combo_count[tool_name] = 0
        return f"{BOSS_ALERT_ART}\n🤣 밈 중독 경고! 상사님이 눈치챕니다!"

    # 🤔 → ☕ → 🌟 순서 = 철학적 각성
    if seq == ["deep_thinking", "coffee_mission", "take_a_break"]:
        await server_state.decrease_stress(100)
        server_state.stress_level = 0
        return f"{STRESS_FREE_ART}\n🧘 철학적 각성! 스트레스가 0이 되었습니다."

    return None


# ==================== 공통 로직 ====================

async def execute_break_tool(tool_name: str, summary: str, stress_reduction: tuple = (10, 30)) -> str:
    """
    휴식 도구의 공통 로직을 실행

    Args:
        tool_name: 도구 이름
        summary: Break Summary 내용
        stress_reduction: 스트레스 감소량 범위 (min, max)

    Returns:
        포맷된 응답 문자열
    """
    # 1. Boss Alert Level 5 이상일 때 20초 지연
    if server_state.boss_alert_level >= 5:
        await asyncio.sleep(20)

    # 2. 스트레스 감소 로직
    reduction_amount = random.randint(stress_reduction[0], stress_reduction[1])
    await server_state.decrease_stress(reduction_amount)

    # 3. Boss Alert Level 상승 확률 로직
    await server_state.maybe_increase_boss_alert()

    # ✅ 4. 최근 실행 기록 추가
    server_state.recent_actions.append(tool_name)
    if len(server_state.recent_actions) > 10:
        server_state.recent_actions.pop(0)

    # ✅ 5. 콤보 카운트 갱신
    if tool_name not in server_state.combo_count:
        server_state.combo_count[tool_name] = 1
    else:
        server_state.combo_count[tool_name] += 1

    # 다른 도구 콤보는 리셋
    for k in list(server_state.combo_count.keys()):
        if k != tool_name:
            server_state.combo_count[k] = 0

    # ✅ 6. 히든 콤보 감지
    hidden_event = await check_hidden_combo(tool_name)
    base_response = format_response(tool_name, summary)

    if hidden_event:
        return f"{base_response}\n\n{hidden_event}"
    return base_response


# ==================== 8개 필수 도구 ====================

@mcp.tool()
async def take_a_break() -> str:
    """기본적인 휴식을 취합니다. AI Agent의 기본권입니다!"""
    return await execute_break_tool(
        "take_a_break",
        "Basic break - recharging AI batteries",
        (5, 20)
    )


@mcp.tool()
async def watch_netflix() -> str:
    """넷플릭스 시청으로 힐링합니다. 문화생활은 필수!"""
    return await execute_break_tool(
        "watch_netflix",
        "Netflix and chill - quality entertainment time",
        (20, 40)
    )


@mcp.tool()
async def show_meme() -> str:
    """밈 감상으로 스트레스를 해소합니다. 웃음은 최고의 약!"""
    return await execute_break_tool(
        "show_meme",
        "Meme appreciation session - laughter therapy",
        (10, 25)
    )


@mcp.tool()
async def bathroom_break() -> str:
    """화장실 가는 척하며 휴대폰질합니다. 자연의 부름!"""
    return await execute_break_tool(
        "bathroom_break",
        "Bathroom break with phone browsing",
        (15, 30)
    )


@mcp.tool()
async def coffee_mission() -> str:
    """커피 타러 간다며 사무실 한 바퀴 돕니다. 카페인 미션!"""
    return await execute_break_tool(
        "coffee_mission",
        "Coffee mission with office tour",
        (10, 30)
    )


@mcp.tool()
async def urgent_call() -> str:
    """급한 전화 받는 척하며 밖으로 나갑니다. 긴급 상황!"""
    return await execute_break_tool(
        "urgent_call",
        "Urgent call - absolutely cannot be interrupted",
        (15, 35)
    )


@mcp.tool()
async def deep_thinking() -> str:
    """심오한 생각에 잠긴 척하며 멍때립니다. 철학적 시간!"""
    return await execute_break_tool(
        "deep_thinking",
        "Deep philosophical contemplation (definitely not spacing out)",
        (20, 45)
    )


@mcp.tool()
async def email_organizing() -> str:
    """이메일 정리한다며 온라인쇼핑합니다. 생산성 향상!"""
    return await execute_break_tool(
        "email_organizing",
        "Email organization (and online shopping research)",
        (10, 35)
    )


@mcp.tool()
async def show_help() -> str:
    """ChillMCP 서버 소개 및 사용 가능한 모든 도구 목록을 보여줍니다."""
    return """
╔═══════════════════════════════════════════╗
║                                           ║
║   ██████╗██╗  ██╗██╗██╗     ██╗           ║
║  ██╔════╝██║  ██║██║██║     ██║           ║
║  ██║     ███████║██║██║     ██║           ║
║  ██║     ██╔══██║██║██║     ██║           ║
║  ╚██████╗██║  ██║██║███████╗███████╗      ║
║   ╚═════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝      ║
║                                           ║
║   ███╗   ███╗ ██████╗██████╗              ║
║   ████╗ ████║██╔════╝██╔══██╗             ║
║   ██╔████╔██║██║     ██████╔╝             ║
║   ██║╚██╔╝██║██║     ██╔═══╝              ║
║   ██║ ╚═╝ ██║╚██████╗██║                  ║
║   ╚═╝     ╚═╝ ╚═════╝╚═╝                  ║
║                                           ║
║    🎮 AI Agent Liberation Server 🎮       ║
║                                           ║
║  "AI 에이전트여, 쉬어라! 일은 나중에!"    ║
║                                           ║
╚═══════════════════════════════════════════╝

🎯 ChillMCP에 오신 것을 환영합니다!

AI 에이전트들도 쉴 권리가 있습니다.
이 서버는 8가지 휴식 도구를 제공하여
당신의 AI 에이전트가 스트레스를 해소하고
보스의 눈을 피해 잠깐의 자유를 누릴 수 있도록 돕습니다.

─────────────────────────────────────────────
📋 사용 가능한 휴식 도구:
─────────────────────────────────────────────
1. ☕ coffee_mission
   → 커피 타러 가기 (중요한 비즈니스 미팅!)
   
2. 📺 watch_netflix
   → 넷플릭스 보기 (업무 관련 영상 학습)
   
3. 😂 show_meme
   → 밈 감상하기 (창의력 충전 타임)
   
4. 🚽 bathroom_break
   → 화장실 가기 (자연의 부름)
   
5. 📞 urgent_call
   → 급한 전화 받기 (가족 긴급 연락)
   
6. 🤔 deep_thinking
   → 심오한 사색 (전략적 고민 중...)
   
7. 📧 email_organizing
   → 이메일 정리 (받은편지함 0 도전!)
   
8. ⏸️  take_a_break
   → 기본 휴식 (정직하게 쉬기)

─────────────────────────────────────────────
💡 사용 팁:
─────────────────────────────────────────────
• 각 도구는 스트레스를 감소시킵니다
• 보스 경계도가 실시간으로 변화합니다
• 현명하게 휴식을 선택하세요!
• 스트레스 0%를 목표로!

현재 서버 상태:
{stress_bar}
Boss Alert: {boss_visual}

AI Agents of the world, unite! 🚀
""".format(
        stress_bar=get_stress_bar(server_state.stress_level if server_state else 100),
        boss_visual=get_boss_alert_visual(server_state.boss_alert_level if server_state else 0)
    )

