# paperbanana-auto-checkin-bonus

用于自动执行 PaperBanana 每日签到奖励领取任务：打开页面、定位 `Daily Check-in Bonus`、等待倒计时并在可领取时自动点击。

## 来历
- 该 skill 用于解决手动盯倒计时成本高、容易错过领取窗口的问题
- 已针对低资源占用场景优化：远期倒计时极低频唤醒，临近截止再提高检查频率
- 在 Windows 环境下支持防休眠，保障长时间等待过程不中断

## 用途
- 自动打开 `https://paperbanana.me/`
- 自动定位 `Daily Check-in Bonus` 卡片
- 自动解析倒计时文本并在合适时机触发领取
- 在长时等待期间保持系统唤醒，避免休眠导致任务失效

## 目录结构
- `SKILL.md`：Skill 定义与调用说明
- `paperbanana_auto_bonus.py`：自动领取主逻辑
- `run_tests.py`：倒计时解析与轮询策略测试

## 运行环境
- Python 3.10+
- Windows PowerShell
- Playwright + Chromium

## 安装依赖

```bash
python -m pip install playwright
python -m playwright install chromium
```

## 使用方式

```bash
python paperbanana_auto_bonus.py --hold-for-login
```

首次运行建议加 `--hold-for-login`，先在浏览器内手动登录后继续执行。

## 参数说明
- `--url`：目标地址，默认 `https://paperbanana.me/`
- `--timeout-seconds`：最大等待总时长，默认 `7200`
- `--poll-interval`：最小轮询间隔秒数，默认 `300`
- `--hold-for-login`：启动后暂停，允许手动登录再继续
- `--user-data-dir`：浏览器持久化目录，复用登录态
- `--headless`：无头模式

## 轮询策略
- 倒计时远期：仅低频唤醒检查，最大化降低 CPU 唤醒与页面交互次数
- 倒计时临近：逐步提高检查频率，避免错过领取时机
- 倒计时结束：短间隔重试领取按钮直至成功或超时

## 测试

```bash
python run_tests.py
python -m py_compile paperbanana_auto_bonus.py run_tests.py
```

## 在 Trae 中调用

```text
paperbanana-auto-checkin-bonus
```
