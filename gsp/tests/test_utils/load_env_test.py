from gsp.utils.load_env import load_env_variables


def test_load_env_successful():
    envs = load_env_variables()

    assert len(envs) == 4
