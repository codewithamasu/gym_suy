from abc import ABC, abstractmethod

class Transaksi(ABC):
    def __init__(self, transaksi_id, member_id):
        self._transaksi_id = transaksi_id
        self._member_id = member_id

    @abstractmethod
    def hitung_total(self) -> int:
        pass

    @abstractmethod
    def jenis(self) -> str:
        pass

    @property
    def transaksi_id(self):
        return self._transaksi_id

    @property
    def member_id(self):
        return self._member_id
