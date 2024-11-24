import ccxt
from typing import Dict, List
from datetime import datetime
import pytz

class BinanceClient:
    def __init__(self, config: dict):
        self.account_name = config.pop('name')  # 获取并移除name字段
        self.exchange = ccxt.binance(config)
        self._last_positions = {}
        self._position_open_times = {}

    def get_account_balance(self) -> Dict:
        """获取账户总资产和盈亏信息"""
        try:
            # 获取账户总资产、可用余额和占用保证金
            balance = self.exchange.fetch_balance()
            total_balance = balance['total']['USDT']
            free_balance = balance['free']['USDT']
            used_balance = balance['used']['USDT']

            # 获取总未实现盈亏
            account_info = self.exchange.fapiPrivateV2GetAccount()
            total_unrealized_pnl = float(account_info['totalUnrealizedProfit'])

            return {
                'account_name': self.account_name,
                'total_balance': total_balance,
                'free_balance': free_balance,
                'used_balance': used_balance,
                'total_unrealized_pnl': total_unrealized_pnl
            }
        except Exception as e:
            raise Exception(f"{self.account_name} 获取账户余额失败: {str(e)}")

    def get_positions(self) -> List[Dict]:
        """获取当前持仓信息"""
        try:
            positions = self.exchange.fetch_positions()
            active_positions = []
            
            # 设置美国东部时区
            eastern = pytz.timezone('America/New_York')
            
            for position in positions:
                if float(position['contracts']) > 0:
                    # 提取基础货币名称（例如从"BTC/USDT:USDT"提取"BTC"）
                    base_currency = position['symbol'].split('/')[0]
                    
                    timestamp = self.exchange.milliseconds()
                    # 转换为美国东部时间
                    utc_dt = datetime.fromtimestamp(timestamp/1000, pytz.UTC)
                    eastern_dt = utc_dt.astimezone(eastern)
                    datetime_str = eastern_dt.strftime('%Y-%m-%d %H:%M:%S')
                    
                    position_data = {
                        'account_name': self.account_name,
                        'symbol': position['symbol'],
                        'base_currency': base_currency,  # 添加基础货币字段
                        'side': position['side'],
                        'contracts': position['contracts'],
                        'entryPrice': position['entryPrice'],
                        'margin': position['initialMargin'],
                        'unrealizedPnl': position['unrealizedPnl'],
                        'percentage': position['percentage'],
                        'timestamp': timestamp,
                        'datetime': datetime_str
                    }
                    active_positions.append(position_data)
            return active_positions
        except Exception as e:
            raise Exception(f"{self.account_name} 获取持仓信息失败: {str(e)}")

    def check_position_changes(self) -> Dict:
        """检查仓位变化"""
        current_positions = {
            p['symbol']: p for p in self.get_positions()
        }
        
        changes = {
            'new_positions': [],
            'closed_positions': [],
            'modified_positions': []
        }

        # 检查新开仓和仓位修改
        for symbol, position in current_positions.items():
            if symbol not in self._last_positions:
                changes['new_positions'].append(position)
                # 记录开仓时间
                self._position_open_times[symbol] = position['datetime']
            elif position != self._last_positions[symbol]:
                changes['modified_positions'].append({
                    'old': self._last_positions[symbol],
                    'new': position
                })

        # 检查平仓
        for symbol, position in self._last_positions.items():
            if symbol not in current_positions:
                # 添加开仓时间到平仓信息中
                position['open_time'] = self._position_open_times.get(symbol)
                changes['closed_positions'].append(position)
                # 清除开仓时间记录
                self._position_open_times.pop(symbol, None)

        self._last_positions = current_positions
        return changes 