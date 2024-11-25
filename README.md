# Binance Account Monitoring System

<p align="center">
  <a href="#readme">English</a> | 
  <a href="./README_CN.md">简体中文</a>
</p>

This project is used to monitor position changes and asset status of Binance futures main account and sub-accounts, with notifications through Feishu or Telegram. The system monitors account position changes in real-time, sends immediate notifications for opening and closing positions, and sends daily account total asset reports at fixed times.

## Features

- Supports simultaneous monitoring of main account and sub-accounts
- Real-time monitoring of Binance futures account position changes
- Automatic identification of opening and closing positions
- Daily scheduled account total asset reports
- Support daily report auto storage
- Notifications through Feishu or Telegram
- Support Telegram query function
- Customizable monitoring intervals and report times
- Automatic retry and error notifications
- Support for position duration statistics
- Support for profit/loss calculation and display
- Position display sorted by profit/loss
- Multi-account asset summary statistics

## Notification Features Explained

### Position Change Notifications

- New Position Notifications:

  - Account type (Main Account/Sub Account)
  - Currency and trading pair
  - Position direction (Long/Short)
  - Opening price
  - Position size
  - Margin used
  - Opening time (Eastern Time)

- Closing Position Notifications:
  - Account type (Main Account/Sub Account)
  - Currency and trading pair
  - Position direction
  - Opening and closing prices
  - Position size
  - Profit/loss amount and return rate
  - Position duration (days/hours/minutes)
  - Closing time (Eastern Time)

### Daily Account Report

- Account Overview:
  - Main account total assets (USDT)
  - Sub-account total assets (USDT)
  - Account portfolio total assets
  - Available balance for each account
  - Margin occupied for each account
  - Unrealized PnL for each account
- Position Details (sorted by account and PnL):
  - Account type
  - Trading pair
  - Position direction
  - Unrealized PnL
  - Return rate percentage

## Installation Requirements

- Python 3.8+
- ccxt >= 2.0.0
- requests >= 2.26.0
- schedule >= 1.1.0
- python-dotenv >= 0.19.0
- pytz >= 2021.1
- python-telegram-bot==20.8

## Installation Steps

If deploying on a server:

```bash
# Download miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

# Add execution permissions
chmod +x Miniconda3-latest-Linux-x86_64.sh

# Install miniconda
./Miniconda3-latest-Linux-x86_64.sh

# Update bashrc
source ~/.bashrc

# Install screen (if not installed)
yum install screen -y

# Create screen session
screen -S binance_monitor

# Exit screen session
# ctrl + a + d

# Reconnect session
screen -r binance_monitor
```

1. Clone project locally
2. Create virtual environment

```bash
conda create -n binance_monitor
conda activate binance_monitor
conda install pip

# View environments
# conda env list

# Exit environment
# conda deactivate

# Remove environment
# conda env remove -n binance_monitor
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Fill in the following configurations:
     - BINANCE_API_KEY: Main account Binance API Key
     - BINANCE_API_SECRET: Main account Binance API Secret
     - SUB_ACCOUNT_API_KEY: Sub-account Binance API Key
     - SUB_ACCOUNT_API_SECRET: Sub-account Binance API Secret
     - FEISHU_WEBHOOK_URL: Feishu bot Webhook URL
     - NOTIFY_INTERVAL: Monitoring interval (seconds)
     - DAILY_REPORT_TIME: Daily report time (format: HH:MM)
     - NOTIFICATION_TYPE: Notification channel (FEISHU/TELEGRAM)
     - TELEGRAM_BOT_TOKEN: Telegram bot token
     - TELEGRAM_CHAT_ID: Telegram chat ID

## Usage

1. After ensuring correct configuration, run the main program:

```bash
python main.py
```

2. After program startup:
   - Immediately sends an account report
   - Monitors position changes according to set interval
   - Sends daily report at specified time

## Notification Services

The system supports multiple notification channels:

### Feishu Notifications

- Send notifications through Feishu bot Webhook
- Support rich text format
- Real-time position change notifications
- Daily account reports

### Telegram Notifications

- Send notifications through Telegram Bot
- Support real-time query functionality
- Support command interaction
- Support message formatting

Configuration method:

1. Users need to configure in .env file:

   - TELEGRAM_BOT_TOKEN: Bot token obtained from @BotFather
   - TELEGRAM_CHAT_ID: Target chat ID
   - NOTIFICATION_TYPE: Choose 'FEISHU' or 'TELEGRAM'

2. When configured as TELEGRAM:
   - All notifications will be sent through Telegram bot
   - Sending "query" message to the bot will immediately return current account asset report (without position information)

## System Features

### Timezone Handling

- All time displays use Eastern Time (ET)
- Automatic daylight saving time conversion

### Error Handling Mechanism

- Automatic retry for API call failures
- Automatic reconnection for network exceptions
- Critical error logging
- Real-time notification for exceptions
- Scheduler exception auto-recovery

### Performance Optimization

- Use ccxt library to ensure API call rate limits
- Reasonable monitoring interval settings
- Efficient data structures for storing historical positions
- Multi-account concurrent monitoring optimization

### Connection Monitoring Features

- Automatic system connection status detection
- Immediate notification on disconnection
- Automatic reconnection mechanism
- Recovery notification after successful reconnection
- Warning for multiple reconnection failures
- Configurable reconnection interval and maximum retry attempts

## Development Plan

### Near-term Plans

- [ ] Support more sub-account monitoring
- [ ] Add chart display functionality
- [ ] Support custom notification templates
- [ ] Add account portfolio analysis functionality
- [ ] Add more notification channels (like WeCom, Discord, etc.)

### Items to Optimize

- [ ] Add unit tests
- [ ] Optimize error retry mechanism
- [ ] Add data persistence storage
- [ ] Add Web management interface
- [ ] Optimize multi-account concurrent monitoring

## License

MIT License
