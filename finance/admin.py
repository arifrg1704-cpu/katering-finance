from django.contrib import admin
from .models import Dinas, Client, Transaksi, TransaksiDetail


@admin.register(Dinas)
class DinasAdmin(admin.ModelAdmin):
    list_display = ('nama_dinas', 'alamat', 'created_at')
    search_fields = ('nama_dinas',)


class TransaksiDetailInline(admin.TabularInline):
    model = TransaksiDetail
    extra = 1
    readonly_fields = ('fee_5_persen', 'fee_bersih_80', 'fee_pemilik_20', 'bersih')
    fields = ('uang_masuk', 'pajak', 'fee_5_persen', 'fee_bersih_80', 'fee_pemilik_20', 'bersih')


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('nama_client', 'dinas', 'no_hp', 'created_at')
    list_filter = ('dinas',)
    search_fields = ('nama_client', 'dinas__nama_dinas')


@admin.register(Transaksi)
class TransaksiAdmin(admin.ModelAdmin):
    list_display = ('client', 'get_dinas', 'tanggal', 'status_transfer', 'created_at')
    list_filter = ('client__dinas', 'client', 'tanggal', 'status_transfer')
    search_fields = ('client__nama_client', 'client__dinas__nama_dinas')
    date_hierarchy = 'tanggal'
    inlines = [TransaksiDetailInline]

    @admin.display(description='Dinas', ordering='client__dinas__nama_dinas')
    def get_dinas(self, obj):
        return obj.client.dinas.nama_dinas


@admin.register(TransaksiDetail)
class TransaksiDetailAdmin(admin.ModelAdmin):
    list_display = (
        'transaksi', 'uang_masuk', 'fee_5_persen',
        'fee_bersih_80', 'fee_pemilik_20', 'pajak', 'bersih',
    )
    list_filter = (
        'transaksi__client__dinas',
        'transaksi__client',
        'transaksi__tanggal',
        'transaksi__status_transfer',
    )
    readonly_fields = ('fee_5_persen', 'fee_bersih_80', 'fee_pemilik_20', 'bersih')
