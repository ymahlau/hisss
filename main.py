
from hisss.game.battlesnake import UP, BattleSnakeGame
from hisss.game.config import BattleSnakeConfig, duel_config


def main():
    print("Hello from hisss!")
    cfg = duel_config()
    env = BattleSnakeGame(cfg)
    env.render()
    
    env.step(actions=(UP, UP))
    env.render()
    
    x = env.get_state()
    a = 1
    
    


if __name__ == "__main__":
    main()
