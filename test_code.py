
# %% This is a piece of code I wrote to generate a random set of shields to 
# see if the code was working
shield_set = "profane"
n_pieces = 16
n_slots = 8
slots = [i for i in range(8)] * 2
# slots = np.random.randint(0, n_slots, n_pieces)
hp_values = np.random.randint(10, 20, n_pieces)
crit_values = np.random.randint(100, 200, n_pieces)

pieces = {k: [] for k in range(n_slots)}
pieces_by_index = {}

for idx, (slot, hp, crit) in enumerate(zip(slots, hp_values, crit_values)):
    ss = np.random.choice(["profane", "sacrifice"])
    this_piece = Piece(ss, slot, hp, crit, idx)
    pieces[slot].append(this_piece)
    pieces_by_index[idx] = this_piece


all_combinations = []
res = generate_combinations(pieces, [], 0, all_combinations)
len(res)


# %% Now I have all the combinations and I want to find which one is the best
for c in res:
    print(c.shield_sets)

# %%
best_combinations = sorted(res, reverse=True, key=lambda x: x.crit)[:10]
# %%
for p in pieces_by_index.values():
    print(p.shield_set, p.slot)