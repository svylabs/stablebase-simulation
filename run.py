from stablecoin_model import StablecoinModel
import matplotlib.pyplot as plt

# Initialize the model
model = StablecoinModel(
    N_rate_governors=10,
    N_users=100,
    N_depositors=300,
    N_liquidators=10
)

# Run the simulation for 100 steps (days)
for i in range(300):
    model.step()

# Retrieve data
data = model.datacollector.get_model_vars_dataframe()

# Plot total supply over time
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
data["Collateral Pool"].plot()
plt.title("Collateral Pool Over Time")
plt.xlabel("Time")
plt.ylabel("Collateral Pool")
#plt.show()

data["Collateral Price"].plot()
plt.title("Collateral Price Over Time")
plt.xlabel("Time")
plt.ylabel("Collateral Price")
#plt.show()

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

# Plot the debt of Rate Governors and Normal Users over time
for agent_id in agent_data_governors.index.get_level_values("AgentID").unique():
    agent_debt = agent_data_governors.xs(agent_id, level="AgentID")["Debt"]
    plt.plot(agent_debt, label=f"Rate Governor {agent_id}")

for agent_id in agent_data_users.index.get_level_values("AgentID").unique():
    agent_debt = agent_data_users.xs(agent_id, level="AgentID")["Debt"]
    plt.plot(agent_debt, label=f"Normal User {agent_id}", linestyle='dashed')

plt.title("Debt of Rate Governors and Normal Users Over Time")
plt.xlabel("Time Steps")
plt.ylabel("Debt")
#plt.legend()
plt.show()