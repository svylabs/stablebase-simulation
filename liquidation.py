import json 

PRECISION = 1e18

def ComplexHandler(Obj):
    if hasattr(Obj, '__json__'):
        return Obj.__json__()
    else:
        raise TypeError('Object of type %s with value of %s is not JSON serializable' % (type(Obj), repr(Obj)))

class Uint:
    def __init__(self, value, scaled=True):
        self.value = value * PRECISION if not scaled else value

    def zero():
        return Uint(0)

    def one():
        return Uint(1)

    def ONE():
        return Uint(PRECISION)
    
    def unscaled(value):
        return Uint(value, scaled=False)

    def __add__(self, other):
        return Uint(self.value + other.value)
    
    def __iadd__(self, other):
        self.value += other.value
        return self
    
    def __sub__(self, other):
        return Uint(self.value - other.value)

    def __mul__(self, other):
        return Uint(self.value * other.value)
    
    def __truediv__(self, other):
        return Uint(self.value // other.value)
    
    def __repr__(self):
        return str(self.value / PRECISION)
    
    def __str__(self):
        return str(self.value / PRECISION)
    
    def clone(self):
        return Uint(self.value, scaled=True)
    
class Stake:
    def __init__(self, amount):
        self.amount = amount
        self.reward_snapshot = Uint.zero()
        self.collateral_snapshot = Uint.zero()
        self.claimed_rewards = Uint.zero()
        self.claimed_collateral = Uint.zero()
        self.cumulative_product_scaling_factor = Uint.ONE()
    
    def __json__(self):
        return json.dumps({
            "amount": str(self.amount),
            "reward_snapshot": str(self.reward_snapshot),
            "collateral_snapshot": str(self.collateral_snapshot),
            "claimed_rewards": str(self.claimed_rewards / Uint.ONE()),
            "claimed_collateral": str(self.claimed_collateral / Uint.ONE()),
            "cumulative_product_scaling_factor": str(self.cumulative_product_scaling_factor)
        })


class StabilityPool:
    def __init__(self):
        self.stakes = {
        }
        self.total_stake = Uint.zero()
        self.rewards_per_token = Uint.zero()
        self.collateral_per_token = Uint.zero()
        self.stake_scaling_factor = Uint.ONE()


    def liquidate(self, amount, collateral):
        current_scaling_factor = self.stake_scaling_factor
        # scaling factor = ( 1 - A / T) = (T - A) / T
        new_scaling_factor = ((self.total_stake - amount) * Uint.ONE()) / self.total_stake
        # cumulative product scaling factor = (1 - A[1] / T[0]) * (1 - A[2] / T[1]) * ... * (1 - A[n] / T[n-1])
        cumulative_product_scaling_factor = (self.stake_scaling_factor * new_scaling_factor) / Uint.ONE()
        self.stake_scaling_factor = cumulative_product_scaling_factor
        # CGPT = CGPT + (C / T) * current_scaling_factor
        # CGPT =  CGPT + (C / T) * (1 - A1 / T0) * (1 - A2 / T1) * ... * (1 - An / Tn-1)
        self.collateral_per_token += ((collateral * current_scaling_factor) / self.total_stake)
        self.total_stake -= amount

    def update_user(self, user):
        pending_rewards = ((self.rewards_per_token - user.reward_snapshot) * user.amount) / user.cumulative_product_scaling_factor
        user.claimed_rewards += pending_rewards
        # CGPT =  CGPT + (C / T) * (1 - A1 / T0) * (1 - A2 / T1) * ... * (1 - An / Tn-1)
        # CGNT = (CGPT * user_stake - user.collateral_snapshot * user_stake) /  [ 1 * (1 - A1 / T0) * (1 - A2 / T1) * ... * (1 - Ai / Ti-1) ] where i < n, and i is the ith liquidation after which user staked / reset their stakes
        pending_collateral = ((self.collateral_per_token  - user.collateral_snapshot ) * user.amount) / user.cumulative_product_scaling_factor
        user.claimed_collateral += pending_collateral
        user.reward_snapshot = self.rewards_per_token.clone()
        user.collateral_snapshot = self.collateral_per_token.clone()
        user.amount = ((user.amount * self.stake_scaling_factor) / user.cumulative_product_scaling_factor)
        user.cumulative_product_scaling_factor = self.stake_scaling_factor.clone()
        return (pending_rewards, pending_collateral)
    
    def claim(self, user):
        if user not in self.stakes:
            return (Uint.zero(), Uint.zero())
        pending_rewards, pending_collateral = self.update_user(self.stakes[user])
        return (pending_rewards, pending_collateral)


    def stake(self, user, amount):
        if user in self.stakes:
            self.update_user(self.stakes[user])
            self.stakes[user].amount += amount
        else:
            stake = Stake(amount.clone())
            stake.reward_snapshot = self.rewards_per_token.clone()
            stake.collateral_snapshot = self.collateral_per_token.clone()
            stake.amount = amount.clone()
            stake.cumulative_product_scaling_factor = self.stake_scaling_factor.clone()
            self.stakes[user] = stake
        self.total_stake += amount


    def unstake(self, user, amount):
        if user in self.stakes:
            self.update_user(self.stakes[user])
            self.stakes[user].amount -= amount
            self.total_stake -= amount
        else:
            pass

    def add_reward(self, amount):
        # RPT = RPT + (R / T) * current_scaling_factor
        # RPT =  RPT + (R / T) * (1 - A1 / T0) * (1 - A2 / T1) * ... * (1 - An / Tn-1)
        self.rewards_per_token += (amount * self.stake_scaling_factor) / self.total_stake

    def withdraw_reward(self, user):
        if user not in self.stakes:
            return Uint.zero()
        self.update_user(self.stakes[user])
        reward = self.stakes[user] * self.rewards_per_token
        self.stakes[user] = 0
        self.total_stake -= self.stakes[user]
        return reward
    

    def __repr__(self):
        return json.dumps(self.__json__(), indent=2)
    
    def __json__(self):
        return {
            "stakes": self.stakes,
            "total_stake": str(self.total_stake),
            "rewards_per_token": str(self.rewards_per_token),
            "collateral_per_token": str(self.collateral_per_token),
            "stake_scaling_factor": str(self.stake_scaling_factor)
        }
    
def print_pool(pool, message=""):
    print()
    print(message)
    print(json.dumps(pool, indent=2, default=ComplexHandler))



pool = StabilityPool()

userAStake = Uint.unscaled(1000)
userBStake = Uint.unscaled(2000)
userCStake = Uint.unscaled(1500)

print(userAStake.value, userBStake.value, userCStake.value)


pool.stake(1, userAStake)
pool.stake(2, userBStake)
pool.stake(3, userCStake)
print_pool(pool)
pool.add_reward(Uint.unscaled(450))
print_pool(pool)
pool.unstake(1, userAStake)
print_pool(pool)
pool.stake(1, userAStake)
print_pool(pool)
pool.unstake(1, userAStake)
print_pool(pool)
pool.stake(1, userAStake)
print_pool(pool)
pool.unstake(2, userBStake)
print_pool(pool)
pool.add_reward(Uint.unscaled(100))
print_pool(pool)
pool.unstake(3, userCStake)
print_pool(pool)
pool.liquidate(Uint.unscaled(500), Uint.unscaled(1))
print_pool(pool, "After liquidation 1, only 1 stakes 1000 tokens")
pool.add_reward(Uint.unscaled(100))
print_pool(pool, "After 100 token rewards added")
#print(pool.claim(1))
#print_pool(pool, "Aftr liquidation, user 1 stake reduced to 500 tokens")
pool.stake(3, Uint.unscaled(500))
print_pool(pool, "After 3 stakes 500 tokens")
pool.stake(4, Uint.unscaled(500))
print_pool(pool, "After 4 stakes 500 tokens")
pool.add_reward(Uint.unscaled(100))
print_pool(pool, "After 100 token rewards added")
pool.liquidate(Uint.unscaled(500), Uint.unscaled(1))
print_pool(pool, "After liquidation 2(1: 500, 3: 500, 4: 500)")
#print(pool.claim(1), "After 1 claims")
#print_pool(pool)
print(pool.claim(3), "After 3 claims")
print_pool(pool, "After 3 claims rewards")
#print(pool.claim(4), "After 4 claims")
#print_pool(pool)
pool.stake(1, Uint.unscaled(666))
print_pool(pool, "After 1 stakes 666 tokens")
pool.add_reward(Uint.unscaled(100))
print_pool(pool, "After 100 token rewards added")
pool.liquidate(Uint.unscaled(333), Uint.unscaled(1))
print_pool(pool, "After liquidation of 333 tokens") # 1000, 333, 333
print(pool.claim(1), "After 1 claims")
print_pool(pool, "After 1 claims")
print(pool.claim(3), "After 3 claims")
print_pool(pool, "After 3 claims")
print(pool.claim(4), "After 4 claims")
print_pool(pool, "After 4 claims")


