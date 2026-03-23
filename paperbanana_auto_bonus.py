import argparse
import ctypes
import re
import time
from pathlib import Path
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.sync_api import Locator, Page
else:
    Locator = Any
    Page = Any


COUNTDOWN_HMS_PATTERN = re.compile(r"(?<!\d)(\d{1,2}):([0-5]\d):([0-5]\d)(?!\d)")
COUNTDOWN_MS_PATTERN = re.compile(r"(?<!\d)([0-5]?\d):([0-5]\d)(?!\d)")
BUTTON_KEYWORDS = ["Claim", "Check in", "Receive", "Bonus", "领取", "签到"]
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001


def parse_countdown_seconds(text: str) -> Optional[int]:
    if not text:
        return None
    normalized = text.replace("：", ":")
    hms_match = COUNTDOWN_HMS_PATTERN.search(normalized)
    if hms_match:
        hours = int(hms_match.group(1))
        minutes = int(hms_match.group(2))
        seconds = int(hms_match.group(3))
        return hours * 3600 + minutes * 60 + seconds
    ms_match = COUNTDOWN_MS_PATTERN.search(normalized)
    if ms_match:
        minutes = int(ms_match.group(1))
        seconds = int(ms_match.group(2))
        return minutes * 60 + seconds
    return None


def locate_bonus_card(page: Page, timeout_ms: int) -> Locator:
    title = page.get_by_text("Daily Check-in Bonus", exact=False).first
    title.wait_for(timeout=timeout_ms)
    card = title.locator("xpath=ancestor::*[self::section or self::article or self::div][1]")
    if card.count() == 0:
        return title.locator("xpath=..")
    return card


def find_claim_button(card: Locator) -> Optional[Locator]:
    for keyword in BUTTON_KEYWORDS:
        button = card.get_by_role("button", name=re.compile(keyword, re.IGNORECASE)).first
        if button.count() > 0 and button.is_visible():
            return button
    for keyword in BUTTON_KEYWORDS:
        button = card.locator(f"button:has-text('{keyword}')").first
        if button.count() > 0 and button.is_visible():
            return button
    return None


def try_claim_bonus(card: Locator) -> bool:
    button = find_claim_button(card)
    if button is None:
        return False
    if not button.is_enabled():
        return False
    button.click()
    return True


def set_system_keep_awake(enable: bool) -> None:
    if not hasattr(ctypes, "windll"):
        return
    flags = ES_CONTINUOUS | ES_SYSTEM_REQUIRED if enable else ES_CONTINUOUS
    ctypes.windll.kernel32.SetThreadExecutionState(flags)


def compute_sleep_seconds(remain_seconds: int, poll_interval: float) -> float:
    base_interval = max(poll_interval, 300.0)
    if remain_seconds > 900:
        return max(base_interval, remain_seconds - 600.0)
    if remain_seconds > 300:
        return max(base_interval, remain_seconds - 180.0)
    if remain_seconds > 120:
        return max(60.0, min(base_interval, 120.0))
    if remain_seconds > 30:
        return max(15.0, min(base_interval, 30.0))
    if remain_seconds > 10:
        return max(5.0, min(base_interval, 10.0))
    return max(2.0, min(base_interval, 3.0))


def monitor_and_claim(page: Page, timeout_seconds: int, poll_interval: float) -> int:
    started = time.time()
    card = locate_bonus_card(page, timeout_ms=30000)
    set_system_keep_awake(True)
    try:
        while True:
            elapsed = time.time() - started
            if elapsed > timeout_seconds:
                print("超时：在指定时间内未完成领取。")
                return 1
            card_text = card.inner_text(timeout=5000)
            remain_seconds = parse_countdown_seconds(card_text)
            if remain_seconds is None:
                if try_claim_bonus(card):
                    print("已执行领取点击。")
                    page.wait_for_timeout(1500)
                    print("领取流程完成。")
                    return 0
                print("未识别到倒计时，按钮暂不可领取，进入低频等待。")
                unknown_wait = max(poll_interval, 600.0)
                page.wait_for_timeout(int(unknown_wait * 1000))
                continue
            if remain_seconds <= 0:
                if try_claim_bonus(card):
                    print("倒计时结束，已点击领取。")
                    page.wait_for_timeout(1500)
                    print("领取流程完成。")
                    return 0
                print("倒计时结束但按钮未就绪，继续轮询。")
                page.wait_for_timeout(int(max(3.0, min(5.0, poll_interval)) * 1000))
                continue
            sleep_seconds = min(compute_sleep_seconds(remain_seconds, poll_interval), float(remain_seconds))
            
            def fmt(sec):
                h = int(sec // 3600)
                m = int((sec % 3600) // 60)
                s = int(sec % 60)
                return f"{h}时{m}分{s}秒"
            print(f"倒计时剩余 {fmt(remain_seconds)}，等待 {fmt(sleep_seconds)}后重试。")
            page.wait_for_timeout(int(sleep_seconds * 1000))
    finally:
        set_system_keep_awake(False)


def build_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="https://paperbanana.me/")
    parser.add_argument("--timeout-seconds", type=int, default=7200)
    parser.add_argument("--poll-interval", type=float, default=300.0)
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--hold-for-login", action="store_true")
    parser.add_argument("--user-data-dir", default="")
    return parser.parse_args()


def main() -> int:
    args = build_args()
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        user_data_dir = args.user_data_dir.strip()
        if user_data_dir:
            context = playwright.chromium.launch_persistent_context(
                user_data_dir=str(Path(user_data_dir).resolve()),
                headless=args.headless,
            )
            page = context.pages[0] if context.pages else context.new_page()
        else:
            browser = playwright.chromium.launch(headless=args.headless)
            context = browser.new_context()
            page = context.new_page()
        page.goto(args.url, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)
        if args.hold_for_login:
            input("请在浏览器中完成登录后按回车继续...")
        code = monitor_and_claim(
            page=page,
            timeout_seconds=args.timeout_seconds,
            poll_interval=args.poll_interval,
        )
        context.close()
    return code


if __name__ == "__main__":
    raise SystemExit(main())
