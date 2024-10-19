from base_agent import BaseAgent
import random
from third_party_depositor_agent import ThirdPartyDepositorAgent

class NormalUserAgent(BaseAgent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        #self.collateral = random.randint(1, 1000)
        #self.debt = (random.randint(10, 90) * self.collateral) / 100
        self.debt = 0
        self.transferred = 0
        self.collateral = random.uniform(0.3, 10)
        self.redemption_protection = 0  # Amount of protection purchased
        self.protection_duration = 0    # Days remaining
        self.shielding_rate_paid = 0

    def step(self):
        # Decide whether to borrow
        if self.debt == 0 and self.model.random.random() < 0.1:
            self.init_debt()
        #if self.model.random.random() < 0.1:
        #    self.borrow()

        # Update redemption protection
        if self.protection_duration > 0:
            self.protection_duration -= 1
        else:
            self.redemption_protection = 0  # Protection expired

        # Renewal of redemption protection
        if self.protection_duration == 0:
            if self.model.random.random() < 0.5:
                # 50% chance to renew protection
                total_shielding_rate = self.model.current_shielding_rate
                protection_months = random.randint(1, 4)
                renewal_fee = self.debt *  (total_shielding_rate / 12) * protection_months
                self.redemption_protection += renewal_fee
                self.shielding_rate_paid = total_shielding_rate
                #self.model.total_fee_paid += renewal_fee
                self.model.distribute_shielding_fees(renewal_fee)
                self.protection_duration = protection_months * 30
                # Adjust debt accordingly
                #self.debt += renewal_fee

        if self.model.random.random() < 0.02 and self.transferred < self.debt:
            # transfer to third party depositor agent 
            agent = None
            while True:
                agent = self.model.random.choice(self.model.schedule.agents)
                if isinstance(agent, ThirdPartyDepositorAgent):
                    break
            to_transfer = random.uniform(1, self.debt)
            agent.receive_payment(to_transfer)
            self.transferred += to_transfer
    
    def init_debt(self):
        self.debt = (random.randint(10, 90) * self.collateral * self.model.collateral_value) / 100
        self.model.total_supply += self.debt
        self.model.collateral_pool += self.collateral
        self.model.normal_user_debt += self.debt
        total_shielding_rate = self.model.current_shielding_rate
        self.shielding_rate_paid = total_shielding_rate
        protection_months = random.randint(1, 4)
        shielding_fee = self.debt * (total_shielding_rate / 12) * protection_months
        #self.model.total_fee_paid += shielding_fee
        self.protection_duration = protection_months * 30
        self.model.distribute_shielding_fees(shielding_fee)

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

