# PAX User Simulator

基于 Python + Selenium 的用户注册与行为模拟框架，目标站点：[uwin UAT](https://uat02.uwingame.fun/en/?modal=register&tab=account)。

## 功能

- 自动打开注册弹窗并填写表单（Email / Username / Password / Referral Code）
- 随机生成测试用户数据（Faker）
- 模拟真实用户浏览行为（滚动、切换 Tab、点击安全按钮）
- 支持 Chrome / Edge，可配置 headless 模式
- 注册结果写入 `artifacts/users.jsonl`，失败时自动截图

## 环境要求

- Python 3.10+
- Chrome 或 Edge 浏览器

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 复制环境变量（可选）
copy .env.example .env

# 3. 注册单个用户
python main.py register

# 4. 仅模拟浏览行为
python main.py simulate

# 5. 注册 + 行为模拟
python main.py full

# 6. 检查页面元素（调试选择器）
python main.py inspect
```

## 常用参数

```bash
# 无头模式
python main.py register --headless

# 自定义账号
python main.py register --email test@gmail.com --username myuser --password "Pass123!@#"

# 调试日志
python main.py full -v
```

## 项目结构

```
pax-user-simulator/
├── config/settings.yaml      # 站点 URL、浏览器、选择器配置
├── src/pax_simulator/
│   ├── config.py             # 配置加载
│   ├── driver.py             # WebDriver 工厂
│   ├── runner.py             # 任务编排
│   ├── pages/                # Page Object
│   │   ├── base.py
│   │   ├── register.py
│   │   └── home.py
│   ├── actions/
│   │   └── user_behavior.py  # 行为模拟
│   └── utils/
├── main.py                   # CLI 入口
└── artifacts/                # 输出目录（自动生成）
```

## 配置说明

编辑 `config/settings.yaml` 或 `.env`：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `BASE_URL` | 站点根地址 | `https://uat02.uwingame.fun` |
| `HEADLESS` | 无头浏览器 | `false` |
| `REFERRAL_CODE` | 邀请码 | 空 |
| `SIMULATION_DURATION_SEC` | 行为模拟时长（秒） | `60` |

## 注册表单字段（已探测）

| 字段 | 选择器 |
|------|--------|
| Email | `#email` |
| Username | `#username` |
| Password | `#password` |
| Referral Code | `#referralCode` |
| 提交按钮 | `button.btn.van-button--primary` |

## 扩展建议

- 在 `pages/` 下新增 `login.py` 实现登录流程
- 在 `actions/user_behavior.py` 增加游戏点击、充值页浏览等场景
- 对接 pytest 做批量注册回归测试
- 若站点增加验证码，可在 `RegisterPage.submit()` 前接入打码或人工介入

## 注意事项

- 仅用于 UAT / 测试环境，请勿对生产环境批量注册
- 首次运行会自动下载匹配的 WebDriver
- 若页面结构变更，运行 `python main.py inspect` 更新选择器
