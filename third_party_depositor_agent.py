from base_agent import BaseAgent

class ThirdPartyDepositorAgent(BaseAgent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.deposit = 0
        self.pending_deposit = 0
        #self.liquidity_ratio = self.model.random.uniform(0.1, 0.5)  # 10% to 50% instant liquidity
        #self.locked_amount = self.deposit * (1 - self.liquidity_ratio)
        #self.instant_liquidity = self.deposit * self.liquidity_ratio
        self.shielding_fees = 0

    def step(self):
        pass
        # Decide whether to adjust deposit
        if self.pending_deposit > 0 and self.model.random.random() < 0.8:
            self.adjust_deposit()

    def adjust_deposit(self):
        # For simplicity, randomly increase or decrease deposit
        #change = self.model.random.randint(5000, 30000)
        self.deposit += self.pending_deposit
        #self.locked_amount = self.deposit * (1 - self.liquidity_ratio)
        #self.instant_liquidity = self.deposit * self.liquidity_ratio
        # Update reserve pool
        self.model.update_reserve_pool_stake_thirdparty_depositor(self.pending_deposit)
        self.pending_deposit = 0

    def receive_payment(self, amount):
        # Third-party depositors receive stablecoins
        self.pending_deposit += amount
        #self.locked_amount = self.deposit * (1 - self.liquidity_ratio)
        #self.instant_liquidity = self.deposit * self.liquidity_ratio
