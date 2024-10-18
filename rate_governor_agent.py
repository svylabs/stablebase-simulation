from base_agent import BaseAgent
import random

class RateGovernorAgent(BaseAgent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.security_deposit_lock_period = 7  # Days
        self.shielding_rate_commitment = None
        self.shielding_rate_reveal = None
        self.reserve_ratio = random.randint(1, 100)
        self.collateral = random.randint(1, 1000)
        self.debt = (random.randint(10, 90) * self.collateral) / 100
        self.stake = (self.reserve_ratio * self.debt) / 100
        self.security_deposit = 0.005 * self.stake  # 0.5% security deposit
        self.days_since_commitment = 0

    def commit_shielding_rate(self):
        # Commit phase: submit hash of the proposed shielding rate
        proposed_rate = self.model.random.uniform(0.01, 0.05)  # Between 1% and 5%
        self.shielding_rate_reveal = proposed_rate
        self.shielding_rate_commitment = hash(proposed_rate)
        self.days_since_commitment = 0

    def reveal_shielding_rate(self):
        # Reveal phase: submit the actual shielding rate
        if self.days_since_commitment >= 1:
            self.model.shielding_rates[self.unique_id] = self.shielding_rate_reveal
            self.shielding_rate_commitment = None
            self.shielding_rate_reveal = None
            self.days_since_commitment = 0

    def step(self):
        # Increment the days since commitment
        self.days_since_commitment += 1

        # Rate setting occurs once per day during specific time windows
        if self.model.schedule.steps % self.model.rate_setting_interval == 0:
            if self.shielding_rate_commitment is None:
                self.commit_shielding_rate()
            else:
                self.reveal_shielding_rate()

        # Borrowing logic
        if self.model.random.random() < 0.1:
            self.borrow()

    def borrow(self):
        # Borrow at 0% interest
        borrow_amount = self.model.random.randint(100, 500)
        # Deposit reserve ratio into the reserve pool
        reserve_deposit = (borrow_amount * self.reserve_ratio) * 0.01
        self.model.total_supply += borrow_amount
        # Update debt and collateral
        self.debt += borrow_amount
        collateral_amount = borrow_amount * self.model.collateralization_ratio
        self.collateral += collateral_amount
        self.model.collateral_pool += collateral_amount
