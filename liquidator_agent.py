from base_agent import BaseAgent
from rate_governor_agent import RateGovernorAgent
from normal_user_agent import NormalUserAgent

class LiquidatorAgent(BaseAgent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        # Identify under-collateralized positions
        for agent in self.model.schedule.agents:
            if isinstance(agent, (RateGovernorAgent, NormalUserAgent)):
                if self.is_under_collateralized(agent):
                    self.liquidate(agent)
                    break  # Limit to one liquidation per step

    def is_under_collateralized(self, agent):
        collateral_value = agent.collateral * self.model.collateral_value
        debt_value = agent.debt
        return collateral_value / debt_value < self.model.liquidation_ratio

    def liquidate(self, agent):
        # Liquidator deposits stablecoins equal to agent's debt, which are burned
        self.model.total_supply -= agent.debt
        # Transfer collateral to liquidator
        self.model.collateral_pool -= agent.collateral
        # Reset agent's debt and collateral
        agent.debt = 0
        agent.collateral = 0

'''
    def liquidate(self, agent):
        # Liquidator deposits stablecoins equal to agent's debt * discount factor
        discount_factor = 0.95  # Liquidator pays 95% of the debt
        liquidation_payment = agent.debt * discount_factor
        self.model.total_supply -= liquidation_payment
        # Liquidator receives collateral
        self.model.collateral_pool -= agent.collateral
        # Profit calculation (optional)
        profit = agent.debt - liquidation_payment
        # Reset agent's debt and collateral
        agent.debt = 0
        agent.collateral = 0
'''

