from .transaksi import Transaksi

class TransaksiMembership(Transaksi):
    def __init__(self, transaksi_id, member_id, harga):
        super().__init__(transaksi_id, member_id)
        self.__harga = harga

    def hitung_total(self) -> int:
        return self.__harga

    def jenis(self) -> str:
        return "MEMBERSHIP"
