# 币安账户监控系统

<p align="center">
  <a href="./README.md">English</a> | 
  <a href="#readme">简体中文</a>
</p>

该项目用于监控币安合约主账户和子账户的仓位变化和资产情况，并通过飞书进行通知。系统会实时监控账户仓位变化，在发生开仓、平仓等操作时立即通知，并在每天固定时间发送账户总资产报告。

## 功能特性

- 支持主账户和子账户同时监控
- 实时监控币安合约账户仓位变化
- 自动识别开仓和平仓操作
- 每日定时发送账户总资产报告
- 通过飞书机器人发送通知
- 支持自定义监控间隔和报告时间
- 异常自动重试和错误通知
- 支持持仓时长统计
- 支持收益率计算和展示
- 按盈亏排序的持仓展示
- 多账户资产汇总统计

## 通知功能详解

### 仓位变化通知

- 新开仓通知：

  - 账户类型（主账户/子账户）
  - 币种和交易对
  - 开仓方向（做多/做空）
  - 开仓价格
  - 开仓数量
  - 使用保证金
  - 开仓时间（美东时间）

- 平仓通知：
  - 账户类型（主账户/子账户）
  - 币种和交易对
  - 持仓方向
  - 开仓价格和平仓价格
  - 持仓数量
  - 盈亏金额和收益率
  - 持仓时长（天/小时/分钟）
  - 平仓时间（美东时间）

### 每日账户报告

- 账户概览：
  - 主账户总资产（USDT）
  - 子账户总资产（USDT）
  - 账户组合总资产
  - 各账户可用余额
  - 各账户占用保证金
  - 各账户未实现盈亏
- 持仓明细（按账户和盈亏排序）：
  - 账户类型
  - 交易对
  - 持仓方向
  - 未实现盈亏
  - 收益率百分比

## 安装要求

- Python 3.8+
- ccxt >= 2.0.0
- requests >= 2.26.0
- schedule >= 1.1.0
- python-dotenv >= 0.19.0

## 安装步骤

如果部署在服务器：

```bash
# 下载 miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

# 添加执行权限
chmod +x Miniconda3-latest-Linux-x86_64.sh

# 安装 miniconda
./Miniconda3-latest-Linux-x86_64.sh

# 更新 bashrc
source ~/.bashrc

# 安装 screen（如果未安装）
yum install screen -y

# 创建 screen 会话
screen -S binance_monitor

# 退出 screen 会话
# ctrl + a + d

# 重连会话
screen -r binance_monitor
```

1. 克隆项目到本地
2. 创建虚拟环境

```bash
conda create -n binance_monitor
conda activate binance_monitor
conda install pip

# 查看环境
# conda env list

# 退出环境
# conda deactivate

# 删除环境
# conda env remove -n binance_monitor
```

3. 安装依赖：

```bash
pip install -r requirements.txt
```

3. 配置环境变量：
   - 复制 `.env.example` 为 `.env`
   - 填入以下配置：
     - BINANCE_API_KEY: 主账户币安 API Key
     - BINANCE_API_SECRET: 主账户币安 API Secret
     - SUB_ACCOUNT_API_KEY: 子账户币安 API Key
     - SUB_ACCOUNT_API_SECRET: 子账户币安 API Secret
     - FEISHU_WEBHOOK_URL: 飞书机器人 Webhook URL
     - NOTIFY_INTERVAL: 监控间隔（秒）
     - DAILY_REPORT_TIME: 每日报告时间（格式：HH:MM）
     - NOTIFICATION_TYPE: 通知渠道（FEISHU/TELEGRAM）
     - TELEGRAM_BOT_TOKEN: Telegram 机器人 token
     - TELEGRAM_CHAT_ID: Telegram 聊天 ID

## 使用方法

1. 确保配置正确后，运行主程序：

```bash
python main.py
```

2. 程序启动后会：
   - 立即发送一次账户报告
   - 按照设定的间隔监控仓位变化
   - 在每天指定时间发送日报

## 通知服务

系统支持多种通知渠道：

### 飞书通知

- 通过飞书机器人 Webhook 发送通知
- 支持富文本格式
- 实时仓位变动通知
- 每日账户报告

### Telegram 通知

- 通过 Telegram Bot 发送通知
- 支持实时查询功能
- 支持命令交互
- 支持消息格式化

配置方式：

1. 用户需要在 .env 文件中配置：

   - TELEGRAM_BOT_TOKEN：从 @BotFather 获取的机器人 token
   - TELEGRAM_CHAT_ID：目标聊天 ID
   - NOTIFICATION_TYPE：选择 'FEISHU' 或 'TELEGRAM'

2. 当配置为 TELEGRAM 时：

   - 所有通知将通过 Telegram 机器人发送
   - 向机器人发送"查询"消息时，将立即返回当前账户资产报告（不含持仓信息）

## 系统特性

### 时区处理

- 所有时间显示均采用美东时间（ET）
- 自动处理夏令时转换

### 错误处理机制

- API 调用失败自动重试
- 网络异常自动重连
- 关键错误日志记录
- 异常情况实时通知
- 调度器异常自动恢复

### 性能优化

- 使用 ccxt 库确保 API 调用限频
- 合理的监控间隔设置
- 高效的数据结构存储历史仓位
- 多账户并发监控优化

### 连接监控功能

- 自动检测系统连接状态
- 断联时立即发送通知
- 自动重连机制
- 重连成功后发送恢复通知
- 多次重连失败发送警告
- 可配置重连间隔和最大重试次数

## 开发计划

### 近期计划

- [ ] 支持更多子账户监控
- [ ] 添加图表展示功能
- [ ] 支持自定义通知模板
- [ ] 添加账户组合分析功能
- [ ] 添加更多通知渠道（如企业微信、Discord 等）

### 待优化项目

- [ ] 添加单元测试
- [ ] 优化错误重试机制
- [ ] 增加数据持久化存储
- [ ] 添加 Web 管理界面
- [ ] 优化多账户并发监控

## 许可证

MIT License
