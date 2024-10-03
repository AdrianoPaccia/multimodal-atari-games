def build_env_pendulum(config, noise_freq=0.0,noise_types:list=['nonoise'], render=False):

    import multimodal_atari_games.multimodal_atari_games.pendulum.pendulum_env as ps
    from multimodal_atari_games.multimodal_atari_games.noise.noise import ImageNoise, SoundNoise, StateNoise
    kwargs = {

    }
    return ps.PendulumSound(
        original_frequency=config.original_frequency,
        sound_vel=config.sound_velocity,
        sound_receivers=[
            ps.SoundReceiver(ps.SoundReceiver.Location[ss])
            for ss in config.sound_receivers
        ],
        noise_generators={
            'rgb': ImageNoise(noise_types=noise_types,game='pendulum',
                       **{'bounds': (config.low_bounds['rgb'], config.high_bounds['rgb'])}),
            'sound': SoundNoise(noise_types=noise_types, game='pendulum',
                       **{'bounds': (config.low_bounds['sound'], config.high_bounds['sound'])}),
            'state': StateNoise(noise_types=noise_types, game='pendulum',
                       **{'low_bounds': (config.low_bounds['state'], config.high_bounds['state'])}),

        },
        noise_frequency=noise_freq,
        rendering_mode='human' if render else 'rgb_array',
    )




def build_env_atari(game, noise_freq=0.0, noise_types:list=['nonoise'], render=False):
    from multimodal_atari_games.multimodal_atari_games.atari.atari_env import AtariImageRam
    from multimodal_atari_games.multimodal_atari_games.noise.image_noise import ImageNoise
    from multimodal_atari_games.multimodal_atari_games.noise.ram_noise import RamNoise
    return AtariImageRam(
        game=game,
        difficulty=None,
        image_noise_generator=ImageNoise(noise_types=noise_types, game=game),
        ram_noise_generator=RamNoise(noise_types=noise_types, game=game),
        noise_frequency=noise_freq
    )

def build_env_mujoco(game, noise_freq=0.0, noise_types:list=['nonoise'], max_episode_steps=1000, render=False, **kwargs):
    from multimodal_atari_games.multimodal_atari_games.noise.image_noise import ImageNoise

    if game=='cheetah':
        from multimodal_atari_games.multimodal_atari_games.mujoco.cheetah_env import CheetahImageConfiguration

        return CheetahImageConfiguration(
                render_mode='rgb_array', #None,
                image_noise_generator=ImageNoise(game='cheetah', noise_types=noise_types),
                max_episode_steps=max_episode_steps,
                noise_frequency=noise_freq
                #ram_noise_generator=RamNoise(['random_obs'], 1.0),
            )


    elif game=='humanoid':
        from multimodal_atari_games.multimodal_atari_games.mujoco.humanoid_env import HumanoidImageConfiguration

        return HumanoidImageConfiguration(
            render_mode='rgb_array', #None,
            image_noise_generator=ImageNoise(game='humanoid', noise_types=noise_types),
            max_episode_steps=max_episode_steps,
            noise_frequency=noise_freq
            # ram_noise_generator=RamNoise(['random_obs'], 1.0)
        )

    else:
        raise ValueError(f'{game} is not a valid game (cheetah, humanoid)!')



def build_env_robotics(game, noise_freq=0.0, noise_types:list=['nonoise'], max_episode_steps=1000, render=False, **kwargs):
    from multimodal_atari_games.multimodal_atari_games.noise.image_noise import ImageNoise

    if game=='fetch_reach':
        from multimodal_atari_games.multimodal_atari_games.robotics.fetch_env import FetchReachImageConfiguration
        return FetchReachImageConfiguration(
            render_mode='rgb_array',
            image_noise_generator=ImageNoise(game='fetch_reach', noise_types=noise_types),
            max_episode_steps=max_episode_steps,
            #ram_noise_generator=RamNoise(['random_obs'], 1.0),
            reward_type=kwargs['reward_type']
        )
    if game=='fetch_push':
        from multimodal_atari_games.multimodal_atari_games.robotics.fetch_env import FetchPushImageConfiguration
        return FetchPushImageConfiguration(
            render_mode='rgb_array',
            image_noise_generator=ImageNoise(game='fetch_push', noise_types=noise_types),
            max_episode_steps=max_episode_steps,
            #ram_noise_generator=RamNoise(['random_obs'], 1.0),
            reward_type=kwargs['reward_type']
        )

    elif game.startswith('antmaze'):
        from multimodal_atari_games.multimodal_atari_games.robotics.ant_maze_env import AntMazeImageConfiguration
        return AntMazeImageConfiguration(
            render_mode='rgb_array',
            image_noise_generator=ImageNoise(game=game, noise_types=noise_types),
            max_episode_steps=max_episode_steps,
            # ram_noise_generator=RamNoise(['random_obs'], 1.0)
            map_size=kwargs['map_size'],
            reward_type=kwargs['reward_type']
        )

    elif game.startswith('pointmaze'):
        from multimodal_atari_games.multimodal_atari_games.robotics.point_maze_env import PointMazeImageConfiguration
        return PointMazeImageConfiguration(
            render_mode='rgb_array',
            image_noise_generator=ImageNoise(game=game, noise_types=noise_types),
            max_episode_steps=max_episode_steps,
            # ram_noise_generator=RamNoise(['random_obs'], 1.0)
            map_size=kwargs['map_size'],
            reward_type=kwargs['reward_type']
        )
    else:
        raise ValueError(f'{game} is not a valid game (fetch_reach, fetch_psuh, antmaze, pointmaze)!')
