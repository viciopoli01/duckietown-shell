import os.path
from dataclasses import dataclass
from typing import Optional

import yaml

from . import dtslogger
from .constants import DTShellConstants
from .exceptions import ConfigNotPresent, InvalidConfig


@dataclass
class ShellConfig:
    token_dt1: Optional[str]  ## key
    docker_username: Optional[str]
    duckietown_version: Optional[str]  # daffy, master19, ...


@dataclass
class RepoInfo:
    username: str
    project: str
    branch: str


def RepoInfo_for_version(duckietown_version: str) -> RepoInfo:
    username = "duckietown"
    project = "duckietown-shell-commands"
    branch = duckietown_version
    return RepoInfo(username, project, branch)


def remoteurl_from_RepoInfo(ri: RepoInfo) -> str:
    return "https://github.com/%s/%s" % (ri.username, ri.project)


def get_shell_config_default() -> ShellConfig:
    return ShellConfig(token_dt1=None, docker_username=None, duckietown_version=None)


def get_config_path() -> str:
    root = DTShellConstants.ROOT
    config_path = os.path.expanduser(root)
    return config_path


def get_shell_config_file() -> str:
    config_path = get_config_path()
    config_file = os.path.join(config_path, "config.yaml")
    return config_file


def read_shell_config() -> ShellConfig:
    """ Reads the config file. Raises InvalidConfig or ConfigNotPresent. """
    config_file = get_shell_config_file()
    return read_shell_config_from_file(config_file)


def write_shell_config(shell_config: ShellConfig) -> None:
    """ Saves the she """
    config_file = get_shell_config_file()
    write_shell_config_to_file(shell_config, config_file)


DT1_TOKEN_CONFIG_KEY = DTShellConstants.DT1_TOKEN_CONFIG_KEY
CONFIG_DOCKER_USERNAME = DTShellConstants.CONFIG_DOCKER_USERNAME
CONFIG_DUCKIETOWN_VERSION = DTShellConstants.CONFIG_DUCKIETOWN_VERSION


def write_shell_config_to_file(shell_config: ShellConfig, filename: str) -> None:
    data = {
        DT1_TOKEN_CONFIG_KEY: shell_config.token_dt1,
        CONFIG_DOCKER_USERNAME: shell_config.docker_username,
        CONFIG_DUCKIETOWN_VERSION: shell_config.duckietown_version,
    }
    dn = os.path.dirname(filename)
    if not os.path.exists(dn):
        os.makedirs(dn)
    with open(filename, "w") as f:
        s = yaml.dump(data)
        f.write(s)


def read_shell_config_from_file(fn: str) -> ShellConfig:
    """ Raises InvalidConfig or ConfigNotPresent"""
    if not os.path.exists(fn):
        raise ConfigNotPresent(fn)

    with open(fn, "r") as fp:
        data = fp.read()

    try:
        d = yaml.load(data, Loader=yaml.Loader)
    except BaseException as e:
        msg = f"Cannot read config file {fn}"
        raise InvalidConfig(msg) from e

    if d is None:
        raise ConfigNotPresent(fn)

    if not isinstance(d, dict):
        msg = f"Invalid config file {fn}; expected dict, got {type(d)}"
        raise InvalidConfig(msg)

    token_dt1 = d.pop(DT1_TOKEN_CONFIG_KEY, None)
    docker_username = d.pop(CONFIG_DOCKER_USERNAME, None)
    duckietown_version = d.pop(CONFIG_DUCKIETOWN_VERSION, None)

    if d:
        msg = (
            f"The config file {fn} contains other options that I do not understand: {d}"
        )
        dtslogger.warning(msg)

    return ShellConfig(
        token_dt1=token_dt1,
        duckietown_version=duckietown_version,
        docker_username=docker_username,
    )
