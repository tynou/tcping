import enum


class Response(enum.Enum):
    PORT_OPEN = 0
    PORT_CLOSED = 1
    TIMEOUT = 2