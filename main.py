from mdp.mdp import MDP

print(-5)
mdp = MDP('examples/1.json', reward=-5, gamma=1)

mdp.value_iterate()
mdp.print_utility()

print(-60)
mdp = MDP('examples/1.json', reward=-60, gamma=1)

mdp.value_iterate()
mdp.print_utility()

print(-150)
mdp = MDP('examples/1.json', reward=-150, gamma=1)

mdp.value_iterate()
mdp.print_utility()
