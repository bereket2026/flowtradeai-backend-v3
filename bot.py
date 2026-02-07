import time
import random
import threading

class FlowTradeBot:
    def __init__(self):
        self.running = False
        self.balance = 10000.0
        self.profit = 0.0

    def start(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self.run_bot, daemon=True).start()

    def stop(self):
        self.running = False

    def run_bot(self):
        while self.running:
            time.sleep(5)

            # simulate profit/loss
            change = random.uniform(-10, 25)
            self.balance += change
            self.profit += change

    def get_status(self):
        return {
            "balance": round(self.balance, 2),
            "profit": round(self.profit, 2),
            "running": self.running
        }


# global bot instance
bot = FlowTradeBot()
