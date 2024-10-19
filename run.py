from stablecoin_model import StablecoinModel
import matplotlib.pyplot as plt

# Initialize the model
model = StablecoinModel(
    N_rate_governors=100,
    N_users=2000,
    N_depositors=300,
    N_liquidators=10
)

# Run the simulation for 100 steps (days)
for i in range(300):
    model.step()

# Retrieve data
data = model.datacollector.get_model_vars_dataframe()

# Plot total supply over time
'''
data["Total Supply"].plot()
plt.title("Total Stablecoin Supply Over Time")
plt.xlabel("Time")
plt.ylabel("Total Supply")
#plt.show()


# Plot reserve pool over time
data["Reserve Pool"].plot()
plt.title("Reserve Pool Over Time")
plt.xlabel("Time")
plt.ylabel("Reserve Pool")
#plt.show()

# Plot collateral pool over time
#data["Collateral Pool"].plot()
#plt.title("Collateral Pool Over Time")
#plt.xlabel("Time")
#plt.ylabel("Collateral Pool")
#plt.show()
'''

#data["Collateral Price"].plot()
#plt.title("Collateral Price Over Time")
#plt.xlabel("Time")
#plt.ylabel("Collateral Price")
#plt.show()

data["normal_user_debt"].plot()
data["total_fee_paid"].plot()
plt.title("Total debt of normal users over time")
plt.xlabel("Time")
plt.ylabel("Debt / Shielding Fees Paid")
plt.yscale("log")   
plt.legend()
plt.show()

data["reserve_pool_stake_governors"].plot()
data["reserve_pool_stake_thirdparty_depositors"].plot()
plt.title("Reserve Pool Stake Over Time")
plt.xlabel("Time")
plt.ylabel("Governors / Third Party Depositors Stake")
plt.yscale("log")
plt.legend()
plt.show()



data["shielding_fees_rate_governors"].plot()
data["shielding_fees_thirdparty_depositor_agents"].plot()
plt.title("Revenue(Rate Governors / Third party depositors) Over Time")
plt.xlabel("Time")
plt.ylabel("Revenue")
plt.yscale("log")
plt.legend()
plt.show()

data["yield_rate_governors"].plot()
data["yield_thirdparty_depositor_agents"].plot()
plt.title("Yield Over Time")
plt.xlabel("Time")
plt.ylabel("Yield")
plt.yscale("log")
plt.legend()
plt.show()

data["shielding_rates"].plot()
data["stablecoin_price"].plot()
plt.title("Collateral Price / Shielding Rates Over Time")
plt.xlabel("Time")
plt.ylabel("Shielding Rates")
plt.yscale("log")
plt.legend()
plt.show()


agent_data = model.datacollector.get_agent_vars_dataframe()

agent_data = agent_data.reset_index()

# Set the new multi-level index with 'Step', 'AgentID', and 'AgentType'
agent_data = agent_data.set_index(['Step', 'AgentID', 'AgentType'])

print(agent_data.index.names)
print(agent_data.head())


# Filter agent data for a specific agent type
agent_data_governors = agent_data.xs('RateGovernorAgent', level="AgentType")
print(agent_data_governors.index.get_level_values("AgentID").unique())
agent_data_users = agent_data.xs('NormalUserAgent', level="AgentType")
agent_data_thirdparty = agent_data.xs('ThirdPartyDepositorAgent', level="AgentType")

'''
# Plot the debt of Rate Governors and Normal Users over time
for agent_id in agent_data_governors.index.get_level_values("AgentID").unique():
    agent_debt = agent_data_governors.xs(agent_id, level="AgentID")["Debt"]
    plt.plot(agent_debt, label=f"Rate Governor {agent_id}")


#for agent_id in agent_data_users.index.get_level_values("AgentID").unique():
#    agent_debt = agent_data_users.xs(agent_id, level="AgentID")["Debt"]
#    plt.plot(agent_debt, label=f"Normal User {agent_id}", linestyle='dashed')


for agent_id in agent_data_governors.index.get_level_values("AgentID").unique():
    agent_yield = agent_data_governors.xs(agent_id, level="AgentID")["Yield"]
    print("Rate Governor", agent_id, agent_yield.max())
    plt.plot(agent_debt, label=f"Rate Governor Yield {agent_id}", linestyle='dotted')

for agent_id in agent_data_thirdparty.index.get_level_values("AgentID").unique():
    agent_yield = agent_data_thirdparty.xs(agent_id, level="AgentID")["Yield"]
    print("ThirdParty Depositor", agent_id, agent_yield.max())
    plt.plot(agent_debt, label=f"Third Party Depositor {agent_id}", linestyle='dotted')



plt.title("Yield of users over time")
plt.xlabel("Time Steps")
plt.ylabel("Yield")
plt.legend()
plt.show()
'''