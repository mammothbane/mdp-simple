## Markov Decision Process

This is is an implementation a simple MDP agent. Configuration files specify a grid-based world with:

- impassable tiles
- 'normal' tiles
- a rectangular region of flowing water
- goal states.

All non-goal states have uniform utilities, and all transitions have a 100% chance of success
unless moving *from* a water tile, in which case they have a chance of moving in the direction the water is flowing
(left, right, up, or down).

The agent generates approximately-optimal utility values for each tile, then infers the optimal movement policy.
