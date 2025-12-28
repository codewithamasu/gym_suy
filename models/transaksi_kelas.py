from .transaksi import Transaksi

class TransaksiKelas(Transaksi):
    def __init__(self, transaksi_id, member_id, tarif):
        super().__init__(transaksi_id, member_id)
        self.__tarif = tarif  # encapsulation

    def hitung_total(self) -> int:
        return self.__tarif

    def jenis(self) -> str:
        return "KELAS"
