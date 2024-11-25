import schedule
import time
import signal
from datetime import datetime
from typing import Callable

class TaskScheduler:
    def __init__(self):
        self.jobs = []
        self.running = True
        
        # 注册信号处理
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)
    
    def _handle_signal(self, signum, frame):
        """处理退出信号"""
        print("\n正在安全退出程序...")
        self.running = False
    
    def add_interval_task(self, interval: int, task: Callable):
        """添加间隔执行的任务"""
        def job():
            try:
                task()
            except Exception as e:
                print(f"执行定时任务失败: {str(e)}")
        
        schedule.every(interval).seconds.do(job)
        self.jobs.append(job)

    def add_daily_task(self, time: str, task: Callable):
        """添加每日定时任务"""
        def job():
            try:
                task()
            except Exception as e:
                print(f"执行每日任务失败: {str(e)}")
        
        schedule.every().day.at(time).do(job)
        self.jobs.append(job)

    def run(self):
        """运行调度器"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                print(f"调度器运行错误: {str(e)}")
                time.sleep(5)
        
        print("程序已安全退出")