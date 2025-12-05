
from hisss.game.battlesnake import LEFT, UP, BattleSnakeGame
from hisss.game.config import BattleSnakeConfig, duel_config, encoding_layer_indices, restricted_duel_config


def main():
    print("Hello from hisss!")
    cfg = restricted_duel_config()
    env = BattleSnakeGame(cfg)
    env.render()
    
    rewards, done, _ = env.step(actions=(UP, UP))
    rewards, done, _ = env.step(actions=(LEFT, LEFT))
    env.render()
    # env.reset()
    obs, _, _ = env.get_obs()
    explanation = encoding_layer_indices(cfg)
    
    x = env.get_state()
    a = 1
    
    


if __name__ == "__main__":
    main()
