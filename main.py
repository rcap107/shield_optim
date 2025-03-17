# TODO:
# define set bonuses
# compute the total stats given the selection of pieces
# iterate over all possible combinations
# filter combinations
# prune bad combinations

# toy example
# 3 pieces
# 2 stats per piece
# %%
import numpy as np
import json
import polars as pl

SET_BONUSES = json.load(open("set_bonuses.json"))

_internal = [
    "hp",
    "crit",
    "cdmg",
    "crit_defense",
    "cdmg_defense",
    "piercing",
    "block",
    "evasion",
    "defense",
    "health_regen",
]

_external = [
    "HP",
    "Accuracy",
    "Critical hit",
    "Critical damage",
    "Critical hit defense",
    "Critical damage defense",
    "Piercing",
    "Block",
    "Evasion",
    "Defense",
    "Health regen",
]

MAPPING_NAMES = dict(zip(_external, _internal))

base_stats = {
    
        "hp" :0,
        'accuracy' :0,
        "crit" :0,
        "cdmg" :0, 
        "crit_defense" :0,
        "cdmg_defense" :0,
        "piercing" :0,
        "block" :0,
        "evasion" :0,
        "defense" :0,
        "health_regen" :0,
        "debuff_resistance" :0,
}


# %%
class Combination:
    def __init__(self, pieces):
        self.hp = 0
        self.accuracy = 0
        self.crit = 0
        self.cdmg = 0
        self.crit_defense = 0
        self.cdmg_defense = 0
        self.piercing = 0
        self.block = 0
        self.evasion = 0
        self.defense = 0
        self.health_regen = 0
        self.debuff_resistance = 0

        self.shield_sets = {}
        for p in pieces:
            for attribute, value in vars(self).items():
                if hasattr(p, attribute):
                    setattr(
                        self,
                        attribute,
                        getattr(self, attribute) + getattr(p, attribute),
                    )

            if p.shield_set in self.shield_sets:
                self.shield_sets[p.shield_set] += 1
            else:
                self.shield_sets[p.shield_set] = 1

        for set_name, pieces_current_set in self.shield_sets.items():
            current_bonus = SET_BONUSES[set_name]
            
            for t, bonus in current_bonus.items():
                tier = int(t)
                if pieces_current_set >= tier:
                    for stat, value in bonus.items():
                        setattr(self, stat, getattr(self, stat)+value)
            

    def check_validity(self):
        """This function checks whether the given configuration satisfies certain
        constraints. If it does, it returns itself, otherwise it returns None.
        """
        if any(v for v in self.shield_sets.values() if v not in [3, 5, 8]):
            return None
        # if self.crit == 0:
        #     return None
        return self

    def __repr__(self):
        return f"Crit: {self.crit} HP: {self.hp} Crit dmg: {self.cdmg} Accuracy: {self.accuracy} Shield sets: {self.shield_sets}"

    def write_on_file(self):
        s = f"{self.crit},{self.hp}"

    def print_full_combination(self):
        """This function pretty prints the full set of shields with all the stats"""
        pass


class Piece:
    def __init__(
        self,
        shield_set,
        slot,
        hp,
        accuracy,
        crit,
        cdmg,
        crit_defense,
        cdmg_defense,
        piercing,
        block,
        evasion,
        defense,
        health_regen,
        idx,
    ):

        self.shield_set = shield_set
        self.slot = slot

        self.hp = hp
        self.crit = crit
        self.accuracy = accuracy
        self.cdmg = cdmg
        self.crit_defense = crit_defense
        self.cdmg_defense = cdmg_defense
        self.piecing = piercing
        self.block = block
        self.evasion = evasion
        self.defense = defense
        self.health_regen = health_regen

        self.idx = idx

    def __str__(self):
        return f"Slot: {self.slot} HP: {self.hp} Crit: {self.crit}"

    def __repr__(self):
        return f"Piece ID: {self.idx}"


# %% Here I generate all the combinations of soulshields
def generate_combinations(pieces, comb, slot, all_combinations):
    if len(comb) == 8:
        this_combination = Combination(comb)
        return this_combination.check_validity()
    else:
        for p in pieces[slot]:
            _c = generate_combinations(pieces, comb + [p], slot + 1, all_combinations)
            if isinstance(_c, Combination):
                all_combinations.append(_c)

        return all_combinations


# %% Time to load my own shield pieces and see if RAM explodes

df = pl.read_csv("shield-data.csv")
df = df.with_columns(
    pl.col("Critical hit defense").cast(int),
    pl.col("Critical damage defense").cast(int),
).fill_null(0)

# %%
n_slots = 8
pieces = {k: [] for k in range(n_slots)}
pieces_by_index = {}
for idx, row in enumerate(df.rows()):
    slot = row[1]
    vals = list(row) + [idx]
    this_piece = Piece(*vals)
    pieces[slot - 1].append(this_piece)
    pieces_by_index[idx] = this_piece
# %%

all_combinations = []
res = generate_combinations(pieces, [], 0, all_combinations)
len(res)
#%%
best_combinations = sorted(res, reverse=True, key=lambda x: x.cdmg)[:10]
vars(best_combinations[0])
# %%
