class ScreException(Exception):
    pass


class GameException(ScreException):
    pass


class PlayerException(ScreException):
    pass


class DockerException(ScreException):
    pass


class ContainerException(DockerException):
    pass


class RealtimeOutedException(ContainerException):
    pass
