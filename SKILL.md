---
name: "paperbanana-auto-checkin-bonus"
description: "自动执行 PaperBanana Daily Check-in Bonus 领取。用户要求自动签到、等待倒计时并点击领取时调用。"
---

# PaperBanana Auto Check-in Bonus

## 适用场景
- 用户希望自动打开 `https://paperbanana.me/`
- 用户希望自动定位 `Daily Check-in Bonus`
- 用户希望倒计时结束后自动点击领取奖励

## 交付文件
- `paperbanana_auto_bonus.py`：自动打开页面、定位奖励卡片、轮询倒计时并自动点击领取
- `run_tests.py`：核心倒计时解析逻辑测试

## 使用方式
在该目录执行：

```bash
python -m pip install playwright
python -m playwright install chromium
python paperbanana_auto_bonus.py --hold-for-login
```

## 参数说明
- `--url`：目标地址，默认 `https://paperbanana.me/`
- `--timeout-seconds`：最大等待总时长，默认 `7200`
- `--poll-interval`：最小轮询间隔秒数，默认 `300`
- `--hold-for-login`：启动后暂停，允许手动登录再继续
- `--user-data-dir`：浏览器持久化目录，便于复用登录态
- `--headless`：无头模式，默认关闭

## 执行策略
1. 打开 PaperBanana 页面并等待主内容出现
2. 定位包含 `Daily Check-in Bonus` 的卡片区域
3. 读取卡片文本中的倒计时
4. 倒计时远期仅保活等待，接近截止时才进入密集轮询
5. 等待期间保持系统唤醒，避免休眠导致错过领取
6. 倒计时结束后自动点击领取按钮并输出结果
