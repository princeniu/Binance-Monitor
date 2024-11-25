from telegram import Bot
from telegram.error import TelegramError
import asyncio
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TelegramService:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self._bot = None
        self._loop = None

        # 创建报告保存目录
        self.report_dir = os.path.join(os.path.dirname(__file__), '..', '每日报告')
        if not os.path.exists(self.report_dir):
            os.makedirs(self.report_dir)

    @property
    def bot(self):
        """延迟初始化 bot，确保在正确的事件循环中创建"""
        if self._bot is None:
            self._bot = Bot(token=self.bot_token)
        return self._bot

    def send_message(self, message: str):
        """同步发送消息方法"""
        try:
            # 创建新的事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # 在新的事件循环中创建新的 bot 实例
            temp_bot = Bot(token=self.bot_token)
            
            # 发送消息
            loop.run_until_complete(self._async_send_message(temp_bot, message))
            
            # 关闭事件循环
            loop.close()
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")

    async def _async_send_message(self, bot, message: str):
        """异步发送消息方法"""
        try:
            await bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
        except TelegramError as e:
            logger.error(f"Failed to send Telegram message: {e}")

    async def start_message_handler(self, accounts):
        """Start handling incoming messages"""
        try:
            offset = None
            while True:
                try:
                    updates = await self.bot.get_updates(offset=offset, timeout=30)
                    for update in updates:
                        if update.message and update.message.text == "查询":
                            # 收集所有账户的信息
                            all_balances = []
                            for account in accounts:
                                balance = account.get_account_balance()
                                all_balances.append(balance)
                            
                            # 计算总资产和总未实现盈亏
                            total_balance = sum(balance['total_balance'] for balance in all_balances)
                            total_unrealized_pnl = sum(balance['total_unrealized_pnl'] for balance in all_balances)
                            
                            # 格式化消息
                            message = "📊 账户资产概览\n\n"
                            
                            # 总览部分
                            message += f"💰 总资产: {total_balance:.2f} USDT\n"
                            message += f"📈 未实现盈亏: {total_unrealized_pnl:.2f} USDT\n\n"
                            
                            # 各账户详细信息
                            for balance in all_balances:
                                message += f"【{balance['account_name']}】\n"
                                message += f"💰 总资产: {balance['total_balance']:.2f} USDT\n"
                                message += f"💵 可用余额: {balance['free_balance']:.2f} USDT\n"
                                message += f"🔒 占用保证金: {balance['used_balance']:.2f} USDT\n"
                                message += f"📈 未实现盈亏: {balance['total_unrealized_pnl']:.2f} USDT\n\n"
                            
                            # 使用当前事件循环的 bot 发送消息
                            await self._async_send_message(self.bot, message)
                        
                        # 更新offset
                        offset = update.update_id + 1
                    
                    # 短暂等待以避免过于频繁的请求
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error in message handler loop: {e}")
                    await asyncio.sleep(5)  # 出错后等待5秒再重试
                    
        except Exception as e:
            logger.error(f"Error in message handler: {e}")

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

    def format_daily_report(self, balances: list, positions: list) -> str:
        """Format daily report message"""
        message = f"📊 每日账户报告 ({datetime.now().strftime('%Y-%m-%d')})\n\n"
        
        # 合计所有账户的总资产和未实现盈亏
        total_balance = sum(balance['total_balance'] for balance in balances)
        total_unrealized_pnl = sum(balance['total_unrealized_pnl'] for balance in balances)
        
        # 添加总览信息
        message += f"💰 总资产: {total_balance:.2f} USDT\n"
        message += f"📈 未实现盈亏: {total_unrealized_pnl:.2f} USDT\n\n"
        
        # 添加各个账户的详细信息
        for balance in balances:
            message += f"【{balance['account_name']}】\n"
            message += f"总资产: {balance['total_balance']:.2f} USDT\n"
            message += f"可用余额: {balance['free_balance']:.2f} USDT\n"
            message += f"占用保证金: {balance['used_balance']:.2f} USDT\n"
            message += f"未实现盈亏: {balance['total_unrealized_pnl']:.2f} USDT\n\n"
        
        # 保存每日报告到文件
        self.save_daily_report_to_file(message, datetime.now().strftime('%Y-%m-%d'))
        
        # 添加持仓信息
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
                message += "📍 主账户持仓:\n\n"
                for pos in main_positions:
                    message += f"币种: {pos['base_currency']}\n"
                    message += f"方向: {pos['side']}\n"
                    message += f"未实现盈亏: {pos['unrealizedPnl']:.2f} USDT ({pos['percentage']:.2f}%)\n\n"

            # 再添加子账户持仓
            if sub_positions:
                message += "📍 子账户持仓:\n\n"
                for pos in sub_positions:
                    message += f"币种: {pos['base_currency']}\n"
                    message += f"方向: {pos['side']}\n"
                    message += f"未实现盈亏: {pos['unrealizedPnl']:.2f} USDT ({pos['percentage']:.2f}%)\n\n"
        else:
            message += "📍 当前无持仓\n\n"
        
        return message

    def format_position_message(self, changes: dict, exchange) -> str:
        """Format position change message"""
        message = ""
        
        # 处理新开仓
        if changes['new_positions']:
            message += "🆕 新开仓:\n\n"
            for pos in changes['new_positions']:
                message += f"账户: {pos['account_name']}\n"
                message += f"币种: {pos['base_currency']}\n"
                message += f"方向: {pos['side']}\n"
                message += f"数量: {pos['contracts']}\n"
                message += f"开仓价格: {pos['entryPrice']:.4f}\n"
                message += f"保证金: {pos['margin']:.2f} USDT\n"
                message += f"时间: {pos['datetime']}\n\n"

        # 处理平仓
        if changes['closed_positions']:
            message += "❌ 已平仓:\n\n"
            for pos in changes['closed_positions']:
                current_price = exchange.fetch_ticker(pos['symbol'])['last']
                
                # 计算持仓时长
                close_time = datetime.strptime(pos['datetime'], '%Y-%m-%d %H:%M:%S')
                open_time = datetime.strptime(pos['open_time'], '%Y-%m-%d %H:%M:%S')
                duration_seconds = int((close_time - open_time).total_seconds())
                
                days = duration_seconds // 86400
                hours = (duration_seconds % 86400) // 3600
                minutes = (duration_seconds % 3600) // 60
                
                if days == 0 and hours == 0 and minutes == 0:
                    minutes = 1
                
                duration_parts = []
                if days > 0:
                    duration_parts.append(f"{days}天")
                if hours > 0:
                    duration_parts.append(f"{hours}小时")
                if minutes > 0 or not duration_parts:
                    duration_parts.append(f"{minutes}分钟")
                duration_str = " ".join(duration_parts)
                
                message += f"账户: {pos['account_name']}\n"
                message += f"币种: {pos['base_currency']}\n"
                message += f"方向: {pos['side']}\n"
                message += f"开仓价格: {pos['entryPrice']:.4f}\n"
                message += f"平仓价格: {current_price:.4f}\n"
                message += f"数量: {pos['contracts']}\n"
                message += f"持仓时长: {duration_str}\n"
                message += f"盈亏: {pos['unrealizedPnl']:.2f} USDT ({pos['percentage']:.2f}%)\n"
                message += f"时间: {pos['datetime']}\n\n"

        return message if message else "持仓无变化"

    def format_trade_message(self, trade_data: dict) -> str:
        """Format trade notification message"""
        action = "开仓" if trade_data['action'] == 'OPEN' else "平仓"
        message = f"🔔 {action}通知\n\n"
        message += f"币种: {trade_data['base_currency']}\n"
        message += f"方向: {'做多' if trade_data['side'] == 'LONG' else '做空'}\n"
        message += f"数量: {trade_data['contracts']}\n"
        message += f"价格: {trade_data['price']:.4f}\n"
        if 'pnl' in trade_data:
            message += f"盈亏: {trade_data['pnl']:.2f} ({trade_data['roe']:.2f}%)"
        return message 