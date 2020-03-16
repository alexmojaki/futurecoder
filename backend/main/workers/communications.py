from abc import ABC, abstractmethod


class AbstractCommunications(ABC):
    @abstractmethod
    def send_entry(self, entry): ...

    @abstractmethod
    def recv_entry(self): ...

    @abstractmethod
    def send_result(self, queue_name, result): ...

    @abstractmethod
    def recv_result(self, queue_name): ...

    @abstractmethod
    def make_master_side_communications(self) -> "AbstractCommunications": ...


class ThreadCommunications(AbstractCommunications):
    def __init__(self):
        from multiprocessing.dummy import Pipe

        self.server_connection, self.child_connection = Pipe()

    def make_master_side_communications(self):
        return self

    def send_entry(self, entry):
        self.server_connection.send(entry)

    def recv_entry(self):
        return self.child_connection.recv()

    # TODO doesn't handle multiple users (queues)
    def send_result(self, queue_name, result):
        self.child_connection.send(result)

    def recv_result(self, queue_name):
        return self.server_connection.recv()
