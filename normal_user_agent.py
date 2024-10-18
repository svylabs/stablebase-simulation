from base_agent import BaseAgent
import random

class NormalUserAgent(BaseAgent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.collateral = random.randint(1, 1000)
        self.debt = (random.randint(10, 90) * self.collateral) / 100
        self.redemption_protection = 0  # Amount of protection purchased
        self.protection_duration = 0    # Days remaining

    def step(self):
        # Decide whether to borrow
        if self.model.random.random() < 0.1:
            self.borrow()

        # Update redemption protection
        if self.protection_duration > 0:
            self.protection_duration -= 1
        else:
            self.redemption_protection = 0  # Protection expired

        # Renewal of redemption protection
        if self.protection_duration == 0:
            if self.model.random.random() < 0.5:
                # 50% chance to renew protection
                renewal_fee = self.debt * self.model.current_shielding_rate
                self.redemption_protection += renewal_fee
                self.protection_duration = self.model.protection_period
                # Adjust debt accordingly
                self.debt += renewal_fee

    def borrow(self):
        borrow_amount = self.model.random.uniform(50, 200)
        total_shielding_rate = self.model.current_shielding_rate

        # Check reserve pool
        if self.model.reserve_pool >= borrow_amount:
            self.model.reserve_pool -= borrow_amount
        else:
            mint_amount = borrow_amount
            #self.model.reserve_pool = 0
            self.model.total_supply += mint_amount

        # Pay shielding fee and purchase redemption protection
        shielding_fee = borrow_amount * total_shielding_rate
        self.redemption_protection += shielding_fee
        self.protection_duration = self.model.protection_period

        # Update debt and collateral
        self.debt += borrow_amount + shielding_fee
        collateral_amount = borrow_amount * self.model.collateralization_ratio
        self.collateral += collateral_amount
        self.model.collateral_pool += collateral_amount

