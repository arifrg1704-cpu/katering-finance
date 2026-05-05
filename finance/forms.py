from django import forms
from django.forms import inlineformset_factory
from .models import Dinas, Client, Transaksi, TransaksiDetail, Pesanan, Penjualan, PenjualanDetail


class BootstrapFormMixin:
    """Mixin to add Bootstrap CSS classes to form fields."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault('class', 'form-check-input')
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault('class', 'form-select')
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault('class', 'form-control')
                field.widget.attrs.setdefault('rows', 3)
            elif isinstance(field.widget, forms.DateInput):
                field.widget.attrs.setdefault('class', 'form-control')
                field.widget.attrs.setdefault('type', 'date')
            else:
                field.widget.attrs.setdefault('class', 'form-control')


class DinasForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Dinas
        fields = ['nama_dinas', 'alamat']


class ClientForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Client
        fields = ['dinas', 'nama_client', 'no_hp', 'keterangan']


class PesananForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Pesanan
        fields = ['nomor_surat_pesanan', 'tanggal_surat_pesanan', 'client', 'nilai_pesanan']
        widgets = {
            'tanggal_surat_pesanan': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'nilai_pesanan': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
            }),
        }


class TransaksiForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Transaksi
        fields = ['client', 'tanggal', 'status_transfer', 'catatan', 'biaya_materai', 'biaya_tte']
        widgets = {
            'tanggal': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'biaya_materai': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0',
                'id': 'id_biaya_materai',
            }),
            'biaya_tte': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0',
                'id': 'id_biaya_tte',
            }),
        }


class TransaksiDetailForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = TransaksiDetail
        fields = ['uang_masuk', 'pajak']
        widgets = {
            'uang_masuk': forms.NumberInput(attrs={
                'class': 'form-control uang-masuk-input',
                'step': '0.01',
                'min': '0',
            }),
            'pajak': forms.NumberInput(attrs={
                'class': 'form-control pajak-input',
                'step': '0.01',
                'min': '0',
            }),
        }


TransaksiDetailFormSet = inlineformset_factory(
    Transaksi,
    TransaksiDetail,
    form=TransaksiDetailForm,
    extra=1,
    can_delete=True,
)


class PenjualanForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Penjualan
        fields = ['dinas', 'tanggal', 'no_nota']
        widgets = {
            'tanggal': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        }


class PenjualanDetailForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = PenjualanDetail
        fields = ['qty', 'nama_barang', 'satuan']
        widgets = {
            'qty': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'satuan': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        }


PenjualanDetailFormSet = inlineformset_factory(
    Penjualan,
    PenjualanDetail,
    form=PenjualanDetailForm,
    extra=1,
    can_delete=True,
)
