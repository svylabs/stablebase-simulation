from base_agent import BaseAgent
import random
from third_party_depositor_agent import ThirdPartyDepositorAgent

class RateGovernorAgent(BaseAgent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.security_deposit_lock_period = 7  # Days
        self.shielding_rate_commitment = None
        self.shielding_rate_reveal = random.uniform(0.04, 0.05)
        self.reserve_ratio = random.randint(1, 100)
        self.collateral = random.randint(10, 200)
        self.debt = 0
        self.stake = 0
        self.security_deposit = 0
        self.shielding_fees = 0
        self.transferred = 0
        #self.debt = (random.randint(10, 90) * self.collateral) / 100
        #self.stake = (self.reserve_ratio * self.debt) / 100
        #self.security_deposit = 0.005 * self.stake  # 0.5% security deposit
        self.days_since_commitment = 0

    def commit_shielding_rate(self):
        # Commit phase: submit hash of the proposed shielding rate
        proposed_rate = self.shielding_rate_reveal
        if (self.model.stablecoin_price < 1.0):
            proposed_rate = self.shielding_rate_reveal + self.model.random.uniform(0.0001, 0.001)
        elif (self.model.stablecoin_price > 1.0):
            proposed_rate = self.shielding_rate_reveal - self.model.random.uniform(0.0001, 0.001)
          # Between 1% and 5%
        self.shielding_rate_reveal = proposed_rate
        self.shielding_rate_commitment = hash(proposed_rate)
        self.days_since_commitment = 0

    def reveal_shielding_rate(self):
        # Reveal phase: submit the actual shielding rate
        if self.days_since_commitment >= 1:
            self.model.shielding_rates[self.unique_id] = self.shielding_rate_reveal
            self.shielding_rate_commitment = None
            #self.shielding_rate_reveal = None
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
        if self.debt == 0:
            self.init_debt()
        #elif self.model.random.random() < 0.05:
        #    self.borrow()

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
        self.stake = (self.reserve_ratio * self.debt) / 100
        self.security_deposit = 0.005 * self.stake  # 0.5% security deposit
        self.model.total_supply += self.debt
        self.model.update_reserve_pool_stake_governor(self.stake)
        self.model.collateral_pool += self.collateral


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
