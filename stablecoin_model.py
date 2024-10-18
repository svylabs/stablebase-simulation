from mesa import Model
from mesa.time import SimultaneousActivation
from mesa.datacollection import DataCollector
from rate_governor_agent import RateGovernorAgent
from normal_user_agent import NormalUserAgent
from third_party_depositor_agent import ThirdPartyDepositorAgent
from liquidator_agent import LiquidatorAgent

class StablecoinModel(Model):
    def __init__(self, N_rate_governors, N_users, N_depositors, N_liquidators):
        self.num_agents = N_rate_governors + N_users + N_depositors + N_liquidators
        self.schedule = SimultaneousActivation(self)
        self.reserve_pool = 0
        self.collateral_pool = 0
        self.total_supply = 0
        self.collateral_value = 2000  # Assume collateral value starts at 1
        self.collateralization_ratio = 1.5  # 150% collateralization
        self.liquidation_ratio = 1.1  # Liquidate if collateral drops below 110%
        self.protection_period = 30  # Days for redemption protection
        self.rate_setting_interval = 1  # Rate governors set rates every day
        self.shielding_rates = {}  # Store shielding rates submitted by rate governors
        self.current_shielding_rate = 0.02  # Initial shielding rate

        # Create agents
        agent_id = 0
        for _ in range(N_rate_governors):
            stake = self.random.uniform(1000, 5000)
            agent = RateGovernorAgent(agent_id, self)
            self.schedule.add(agent)
            agent_id += 1

        for _ in range(N_users):
            agent = NormalUserAgent(agent_id, self)
            self.schedule.add(agent)
            agent_id += 1

        for _ in range(N_depositors):
            agent = ThirdPartyDepositorAgent(agent_id, self)
            self.schedule.add(agent)
            # Add their deposit to the reserve pool
            self.reserve_pool += agent.deposit
            agent_id += 1

        for _ in range(N_liquidators):
            agent = LiquidatorAgent(agent_id, self)
            self.schedule.add(agent)
            agent_id += 1

        self.datacollector = DataCollector(
            model_reporters={
                "Total Supply": "total_supply",
                "Reserve Pool": "reserve_pool",
                "Collateral Pool": "collateral_pool",
                "Current Shielding Rate": "current_shielding_rate",
                "Collateral Price": "collateral_value"
            },
            agent_reporters={
                "AgentType": lambda agent: type(agent).__name__,  # Agent type (RateGovernor, NormalUser, etc.)
                #"AgentID": lambda agent: getattr(agent, "unique_id"),
                "Debt": lambda agent: getattr(agent, "debt", 0),
                "Collateral": lambda agent: getattr(agent, "collateral", 0),
                "RedemptionProtection": lambda agent: getattr(agent, "redemption_protection", 0),
                "Stake": lambda agent: getattr(agent, "stake", 0) if isinstance(agent, RateGovernorAgent) else 0,
            }
        )

    def step(self):
        self.schedule.step()
        # Collect data
        self.datacollector.collect(self)

        # Update collateral value (simulate price changes)
        self.update_collateral_value()

        # Rate governors set shielding rates at defined intervals
        if self.schedule.steps % self.rate_setting_interval == 0:
            self.calculate_shielding_rate()

        # Step all agents
        self.schedule.step()

    def calculate_shielding_rate(self):
        total_stake = sum(
            agent.stake for agent in self.schedule.agents if isinstance(agent, RateGovernorAgent)
        )
        if total_stake == 0:
            self.current_shielding_rate = 0
        else:
            weighted_rates = [
                agent.shielding_rate_reveal * agent.stake
                for agent in self.schedule.agents
                if isinstance(agent, RateGovernorAgent) and agent.shielding_rate_reveal is not None
            ]
            self.current_shielding_rate = sum(weighted_rates) / total_stake

    def update_collateral_value(self):
        # Simulate collateral price movements (e.g., between 0.95 and 1.05)
        self.collateral_value *= self.random.uniform(0.98, 1.02)

    def automatic_liquidation(self):
        # Identify rate governors who are under-collateralized
        under_collateralized_agents = [
            agent for agent in self.schedule.agents
            if isinstance(agent, RateGovernorAgent) and self.is_under_collateralized(agent)
        ]

        if under_collateralized_agents:
            # Distribute debt and collateral among other rate governors
            # Implementation details depend on the specific rules of your protocol
            pass

