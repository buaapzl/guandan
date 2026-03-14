from dataclasses import dataclass
from typing import Optional

@dataclass
class TrainConfig:
    algorithm: str = "PPO"
    total_timesteps: int = 1_000_000
    model_kwargs: Optional[dict] = None
    save_freq: int = 10000
    eval_freq: int = 50000
    save_path: str = "./models"
    seed: int = 42

    def __post_init__(self):
        if self.model_kwargs is None:
            self.model_kwargs = {
                'policy': 'MlpPolicy',
                'learning_rate': 3e-4,
                'n_steps': 2048,
                'batch_size': 64,
                'n_epochs': 10,
                'gamma': 0.99,
            }
