from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal


class Dinas(models.Model):
    """Model untuk Organisasi Perangkat Daerah (Dinas)."""
    nama_dinas = models.CharField(max_length=255, verbose_name="Nama Dinas")
    alamat = models.TextField(verbose_name="Alamat")
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=2, verbose_name="Dibuat Oleh")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Dinas"
        verbose_name_plural = "Dinas"
        ordering = ['nama_dinas']

    def __str__(self):
        return self.nama_dinas


class Client(models.Model):
    """Model untuk Client yang terkait dengan Dinas."""
    dinas = models.ForeignKey(
        Dinas,
        on_delete=models.CASCADE,
        related_name='clients',
        verbose_name="Dinas",
    )
    nama_client = models.CharField(max_length=255, verbose_name="Nama Client")
    no_hp = models.CharField(
        max_length=20, blank=True, default='', verbose_name="No. HP"
    )
    keterangan = models.TextField(
        blank=True, default='', verbose_name="Keterangan"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=2, verbose_name="Dibuat Oleh")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Client"
        ordering = ['nama_client']

    def __str__(self):
        return f"{self.nama_client} ({self.dinas.nama_dinas})"


class Pesanan(models.Model):
    """Model untuk Pesanan."""
    nomor_surat_pesanan = models.CharField(max_length=255, verbose_name="Nomor Surat Pesanan")
    tanggal_surat_pesanan = models.DateField(verbose_name="Tanggal Surat Pesanan")
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='pesanan_list',
        verbose_name="Client (FK Client)",
    )
    nilai_pesanan = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0'),
        verbose_name="Nilai Pesanan (Rp)",
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=2, verbose_name="Dibuat Oleh")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Pesanan"
        verbose_name_plural = "Pesanan"
        ordering = ['-tanggal_surat_pesanan']

    def __str__(self):
        return f"{self.nomor_surat_pesanan} - {self.client.nama_client}"


class Transaksi(models.Model):
    """Model header transaksi keuangan."""
    STATUS_CHOICES = [
        ('Sudah Dibayar', 'Sudah Dibayar'),
        ('Belum Dibayar', 'Belum Dibayar'),
    ]

    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='transaksi_list',
        verbose_name="Client",
    )
    tanggal = models.DateField(verbose_name="Tanggal")
    status_transfer = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Belum Dibayar',
        verbose_name="Status Pembayaran",
    )
    catatan = models.TextField(
        blank=True, default='', verbose_name="Catatan"
    )
    biaya_materai = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0'),
        blank=True, verbose_name="Biaya Materai",
    )
    biaya_tte = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0'),
        blank=True, verbose_name="Biaya TTE",
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=2, verbose_name="Dibuat Oleh")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Transaksi"
        verbose_name_plural = "Transaksi"
        ordering = ['-tanggal']

    def __str__(self):
        return f"Transaksi {self.client.nama_client} - {self.tanggal}"

    @property
    def total_uang_masuk(self):
        return self.details.aggregate(
            total=models.Sum('uang_masuk')
        )['total'] or Decimal('0')

    @property
    def total_fee_5_persen(self):
        return self.details.aggregate(
            total=models.Sum('fee_5_persen')
        )['total'] or Decimal('0')

    @property
    def total_fee_bersih_80(self):
        return self.details.aggregate(
            total=models.Sum('fee_bersih_80')
        )['total'] or Decimal('0')

    @property
    def total_fee_pemilik_20(self):
        return self.details.aggregate(
            total=models.Sum('fee_pemilik_20')
        )['total'] or Decimal('0')

    @property
    def total_pajak(self):
        return self.details.aggregate(
            total=models.Sum('pajak')
        )['total'] or Decimal('0')

    @property
    def total_potongan(self):
        return (self.biaya_materai or Decimal('0')) + (self.biaya_tte or Decimal('0'))

    @property
    def total_bersih(self):
        subtotal = self.details.aggregate(
            total=models.Sum('bersih')
        )['total'] or Decimal('0')
        return subtotal - self.total_potongan

    @property
    def total_bersih_alt(self):
        return self.total_uang_masuk - self.total_fee_pemilik_20 - self.total_pajak - self.total_potongan


class TransaksiDetail(models.Model):
    """Model detail transaksi — baris pendapatan."""
    transaksi = models.ForeignKey(
        Transaksi,
        on_delete=models.CASCADE,
        related_name='details',
        verbose_name="Transaksi",
    )
    uang_masuk = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0'),
        verbose_name="Uang Masuk",
    )
    fee_5_persen = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0'),
        verbose_name="Fee 5%", editable=False,
    )
    fee_bersih_80 = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0'),
        verbose_name="Fee Bersih 80%", editable=False,
    )
    fee_pemilik_20 = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0'),
        verbose_name="Fee Pemilik 20%", editable=False,
    )
    fee_pemilik_sudah_ditransfer = models.BooleanField(
        default=False, verbose_name="Fee Pemilik Sudah Ditransfer?"
    )
    pajak = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0'),
        verbose_name="Pajak", blank=True, null=True
    )
    bersih = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0'),
        verbose_name="Bersih", editable=False,
    )

    @property
    def bersih_alt(self):
        return self.uang_masuk - self.fee_pemilik_20 - self.pajak

    class Meta:
        verbose_name = "Detail Transaksi"
        verbose_name_plural = "Detail Transaksi"

    def __str__(self):
        return f"Detail #{self.pk} - Rp {self.uang_masuk:,.0f}"

    def save(self, *args, **kwargs):
        """Auto-calculate fee fields before saving."""
        if self.pajak is None:
            self.pajak = Decimal('0')
            
        self.fee_5_persen = self.uang_masuk * Decimal('0.05')
        self.fee_bersih_80 = self.fee_5_persen * Decimal('0.8')
        self.fee_pemilik_20 = self.fee_5_persen * Decimal('0.2')
        self.bersih = self.uang_masuk - self.fee_5_persen - self.pajak
        super().save(*args, **kwargs)


class Penjualan(models.Model):
    """Model header penjualan."""
    dinas = models.ForeignKey(
        Dinas,
        on_delete=models.CASCADE,
        related_name='penjualan_list',
        verbose_name="Tuan / Toko (Dinas)",
    )
    tanggal = models.DateField(verbose_name="Tanggal")
    no_nota = models.CharField(max_length=50, verbose_name="No. Nota")
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=2, verbose_name="Dibuat Oleh")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Penjualan"
        verbose_name_plural = "Penjualan"
        ordering = ['-tanggal', '-no_nota']

    def __str__(self):
        return f"Nota {self.no_nota} - {self.dinas.nama_dinas}"

    @property
    def total_jumlah(self):
        return self.details.aggregate(
            total=models.Sum('jumlah')
        )['total'] or Decimal('0')


class PenjualanDetail(models.Model):
    """Model detail penjualan."""
    penjualan = models.ForeignKey(
        Penjualan,
        on_delete=models.CASCADE,
        related_name='details',
        verbose_name="Penjualan",
    )
    qty = models.IntegerField(verbose_name="QTY", default=1)
    nama_barang = models.CharField(max_length=255, verbose_name="Nama Barang")
    satuan = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0'),
        verbose_name="Satuan (Harga)",
    )
    jumlah = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0'),
        verbose_name="Jumlah", editable=False,
    )

    class Meta:
        verbose_name = "Detail Penjualan"
        verbose_name_plural = "Detail Penjualan"

    def __str__(self):
        return f"{self.nama_barang} - {self.qty}"

    def save(self, *args, **kwargs):
        self.jumlah = Decimal(self.qty) * self.satuan
        super().save(*args, **kwargs)

