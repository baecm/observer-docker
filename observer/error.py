class ObserverException(Exception):
    pass


class GameException(ObserverException):
    pass


class PlayerException(ObserverException):
    pass


class DockerException(ObserverException):
    pass


class ContainerException(DockerException):
    pass


class RealtimeOutedException(ContainerException):
    pass
