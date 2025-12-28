class Pembayaran:
    def __init__(self, transaksi):
        self.__transaksi = transaksi

    @property
    def total(self):
        return self.__transaksi.hitung_total()

    def proses(self, uang_diterima: int) -> int:
        if uang_diterima < self.total:
            raise ValueError("Uang diterima kurang")
        return uang_diterima - self.total

    @property
    def jenis_transaksi(self):
        return self.__transaksi.jenis()
