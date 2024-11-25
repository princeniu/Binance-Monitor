import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 主账户API配置
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET')

# 子账户API配置
SUB_ACCOUNT_API_KEY = os.getenv('SUB_ACCOUNT_API_KEY')
SUB_ACCOUNT_API_SECRET = os.getenv('SUB_ACCOUNT_API_SECRET')

# 飞书配置
FEISHU_WEBHOOK_URL = os.getenv('FEISHU_WEBHOOK_URL')

# 监控配置
NOTIFY_INTERVAL = int(os.getenv('NOTIFY_INTERVAL'))
DAILY_REPORT_TIME = os.getenv('DAILY_REPORT_TIME')

# 主账户配置
MAIN_ACCOUNT_CONFIG = {
    'name': '主账户',
    'apiKey': BINANCE_API_KEY,
    'secret': BINANCE_API_SECRET,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'
    }
}

# 子账户配置
SUB_ACCOUNT_CONFIG = {
    'name': '子账户',
    'apiKey': SUB_ACCOUNT_API_KEY,
    'secret': SUB_ACCOUNT_API_SECRET,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'
    }
} 