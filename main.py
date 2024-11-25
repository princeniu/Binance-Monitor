from binance_client import BinanceClient
from services.feishu_service import FeishuNotifier
from scheduler import TaskScheduler
from config import (
    NOTIFY_INTERVAL, DAILY_REPORT_TIME,
    MAIN_ACCOUNT_CONFIG, SUB_ACCOUNT_CONFIG
)
from services.telegram_service import TelegramService
import os
import asyncio
import threading

def main():
    # 创建主账户和子账户的客户端
    main_account = BinanceClient(MAIN_ACCOUNT_CONFIG.copy())
    sub_account = BinanceClient(SUB_ACCOUNT_CONFIG.copy())
    accounts = [main_account, sub_account]
    
    # 初始化通知服务
    notification_type = os.getenv('NOTIFICATION_TYPE')
    if notification_type == 'TELEGRAM':
        notifier = TelegramService()
    else:
        notifier = FeishuNotifier()

    # 创建调度器
    scheduler = TaskScheduler()

    def check_positions():
        """检查所有账户的仓位变化并发送通知"""
        for account in accounts:
            try:
                changes = account.check_position_changes()
                if changes['new_positions'] or changes['closed_positions']:
                    message = notifier.format_position_message(changes, account.exchange)
                    notifier.send_message(message)
            except Exception as e:
                print(f"{account.account_name} 检查仓位失败: {str(e)}")

    def send_daily_report():
        """发送所有账户的每日报告"""
        try:
            # 收集所有账户的信息
            all_balances = []
            all_positions = []
            
            for account in accounts:
                balance = account.get_account_balance()
                positions = account.get_positions()
                all_balances.append(balance)
                all_positions.extend(positions)
            
            # 格式化并发送报告
            message = notifier.format_daily_report(all_balances, all_positions)
            notifier.send_message(message)
        except Exception as e:
            print(f"发送每日报告失败: {str(e)}")

    async def run_telegram_handler():
        """运行Telegram消息处理器"""
        if notification_type == 'TELEGRAM':
            await notifier.start_message_handler(accounts)

    def start_telegram_handler():
        """在新线程中启动Telegram处理器"""
        if notification_type == 'TELEGRAM':
            def run_async_handler():
                asyncio.run(run_telegram_handler())
            
            telegram_thread = threading.Thread(target=run_async_handler, daemon=True)
            telegram_thread.start()

    # 添加定时任务
    scheduler.add_interval_task(NOTIFY_INTERVAL, check_positions)
    scheduler.add_daily_task(DAILY_REPORT_TIME, send_daily_report)

    # 启动时先执行一次每日报告
    send_daily_report()

    # 如果使用Telegram，启动消息处理器
    if notification_type == 'TELEGRAM':
        start_telegram_handler()

    print(f"监控程序已启动...")
    print(f"- 仓位监控间隔: {NOTIFY_INTERVAL}秒")
    print(f"- 每日报告时间: {DAILY_REPORT_TIME}")
    print(f"- 通知方式: {notification_type}")
    print("按 Ctrl+C 可安全退出程序")

    # 运行调度器
    scheduler.run()

if __name__ == "__main__":
    main() 