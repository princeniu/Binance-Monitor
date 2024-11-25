import requests
from typing import Dict, Any, List
from config import FEISHU_WEBHOOK_URL
from datetime import datetime
import pytz
import os

class FeishuNotifier:
    def __init__(self):
        self.webhook_url = FEISHU_WEBHOOK_URL
        self.report_dir = "每日报告"  # 报告保存目录

    def send_message(self, content: str) -> bool:
        """发送飞书消息"""
        try:
            payload = {
                "msg_type": "text",
                "content": {"text": content}
            }
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"发送飞书消息失败: {str(e)}")
            return False

    def format_position_message(self, changes: Dict[str, Any], exchange) -> str:
        """格式化仓位变化消息"""
        messages = []
        
        if changes['new_positions']:
            messages.append("🆕 新开仓:")
            for pos in changes['new_positions']:
                messages.append(
                    f"账户: {pos['account_name']}\n"
                    f"币种: {pos['base_currency']}\n"
                    f"方向: {pos['side']}\n"
                    f"开仓价格: ${float(pos['entryPrice']):.7f}\n"
                    f"保证金: ${float(pos['margin']):.2f}\n"
                    f"数量: {pos['contracts']}\n"
                    f"时间: {pos['datetime']}\n"
                )

        if changes['closed_positions']:
            messages.append("❌ 已平仓:")
            for pos in changes['closed_positions']:
                current_price = exchange.fetch_ticker(pos['symbol'])['last']
                
                # 计算持仓时长
                close_time = datetime.strptime(pos['datetime'], '%Y-%m-%d %H:%M:%S')
                open_time = datetime.strptime(pos['open_time'], '%Y-%m-%d %H:%M:%S')
                
                # 计算时间差（秒）
                duration_seconds = int((close_time - open_time).total_seconds())
                
                # 计算天数、小时和分钟
                days = duration_seconds // 86400
                hours = (duration_seconds % 86400) // 3600
                minutes = (duration_seconds % 3600) // 60
                
                # 如果总时长小于1分钟，强制设为1分钟
                if days == 0 and hours == 0 and minutes == 0:
                    minutes = 1
                
                # 格式化持仓时长
                duration_parts = []
                if days > 0:
                    duration_parts.append(f"{days}天")
                if hours > 0:
                    duration_parts.append(f"{hours}小时")
                if minutes > 0 or not duration_parts:
                    duration_parts.append(f"{minutes}分钟")
                duration_str = " ".join(duration_parts)
                
                messages.append(
                    f"账户: {pos['account_name']}\n"
                    f"币种: {pos['base_currency']}\n"
                    f"方向: {pos['side']}\n"
                    f"开仓价格: ${float(pos['entryPrice']):.7f}\n"
                    f"平仓价格: ${float(current_price):.7f}\n"
                    f"数量: {pos['contracts']}\n"
                    f"盈亏: ${pos['unrealizedPnl']:.2f}\n"
                    f"收益率: {pos['percentage']:.2f}%\n"
                    f"持仓时长: {duration_str}\n"
                    f"时间: {pos['datetime']}\n"
                )

        return "\n".join(messages) if messages else ""

    def save_daily_report_to_file(self, report_content: str, date: str):
        """保存每日报告到文件"""
        try:
            # 确保文件名格式正确
            filename = f"{date}.txt"
            filepath = os.path.join(self.report_dir, filename)
            
            # 写入文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_content)
                
        except Exception as e:
            print(f"保存每日报告失败: {str(e)}")

    def format_daily_report(self, balances: List[Dict], positions: List[Dict]) -> str:
        """格式化每日报告"""
        # 获取美东时间
        eastern = pytz.timezone('America/New_York')
        current_date = datetime.now(pytz.UTC).astimezone(eastern).strftime('%Y-%m-%d')
        
        # 生成报告内容
        report = [f"📊 每日账户报告 ({current_date})\n"]
        
        # 计算总资产
        total_assets = sum(balance['total_balance'] for balance in balances)
        total_pnl = sum(balance['total_unrealized_pnl'] for balance in balances)
        
        # 添加总资产信息
        report.extend([
            "💰 账户组合总览",
            f"总资产: ${total_assets:.2f} USDT",
            f"总未实现盈亏: ${total_pnl:.2f} USDT\n"
        ])
        
        # 添加每个账户的余额信息
        for balance in balances:
            report.extend([
                f"【{balance['account_name']}】",
                f"账户资产: ${balance['total_balance']:.2f} USDT",
                f"可用余额: ${balance['free_balance']:.2f} USDT",
                f"占用保证金: ${balance['used_balance']:.2f} USDT",
                f"未实现盈亏: ${balance['total_unrealized_pnl']:.2f} USDT\n"
            ])

        # 生成完整报告（用于发送通知）
        full_report = "\n".join(report)
        
        # 保存不含持仓信息的报告到文件
        self.save_daily_report_to_file(full_report, current_date)
        
        # 添加持仓信息（仅用于通知，不保存到文件）
        if positions:
            # 将持仓按账户分组
            main_positions = []
            sub_positions = []
            
            for pos in positions:
                if pos['account_name'] == '主账户':
                    main_positions.append(pos)
                else:
                    sub_positions.append(pos)
            
            # 分别对主账户和子账户的持仓按未实现盈亏排序
            main_positions.sort(key=lambda x: float(x['unrealizedPnl']), reverse=True)
            sub_positions.sort(key=lambda x: float(x['unrealizedPnl']), reverse=True)
            
            # 先添加主账户持仓
            if main_positions:
                report.append("📍 主账户持仓:")
                for pos in main_positions:
                    report.append(
                        f"{pos['base_currency']}: {pos['side']} "
                        f"未实现盈亏: ${float(pos['unrealizedPnl']):.2f} ({pos['percentage']:.2f}%)\n"
                    )
            
            # 再添加子账户持仓
            if sub_positions:
                if main_positions:  # 如果有主账户持仓，添加一个空行分隔
                    report.append("")
                report.append("📍 子账户持仓:")
                for pos in sub_positions:
                    report.append(
                        f"{pos['base_currency']}: {pos['side']} "
                        f"未实现盈亏: ${float(pos['unrealizedPnl']):.2f} ({pos['percentage']:.2f}%)\n"
                    )
        else:
            report.append("当前无持仓")
        
        return "\n".join(report) 