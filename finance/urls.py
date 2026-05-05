from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Dinas
    path('dinas/', views.dinas_list, name='dinas_list'),
    path('dinas/tambah/', views.dinas_create, name='dinas_create'),
    path('dinas/<int:pk>/edit/', views.dinas_update, name='dinas_update'),
    path('dinas/<int:pk>/hapus/', views.dinas_delete, name='dinas_delete'),

    # Client
    path('client/', views.client_list, name='client_list'),
    path('client/tambah/', views.client_create, name='client_create'),
    path('client/<int:pk>/edit/', views.client_update, name='client_update'),
    path('client/<int:pk>/hapus/', views.client_delete, name='client_delete'),

    # Pesanan
    path('pesanan/', views.pesanan_list, name='pesanan_list'),
    path('pesanan/tambah/', views.pesanan_create, name='pesanan_create'),
    path('pesanan/<int:pk>/edit/', views.pesanan_update, name='pesanan_update'),
    path('pesanan/<int:pk>/hapus/', views.pesanan_delete, name='pesanan_delete'),

    # Penjualan
    path('penjualan/', views.penjualan_list, name='penjualan_list'),
    path('penjualan/tambah/', views.penjualan_create, name='penjualan_create'),
    path('penjualan/<int:pk>/edit/', views.penjualan_update, name='penjualan_update'),
    path('penjualan/<int:pk>/hapus/', views.penjualan_delete, name='penjualan_delete'),
    path('penjualan/<int:pk>/export-pdf/', views.export_penjualan_pdf, name='export_penjualan_pdf'),

    # Transaksi
    path('transaksi/', views.transaksi_list, name='transaksi_list'),
    path('fee-pemilik/', views.fee_pemilik_list, name='fee_pemilik_list'),
    path('transaksi/tambah/', views.transaksi_create, name='transaksi_create'),
    path('transaksi/<int:pk>/edit/', views.transaksi_update, name='transaksi_update'),
    path('transaksi/<int:pk>/hapus/', views.transaksi_delete, name='transaksi_delete'),
    path('transaksi/<int:pk>/laporan/', views.transaksi_report, name='transaksi_report'),
    path('transaksi/<int:pk>/laporan-simple/', views.transaksi_report_simple, name='transaksi_report_simple'),
    path('transaksi/<int:pk>/export-pdf/', views.export_pdf, name='export_pdf'),
    path('transaksi/<int:pk>/export-pdf-simple/', views.export_pdf_simple, name='export_pdf_simple'),
]
