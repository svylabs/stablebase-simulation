from mesa import Model
from mesa.time import SimultaneousActivation
from mesa.datacollection import DataCollector
from rate_governor_agent import RateGovernorAgent
from normal_user_agent import NormalUserAgent
from third_party_depositor_agent import ThirdPartyDepositorAgent
from liquidator_agent import LiquidatorAgent
import random

class StablecoinModel(Model):
    def __init__(self, N_rate_governors, N_users, N_depositors, N_liquidators):
        self.num_agents = N_rate_governors + N_users + N_depositors + N_liquidators
        self.schedule = SimultaneousActivation(self)
        self.reserve_pool = 0
        self.reserve_pool_stake_rate_governors = 0
        self.reserve_pool_stake_thirdparty_depositors = 0
        self.collateral_pool = 0
        self.total_supply = 0
        self.collateral_value = 60000  # Assume collateral value starts at 1
        self.collateralization_ratio = 1.5  # 150% collateralization
        self.normal_user_debt = 0
        self.total_fee_paid = 0
        self.liquidation_ratio = 1.1  # Liquidate if collateral drops below 110%
        self.protection_period = 360  # Days for redemption protection
        self.rate_setting_interval = 1  # Rate governors set rates every day
        self.shielding_rates = {}  # Store shielding rates submitted by rate governors
        self.stablecoin_price = 1.0
        self.current_shielding_rate = 0.0  # Initial shielding rate
        self.shielding_fees_rate_governors = 0
        self.shielding_fees_thirdparty_depositor_agents = 0
        self.yield_rate_governors = 0
        self.yield_thirdparty_depositor_agents = 0

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
                "Collateral Price": "collateral_value",
                "shielding_rates": "current_shielding_rate",
                "stablecoin_price": "stablecoin_price",
                "shielding_fees_rate_governors": "shielding_fees_rate_governors",
                "shielding_fees_thirdparty_depositor_agents": "shielding_fees_thirdparty_depositor_agents",
                "reserve_pool_stake_governors": "reserve_pool_stake_rate_governors",
                "reserve_pool_stake_thirdparty_depositors": "reserve_pool_stake_thirdparty_depositors",
                "total_fee_paid": "total_fee_paid",
                "normal_user_debt": "normal_user_debt",
                "yield_rate_governors": "yield_rate_governors",
                "yield_thirdparty_depositor_agents": "yield_thirdparty_depositor_agents",
            },
            agent_reporters={
                "AgentType": lambda agent: type(agent).__name__,  # Agent type (RateGovernor, NormalUser, etc.)
                #"AgentID": lambda agent: getattr(agent, "unique_id"),
                "Debt": lambda agent: getattr(agent, "debt", 0),
                "NormalUserDebt": lambda agent: getattr(agent, "debt", 0) if isinstance(agent, NormalUserAgent) else 0,
                "Collateral": lambda agent: getattr(agent, "collateral", 0),
                "RedemptionProtection": lambda agent: getattr(agent, "redemption_protection", 0),
                "Stake": lambda agent: getattr(agent, "stake", 0) if isinstance(agent, RateGovernorAgent) else 0,
                "Yield": lambda agent: getattr(agent, "shielding_fees", 0) if isinstance(agent, RateGovernorAgent) or isinstance(agent, ThirdPartyDepositorAgent) else 0,
            }
        )

    def step(self):
        self.schedule.step()
        # Collect data
        self.calculate_yield()
        self.datacollector.collect(self)

        # Update collateral value (simulate price changes)
        self.update_collateral_value()

        self.update_stablecoin_price()

        # Rate governors set shielding rates at defined intervals
        if self.schedule.steps % self.rate_setting_interval == 0:
            self.calculate_shielding_rate()

        # Step all agents
        self.schedule.step()

    def calculate_yield(self):
        self.yield_rate_governors = (self.shielding_fees_rate_governors / self.reserve_pool_stake_rate_governors if self.reserve_pool_stake_rate_governors > 0 else 0 ) * 100
        self.yield_thirdparty_depositor_agents = (self.shielding_fees_thirdparty_depositor_agents / self.reserve_pool_stake_thirdparty_depositors if self.reserve_pool_stake_thirdparty_depositors > 0 else 0 ) * 100

    def update_stablecoin_price(self):
        self.stablecoin_price = random.uniform(0.95, 1.05)

    def update_reserve_pool_stake_governor(self, stake):
        self.reserve_pool_stake_rate_governors += stake
        self.reserve_pool += stake

    def update_reserve_pool_stake_thirdparty_depositor(self, stake):
        self.reserve_pool_stake_thirdparty_depositors += stake
        self.reserve_pool += stake

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

    def distribute_shielding_fees(self, shielding_fees):
        # Distribute shielding fees among rate governors
        rate_governors = [agent for agent in self.schedule.agents if isinstance(agent, RateGovernorAgent)]
        total_stake = self.reserve_pool
        if rate_governors:
            #fee_per_agent = shielding_fees / len(rate_governors)
            #total_stake = sum(agent.stake for agent in rate_governors)
            for agent in rate_governors:
                fees = shielding_fees * (agent.stake / total_stake)
                agent.shielding_fees += fees
                self.shielding_fees_rate_governors += fees
        
        thirdparty_depositor_agents = [agent for agent in self.schedule.agents if isinstance(agent, ThirdPartyDepositorAgent)]
        if thirdparty_depositor_agents:
            for agent in thirdparty_depositor_agents:
                fees = shielding_fees * (agent.deposit / self.reserve_pool)
                agent.shielding_fees += fees
                self.shielding_fees_thirdparty_depositor_agents += fees

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

