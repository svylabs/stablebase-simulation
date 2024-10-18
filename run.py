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
data = model.datacollector.get_model_vars_dataframe()
data["Total Supply"].plot()
plt.title("Total Stablecoin Supply Over Time")
plt.xlabel("Time")
plt.ylabel("Total Supply")
plt.show()

# Plot reserve pool over time
data["Reserve Pool"].plot()
plt.title("Reserve Pool Over Time")
plt.xlabel("Time")
plt.ylabel("Reserve Pool")
plt.show()

# Plot collateral pool over time
data["Collateral Pool"].plot()
plt.title("Collateral Pool Over Time")
plt.xlabel("Time")
plt.ylabel("Collateral Pool")
plt.show()

data["Collateral Price"].plot()
plt.title("Collateral Price Over Time")
plt.xlabel("Time")
plt.ylabel("Collateral Price")
plt.show()


