![cover](/img/hisss_cover.png)
# High-Speed Snake Simulator (HISSS)

A very fast simulation environment for the game of [Battlesnake](https://play.battlesnake.com). The game logic is implemented in C++ and provides python wrappers for convenience. The main features include:
- Fast C++ Implemtation with convenient python wrappers
- Support of all game modes including Royale, Wrapped, Constrictor, Restricted
- Generation of observation arrays for neural network training

https://github.com/user-attachments/assets/68538aa0-9ddb-45e2-b0c7-8ac224ff4dd8

## Installation
IMPORTANT: You need to have `g++` installed to use this library. The pip installation will compile the C++ source files for your system

You can install this package via pip:
```bash
pip install hisss
```

If you want to do development, change something or contribute new features fork this repository, clone and install via
```bash
pip install -e .
```
The pip installation already compiles C++ files for you.

## Basic Usage

The repository contains python bindings for the c++ implementation. We follow the basic naming scheme of [Battlesnake](https://play.battlesnake.com) with:
- duel: 1v1 with perfect information (full board visible)
- stadard: 4 snake free for all with perfect information
- restricted_duel: 1v1 with view radius
- restricted_standard: 4 snake free for all with view radius

A very basic usage example of the BattleSnakeGame looks like this:
```python
import hisss
from hisss import UP, DOWN, LEFT, RIGHT
game_config = hisss.duel_config()
env = hisss.BattleSnakeGame(game_config)
rewards, done, _ = env.step(actions=(UP, UP))  # length of actions must conform to number of snakes alive
env.render()  # prints game board to stdout
env.reset()
obs, _, _ = env.get_obs()
print(obs.shape)  # (2, 21, 21, 22), (num_snake_alive, w, h, channels)
explanation = hisss.encoding_layer_indices(game_config)
```
The explanation here is a dictionary telling you which information can be found in which channels of the observation. You may have noticed that the width and height of the observation is 21 even though the game is played in a board of 11x11. The reason for that is that the observation is centered around the snake head for each individual snake. This makes training of neural networks for example with a CNN easier, because CNNs tend to propagate information towards the middle of the image. As a result of the centering, the image needs to be larger to still capture the full game board, for example when the snake head is positioned at the edge of the board.

Notice that the API is slightly different from the standard Gym API. Reason for that is that we wanted to decouple the observation generation from the game simulation. If someone is only interested in simulating the game as fast as possible, then the slower observation generation can be hindering (it is slower in comparison to the step function, but still very fast). If you do the observation then you can simply call `env.get_obs()` to retrieve it.

You can get a pre-defined configuration for the different game modes with:
- duel: `hisss.duel_config()`
- standard: `hisss.standard_config()`
- restricted_duel: `hisss.restricted_duel_config()`
- restricted_standard: `hisss.restricted_standard_config()`


## Advanced Usage

There are a number of things that can be configured about the hisss BattleSnakeGame simulations. `

First of all, the `BattleSnakeConfig` has a lot of configuration options. Some other less popular game modes like Constrictor, Wrapped, Battle-Royal or any desired combination thereof are also supported and can be set via the `constrictor`, `wrapped`, `royale` flags respectively. Additionally, the board size, number of snakes and food spawn chance can be configured freely.

Additionally, if you want to do Reinforcement Learning, it might be worthwile to alter the standard reward calculation. By default, the winner gets a reward of +1 and a snake gets a reward of -1 if it dies. However, if you want to steer your snake to some different behavior, it might be good to do some reward engineering by changing the `reward_cfg` in the game configuration. An example is given by the `KillBattleSnakeRewardConfig` which distributes a positive reward to all living snakes if one of the other snake dies. This can incentivice more aggressive behavior.

Moreover, the obervation (encoding) configuration has a lot of configuration options. Take a look at `BattleSnakeEncodingConfig` for all the options. The default values are pretty good already, but you might also want to add new additional layers. You can do this either by changing the C++ side of the implementation or add the new layers in numpy on the python side. If you need information about the game on python side, you get it from the game state:
```python
state = env.get_state()
env.set_state(state)
```
The game state contains basically all information about the current state of the game. As shown in the example above, you can also set the environment to a specific state if desired. This is a bit dangerous though, make sure your state contains all correct information if you do so.

The battlesnake game board is symmetric in a sense that the value should not change if the board is mirrored or rotated. Additionally, the policy of a snake should only change such that it is permutated corresponding to the mirroring or rotation. This can be exploited for data augmentation by including all possible symmetric variants of the game board in the training data for you neural network. Depending on wether the enemy snakes are compressed into a single layer in the observation or stacked on top of each other, the permutation of these layers are also viable symmetries.
```python
num_symmetries = env.get_symmetry_count()  # by default always 8
obs, perm, inv_perm = env.get_obs(symmetry=1)  # specify the symmetry you want from 0-7
```
You can get the transformed observation by specifying the symmetry as shown in the example above. You will always get the action permutation and inverse permutation as an additional output of the step function, since with a symmetry applied the policy needs to be carefully permutated as well to keep everything correct.

# Limitations
There are some limitation to the current implementation which may or may not be fixed in the future:
- In the restricted mode, food is only visible in the observation within the view radius. Usually it should be visible outside the view radius in the spawn turn, but this does not happen currently, because our current implementation does not save the food spawn turn.

# References

This snake simulator was mainly used in the development of [Albatross](https://github.com/ymahlau/albatross). It has already been published there, but this standalone simulator is easier to install and easier to manage. It is targeted for anyone who wants to work with Battlesnake, but not necessarily use the Albatross method. You can cite this repository the same as the albatross repository with:

```
@inproceedings{mahlau_albatross_24,
  author = {Yannik Mahlau and Frederik Schubert and Bodo Rosenhahn},
  title = {Mastering Zero-Shot Interactions in Cooperative and Competitive Simultaneous Games},
  booktitle = {Proceedings of the 41st International Conference on Machine Learning (ICML)},
  year = {2024},
  month = jul
}
```
