from base_agent import BaseAgent

class ThirdPartyDepositorAgent(BaseAgent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.deposit = self.model.random.randint(5000, 100000)
        self.liquidity_ratio = self.model.random.uniform(0.1, 0.5)  # 10% to 50% instant liquidity
        self.locked_amount = self.deposit * (1 - self.liquidity_ratio)
        self.instant_liquidity = self.deposit * self.liquidity_ratio

    def step(self):
        # Decide whether to adjust deposit
        if self.model.random.random() < 0.05:
            self.adjust_deposit()

    def adjust_deposit(self):
        # For simplicity, randomly increase or decrease deposit
        change = self.model.random.uniform(-100, 100)
        self.deposit += change
        self.locked_amount = self.deposit * (1 - self.liquidity_ratio)
        self.instant_liquidity = self.deposit * self.liquidity_ratio
        # Update reserve pool
        self.model.reserve_pool += change
