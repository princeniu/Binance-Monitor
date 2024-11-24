from binance_client import BinanceClient
from notification import FeishuNotifier
from scheduler import TaskScheduler
from config import (
    NOTIFY_INTERVAL, DAILY_REPORT_TIME,
    MAIN_ACCOUNT_CONFIG, SUB_ACCOUNT_CONFIG
)

def main():
    # 创建主账户和子账户的客户端
    main_account = BinanceClient(MAIN_ACCOUNT_CONFIG.copy())
    sub_account = BinanceClient(SUB_ACCOUNT_CONFIG.copy())
    accounts = [main_account, sub_account]
    
    notifier = FeishuNotifier()
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

    # 添加定时任务
    scheduler.add_interval_task(NOTIFY_INTERVAL, check_positions)
    scheduler.add_daily_task(DAILY_REPORT_TIME, send_daily_report)

    # 启动时先执行一次每日报告
    send_daily_report()

    print(f"监控程序已启动...")
    print(f"- 仓位监控间隔: {NOTIFY_INTERVAL}秒")
    print(f"- 每日报告时间: {DAILY_REPORT_TIME}")

    # 运行调度器
    scheduler.run()

if __name__ == "__main__":
    main() 