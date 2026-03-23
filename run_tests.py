from paperbanana_auto_bonus import compute_sleep_seconds, parse_countdown_seconds


def run() -> int:
    cases = [
        ("Daily Check-in Bonus 01:02:03", 3723),
        ("剩余时间 00:10:00", 600),
        ("claim in 9:08", 548),
        ("Countdown：00:00:20", 20),
        ("No timer text", None),
    ]
    passed = 0
    for idx, (text, expected) in enumerate(cases, start=1):
        got = parse_countdown_seconds(text)
        ok = got == expected
        if ok:
            passed += 1
        print(f"[{idx}] ok={ok} expected={expected} got={got}")
    base = len(cases)
    schedule_cases = [
        ((10800, 300.0), 10200.0),
        ((1200, 300.0), 600.0),
        ((240, 300.0), 120.0),
        ((90, 300.0), 30.0),
        ((20, 300.0), 10.0),
        ((5, 300.0), 3.0),
    ]
    for idx, (args, expected) in enumerate(schedule_cases, start=base + 1):
        got = compute_sleep_seconds(*args)
        ok = got == expected
        if ok:
            passed += 1
        print(f"[{idx}] ok={ok} expected={expected} got={got}")
    total = base + len(schedule_cases)
    print(f"passed={passed}/{total}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(run())
