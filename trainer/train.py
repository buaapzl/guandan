import os
from stable_baselines3 import PPO, A2C
from guandan_gym.env import GuandanEnv
from trainer.config import TrainConfig

def train(config: TrainConfig):
    """训练主函数"""
    # 创建环境
    env = GuandanEnv()

    # 创建模型
    if config.algorithm == "PPO":
        model = PPO("MlpPolicy", env, verbose=1, **config.model_kwargs)
    elif config.algorithm == "A2C":
        model = A2C("MlpPolicy", env, verbose=1, **config.model_kwargs)
    else:
        raise ValueError(f"Unknown algorithm: {config.algorithm}")

    # 训练
    model.learn(total_timesteps=config.total_timesteps)

    # 保存
    os.makedirs(config.save_path, exist_ok=True)
    model.save(os.path.join(config.save_path, f"{config.algorithm}_guandan"))

    return model

if __name__ == '__main__':
    config = TrainConfig(
        algorithm="PPO",
        total_timesteps=100000,
    )
    train(config)
