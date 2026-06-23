# PAX User Simulator 架构说明

本项目采用典型的 Selenium 自动化结构，按功能分离为配置、入口、页面对象、行为和工具模块。

## 项目结构

```
.
├── .env.example
├── README.md
├── config/settings.yaml
├── main.py
├── requirements.txt
├── scripts/inspect_page.py
├── src/pax_simulator/
│   ├── config.py
│   ├── driver.py
│   ├── runner.py
│   ├── pages/
│   │   ├── base.py
│   │   ├── home.py
│   │   └── register.py
│   ├── actions/
│   │   └── user_behavior.py
│   └── utils/
│       ├── inspect.py
│       ├── random_data.py
│       └── waits.py
└── artifacts/
```

## 模块职责

### `main.py`

- CLI 入口
- 解析命令行参数
- 调用 `runner.py` 执行不同任务模式

### `config/settings.yaml`

- 存放基础站点地址、浏览器设置、选择器、模拟时长等配置
- 与 `.env` 配合，可通过环境变量覆盖配置值

### `src/pax_simulator/config.py`

- 加载 YAML 配置文件
- 读取环境变量
- 提供统一配置对象给全局模块使用

### `src/pax_simulator/driver.py`

- 初始化 Selenium WebDriver
- 管理 Chrome / Edge 浏览器选项
- 支持无头模式和常规浏览模式

### `src/pax_simulator/runner.py`

- 任务编排入口
- 根据命令选择注册、模拟、或完整流程
- 管理浏览器生命周期和异常处理

### `src/pax_simulator/pages/base.py`

- 页面对象基类
- 提供通用等待与元素定位方法

### `src/pax_simulator/pages/home.py`

- 封装首页交互逻辑
- 包括打开注册弹窗、页面导航、检查页面状态等

### `src/pax_simulator/pages/register.py`

- 封装注册页面/弹窗交互
- 填写 Email、用户名、密码、Referral Code
- 提交注册表单并处理结果

### `src/pax_simulator/actions/user_behavior.py`

- 模拟真实用户行为
- 包括滚动、切换 Tab、点击安全按钮等操作
- 用于验证页面互动流程和停留时长

### `src/pax_simulator/utils/random_data.py`

- 生成随机测试用户数据
- 支持 Email、用户名、密码等字段生成规则

### `src/pax_simulator/utils/waits.py`

- 封装显式等待逻辑
- 提高稳定性，避免硬编码 sleep

### `src/pax_simulator/utils/inspect.py`

- 页面元素检查工具
- 用于 `inspect` 模式调试选择器和页面状态

### `scripts/inspect_page.py`

- 独立脚本，用于快速检查页面元素和定位器
- 常用于维护选择器时的手工调试

### `artifacts/`

- 输出目录
- 保存注册结果、日志、失败截图等运行产物

## 知识库用途

这些文档帮助团队成员快速理解项目目标、使用场景与内部模块分工，便于：

- 加速新成员上手
- 支持自动化测试方案评审
- 作为后续扩展与维护的参考
- 在远程仓库中形成可查阅知识库内容
