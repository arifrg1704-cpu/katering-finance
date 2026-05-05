from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from django.http import HttpResponse
from django.template.loader import get_template
from decimal import Decimal
import os

from .models import Dinas, Client, Transaksi, TransaksiDetail, Pesanan, Penjualan, PenjualanDetail
from .forms import (
    DinasForm, ClientForm, TransaksiForm, TransaksiDetailFormSet, PesananForm,
    PenjualanForm, PenjualanDetailFormSet
)


# ─── Dashboard ────────────────────────────────────────────────────────────────

def get_pdfkit_config():
    """Helper to get pdfkit configuration for Windows/Linux."""
    import platform
    import os
    import pdfkit
    
    config = None
    if platform.system() == 'Windows':
        path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
        if not os.path.exists(path_wkhtmltopdf):
            path_wkhtmltopdf = r'C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe'
            
        if os.path.exists(path_wkhtmltopdf):
            config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    return config


@login_required
def dashboard(request):
    """Dashboard with summary totals."""
    if request.user.is_superuser:
        base_qs = TransaksiDetail.objects.all()
        recent = Transaksi.objects.select_related('client', 'client__dinas')[:10]
        total_transaksi = Transaksi.objects.count()
        total_dinas = Dinas.objects.count()
        total_client = Client.objects.count()
    else:
        base_qs = TransaksiDetail.objects.filter(transaksi__user=request.user)
        recent = Transaksi.objects.filter(user=request.user).select_related('client', 'client__dinas')[:10]
        total_transaksi = Transaksi.objects.filter(user=request.user).count()
        total_dinas = Dinas.objects.count()
        total_client = Client.objects.filter(user=request.user).count()

    totals = base_qs.aggregate(
        total_uang_masuk=Sum('uang_masuk'),
        total_pajak=Sum('pajak'),
        total_bersih=Sum('bersih'),
        total_fee_5=Sum('fee_5_persen'),
        total_fee_bersih_80=Sum('fee_bersih_80'),
        total_fee_pemilik_20=Sum('fee_pemilik_20'),
    )

    context = {
        'totals': {k: v or Decimal('0') for k, v in totals.items()},
        'recent': recent,
        'total_transaksi': total_transaksi,
        'total_dinas': total_dinas,
        'total_client': total_client,
    }
    return render(request, 'finance/dashboard.html', context)


# ─── Dinas CRUD ───────────────────────────────────────────────────────────────

@login_required
def dinas_list(request):
    queryset = Dinas.objects.all()
    q = request.GET.get('q', '')
    if q:
        queryset = queryset.filter(nama_dinas__icontains=q)
    return render(request, 'finance/dinas_list.html', {'dinas_list': queryset, 'q': q})


@login_required
def dinas_create(request):
    form = DinasForm(request.POST or None)
    if form.is_valid():
        dinas = form.save(commit=False)
        dinas.user = request.user
        dinas.save()
        messages.success(request, 'Dinas berhasil ditambahkan.')
        return redirect('finance:dinas_list')
    return render(request, 'finance/dinas_form.html', {'form': form, 'title': 'Tambah Dinas'})


@login_required
def dinas_update(request, pk):
    dinas = get_object_or_404(Dinas, pk=pk)
    form = DinasForm(request.POST or None, instance=dinas)
    if form.is_valid():
        form.save()
        messages.success(request, 'Dinas berhasil diperbarui.')
        return redirect('finance:dinas_list')
    return render(request, 'finance/dinas_form.html', {'form': form, 'title': 'Edit Dinas'})


@login_required
def dinas_delete(request, pk):
    dinas = get_object_or_404(Dinas, pk=pk)
    if request.method == 'POST':
        dinas.delete()
        messages.success(request, 'Dinas berhasil dihapus.')
        return redirect('finance:dinas_list')
    return render(request, 'finance/dinas_confirm_delete.html', {'object': dinas})


# ─── Client CRUD ──────────────────────────────────────────────────────────────

@login_required
def client_list(request):
    if request.user.is_superuser:
        queryset = Client.objects.select_related('dinas').all()
    else:
        queryset = Client.objects.select_related('dinas').filter(user=request.user)
        
    dinas_options = Dinas.objects.all()
    q = request.GET.get('q', '')
    dinas_id = request.GET.get('dinas', '')
    if q:
        queryset = queryset.filter(
            Q(nama_client__icontains=q) | Q(dinas__nama_dinas__icontains=q)
        )
    if dinas_id:
        queryset = queryset.filter(dinas_id=dinas_id)
        
    for d in dinas_options:
        d.selected = 'selected' if str(d.pk) == dinas_id else ''
    return render(request, 'finance/client_list.html', {
        'client_list': queryset,
        'q': q,
        'dinas_options': dinas_options,
    })


@login_required
def client_create(request):
    form = ClientForm(request.POST or None)
        
    if form.is_valid():
        client = form.save(commit=False)
        client.user = request.user
        client.save()
        messages.success(request, 'Client berhasil ditambahkan.')
        return redirect('finance:client_list')
    return render(request, 'finance/client_form.html', {'form': form, 'title': 'Tambah Client'})


@login_required
def client_update(request, pk):
    qs = Client.objects.all() if request.user.is_superuser else Client.objects.filter(user=request.user)
    client = get_object_or_404(qs, pk=pk)
    form = ClientForm(request.POST or None, instance=client)
    if form.is_valid():
        form.save()
        messages.success(request, 'Client berhasil diperbarui.')
        return redirect('finance:client_list')
    return render(request, 'finance/client_form.html', {'form': form, 'title': 'Edit Client'})


@login_required
def client_delete(request, pk):
    qs = Client.objects.all() if request.user.is_superuser else Client.objects.filter(user=request.user)
    client = get_object_or_404(qs, pk=pk)
    if request.method == 'POST':
        client.delete()
        messages.success(request, 'Client berhasil dihapus.')
        return redirect('finance:client_list')
    return render(request, 'finance/client_confirm_delete.html', {'object': client})


# ─── Pesanan CRUD ───────────────────────────────────────────────────────────────

@login_required
def pesanan_list(request):
    if request.user.is_superuser:
        queryset = Pesanan.objects.select_related('client', 'client__dinas').all()
    else:
        queryset = Pesanan.objects.select_related('client', 'client__dinas').filter(user=request.user)
        
    q = request.GET.get('q', '')
    if q:
        queryset = queryset.filter(
            Q(nomor_surat_pesanan__icontains=q) |
            Q(client__nama_client__icontains=q) |
            Q(client__dinas__nama_dinas__icontains=q)
        )
    return render(request, 'finance/pesanan_list.html', {
        'pesanan_list': queryset,
        'q': q,
    })


@login_required
def pesanan_create(request):
    form = PesananForm(request.POST or None)
    if not request.user.is_superuser:
        form.fields['client'].queryset = Client.objects.filter(user=request.user)
        
    if form.is_valid():
        pesanan = form.save(commit=False)
        pesanan.user = request.user
        pesanan.save()
        messages.success(request, 'Pesanan berhasil ditambahkan.')
        return redirect('finance:pesanan_list')
    return render(request, 'finance/pesanan_form.html', {'form': form, 'title': 'Tambah Pesanan'})


@login_required
def pesanan_update(request, pk):
    qs = Pesanan.objects.all() if request.user.is_superuser else Pesanan.objects.filter(user=request.user)
    pesanan = get_object_or_404(qs, pk=pk)
    form = PesananForm(request.POST or None, instance=pesanan)
    if not request.user.is_superuser:
        form.fields['client'].queryset = Client.objects.filter(user=request.user)
        
    if form.is_valid():
        form.save()
        messages.success(request, 'Pesanan berhasil diperbarui.')
        return redirect('finance:pesanan_list')
    return render(request, 'finance/pesanan_form.html', {'form': form, 'title': 'Edit Pesanan'})


@login_required
def pesanan_delete(request, pk):
    qs = Pesanan.objects.all() if request.user.is_superuser else Pesanan.objects.filter(user=request.user)
    pesanan = get_object_or_404(qs, pk=pk)
    if request.method == 'POST':
        pesanan.delete()
        messages.success(request, 'Pesanan berhasil dihapus.')
        return redirect('finance:pesanan_list')
    return render(request, 'finance/pesanan_confirm_delete.html', {'object': pesanan})


# ─── Penjualan CRUD ───────────────────────────────────────────────────────────────

@login_required
def penjualan_list(request):
    if request.user.is_superuser:
        queryset = Penjualan.objects.select_related('dinas').all()
    else:
        queryset = Penjualan.objects.select_related('dinas').filter(user=request.user)
        
    q = request.GET.get('q', '')
    if q:
        queryset = queryset.filter(
            Q(no_nota__icontains=q) |
            Q(dinas__nama_dinas__icontains=q)
        )
    return render(request, 'finance/penjualan_list.html', {
        'penjualan_list': queryset,
        'q': q,
    })


@login_required
def penjualan_create(request):
    # Dynamically create formset with extra=2 for initial data
    from django.forms import inlineformset_factory
    from .models import Penjualan, PenjualanDetail
    from .forms import PenjualanDetailForm
    
    CreateFormSet = inlineformset_factory(
        Penjualan, PenjualanDetail, form=PenjualanDetailForm, extra=2, can_delete=True
    )
    
    if request.method == 'POST':
        form = PenjualanForm(request.POST)
        formset = CreateFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            penjualan = form.save(commit=False)
            penjualan.user = request.user
            penjualan.save()
            formset.instance = penjualan
            formset.save()
            messages.success(request, 'Penjualan berhasil ditambahkan.')
            return redirect('finance:penjualan_list')
    else:
        form = PenjualanForm()
        initial_data = [
            {'nama_barang': 'Nasi Kotak', 'satuan': 30000, 'qty': 1},
            {'nama_barang': 'Kue Kotak', 'satuan': 15000, 'qty': 1},
        ]
        formset = CreateFormSet(initial=initial_data)
        
    return render(request, 'finance/penjualan_form.html', {
        'form': form,
        'formset': formset,
        'title': 'Tambah Penjualan',
    })


@login_required
def penjualan_update(request, pk):
    qs = Penjualan.objects.all() if request.user.is_superuser else Penjualan.objects.filter(user=request.user)
    penjualan = get_object_or_404(qs, pk=pk)
    if request.method == 'POST':
        form = PenjualanForm(request.POST, instance=penjualan)
        formset = PenjualanDetailFormSet(request.POST, instance=penjualan)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Penjualan berhasil diperbarui.')
            return redirect('finance:penjualan_list')
    else:
        form = PenjualanForm(instance=penjualan)
        formset = PenjualanDetailFormSet(instance=penjualan)
        
    return render(request, 'finance/penjualan_form.html', {
        'form': form,
        'formset': formset,
        'title': 'Edit Penjualan',
    })


@login_required
def penjualan_delete(request, pk):
    qs = Penjualan.objects.all() if request.user.is_superuser else Penjualan.objects.filter(user=request.user)
    penjualan = get_object_or_404(qs, pk=pk)
    if request.method == 'POST':
        penjualan.delete()
        messages.success(request, 'Penjualan berhasil dihapus.')
        return redirect('finance:penjualan_list')
    return render(request, 'finance/penjualan_confirm_delete.html', {'object': penjualan})


# ─── Transaksi CRUD ───────────────────────────────────────────────────────────

@login_required
def transaksi_list(request):
    if request.user.is_superuser:
        queryset = Transaksi.objects.select_related('client', 'client__dinas').all()
    else:
        queryset = Transaksi.objects.select_related('client', 'client__dinas').filter(user=request.user)
        
    dinas_options = Dinas.objects.all()
    q = request.GET.get('q', '')
    status = request.GET.get('status', '')
    dinas_id = request.GET.get('dinas', '')
    if q:
        queryset = queryset.filter(
            Q(client__nama_client__icontains=q) |
            Q(client__dinas__nama_dinas__icontains=q)
        )
    if status:
        queryset = queryset.filter(status_transfer=status)
    if dinas_id:
        queryset = queryset.filter(client__dinas_id=dinas_id)
        
    for d in dinas_options:
        d.selected = 'selected' if str(d.pk) == dinas_id else ''
    return render(request, 'finance/transaksi_list.html', {
        'transaksi_list': queryset,
        'q': q,
        'sudah_selected': 'selected' if status == 'Sudah Dibayar' else '',
        'belum_selected': 'selected' if status == 'Belum Dibayar' else '',
        'dinas_options': dinas_options,
    })


@login_required
def transaksi_create(request):
    if request.method == 'POST':
        form = TransaksiForm(request.POST)
        formset = TransaksiDetailFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            transaksi = form.save(commit=False)
            transaksi.user = request.user
            transaksi.save()
            formset.instance = transaksi
            formset.save()
            messages.success(request, 'Transaksi berhasil ditambahkan.')
            return redirect('finance:transaksi_report', pk=transaksi.pk)
    else:
        form = TransaksiForm()
        formset = TransaksiDetailFormSet()
        
    if not request.user.is_superuser:
        form.fields['client'].queryset = Client.objects.filter(user=request.user)
        
    return render(request, 'finance/transaksi_form.html', {
        'form': form,
        'formset': formset,
        'title': 'Tambah Transaksi',
    })


@login_required
def transaksi_update(request, pk):
    qs = Transaksi.objects.all() if request.user.is_superuser else Transaksi.objects.filter(user=request.user)
    transaksi = get_object_or_404(qs, pk=pk)
    if request.method == 'POST':
        form = TransaksiForm(request.POST, instance=transaksi)
        formset = TransaksiDetailFormSet(request.POST, instance=transaksi)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Transaksi berhasil diperbarui.')
            return redirect('finance:transaksi_report', pk=transaksi.pk)
    else:
        form = TransaksiForm(instance=transaksi)
        formset = TransaksiDetailFormSet(instance=transaksi)
        
    if not request.user.is_superuser:
        form.fields['client'].queryset = Client.objects.filter(user=request.user)
    return render(request, 'finance/transaksi_form.html', {
        'form': form,
        'formset': formset,
        'title': 'Edit Transaksi',
    })


@login_required
def transaksi_delete(request, pk):
    qs = Transaksi.objects.all() if request.user.is_superuser else Transaksi.objects.filter(user=request.user)
    transaksi = get_object_or_404(qs, pk=pk)
    if request.method == 'POST':
        transaksi.delete()
        messages.success(request, 'Transaksi berhasil dihapus.')
        return redirect('finance:transaksi_list')
    return render(request, 'finance/transaksi_confirm_delete.html', {'object': transaksi})


# ─── Report ───────────────────────────────────────────────────────────────────

@login_required
def transaksi_report(request, pk):
    qs = Transaksi.objects.select_related('client', 'client__dinas')
    if not request.user.is_superuser:
        qs = qs.filter(user=request.user)
    transaksi = get_object_or_404(qs, pk=pk)
    
    details = transaksi.details.all()
    
    return render(request, 'finance/transaksi_report.html', {
        'transaksi': transaksi,
        'details': details,
    })

@login_required
def fee_pemilik_list(request):
    if request.user.is_superuser:
        base_qs = TransaksiDetail.objects.select_related('transaksi', 'transaksi__client', 'transaksi__client__dinas').all()
    else:
        base_qs = TransaksiDetail.objects.select_related('transaksi', 'transaksi__client', 'transaksi__client__dinas').filter(transaksi__user=request.user)
        
    status = request.GET.get('status', '')
    if status == 'sudah':
        queryset = base_qs.filter(fee_pemilik_sudah_ditransfer=True)
    elif status == 'belum':
        queryset = base_qs.filter(fee_pemilik_sudah_ditransfer=False)
    else:
        queryset = base_qs
        
    if request.method == 'POST':
        # Handling the checklist toggle form
        action = request.POST.get('action')
        detail_ids = request.POST.getlist('detail_ids')
        if detail_ids:
            if action == 'mark_sudah':
                base_qs.filter(id__in=detail_ids).update(fee_pemilik_sudah_ditransfer=True)
                messages.success(request, f"{len(detail_ids)} fee pemilik ditandai sudah ditransfer.")
            elif action == 'mark_belum':
                base_qs.filter(id__in=detail_ids).update(fee_pemilik_sudah_ditransfer=False)
                messages.success(request, f"{len(detail_ids)} fee pemilik ditandai belum ditransfer.")
        return redirect(request.get_full_path())
        
    # Calculate total fee 20% for displayed rows
    total_fee_pemilik = queryset.aggregate(total=Sum('fee_pemilik_20'))['total'] or Decimal('0')
    
    return render(request, 'finance/fee_pemilik_list.html', {
        'fee_list': queryset,
        'status': status,
        'total_fee_pemilik': total_fee_pemilik,
    })

@login_required
def transaksi_report_simple(request, pk):
    qs = Transaksi.objects.select_related('client', 'client__dinas')
    if not request.user.is_superuser:
        qs = qs.filter(user=request.user)
    transaksi = get_object_or_404(qs, pk=pk)
    details = transaksi.details.all()
    return render(request, 'finance/transaksi_report_simple.html', {
        'transaksi': transaksi,
        'details': details,
    })

# ─── Export PDF ───────────────────────────────────────────────────────────────

@login_required
def export_pdf(request, pk):
    """Export a single transaction report to PDF."""
    try:
        import pdfkit
    except ImportError:
        messages.error(request, 'pdfkit belum diinstall. Jalankan: pip install pdfkit')
        return redirect('finance:transaksi_report', pk=pk)

    qs = Transaksi.objects.select_related('client', 'client__dinas')
    if not request.user.is_superuser:
        qs = qs.filter(user=request.user)
    transaksi = get_object_or_404(qs, pk=pk)
    details = transaksi.details.all()

    template = get_template('finance/pdf_report.html')
    html = template.render({
        'transaksi': transaksi,
        'details': details,
    })

    options = {
        'page-size': 'A4',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
    }
    
    pdf = pdfkit.from_string(html, False, options=options, configuration=get_pdfkit_config())

    response = HttpResponse(pdf, content_type='application/pdf')
    filename = f"laporan_{transaksi.client.nama_client}_{transaksi.tanggal}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response

@login_required
def export_pdf_simple(request, pk):
    """Export a simple single transaction report to PDF."""
    try:
        import pdfkit
    except ImportError:
        messages.error(request, 'pdfkit belum diinstall. Jalankan: pip install pdfkit')
        return redirect('finance:transaksi_report_simple', pk=pk)

    qs = Transaksi.objects.select_related('client', 'client__dinas')
    if not request.user.is_superuser:
        qs = qs.filter(user=request.user)
    transaksi = get_object_or_404(qs, pk=pk)
    details = transaksi.details.all()

    template = get_template('finance/pdf_report_simple.html')
    html = template.render({
        'transaksi': transaksi,
        'details': details,
    })

    options = {
        'page-size': 'A4',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
    }
    
    pdf = pdfkit.from_string(html, False, options=options, configuration=get_pdfkit_config())

    response = HttpResponse(pdf, content_type='application/pdf')
    filename = f"laporan_simple_{transaksi.client.nama_client}_{transaksi.tanggal}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

@login_required
def export_penjualan_pdf(request, pk):
    """Export a single penjualan to PDF (Nota)."""
    try:
        import pdfkit
    except ImportError:
        messages.error(request, 'pdfkit belum diinstall. Jalankan: pip install pdfkit')
        return redirect('finance:penjualan_list')

    qs = Penjualan.objects.select_related('dinas')
    if not request.user.is_superuser:
        qs = qs.filter(user=request.user)
    penjualan = get_object_or_404(qs, pk=pk)
    details = penjualan.details.all()

    # Convert logo to base64 for compatibility
    import base64
    from django.conf import settings
    
    # Try multiple possible paths for the logo
    possible_paths = [
        os.path.join(settings.BASE_DIR, 'static', 'images', 'logo_zahara.png'),
        os.path.join(settings.BASE_DIR, 'finance', 'static', 'finance', 'images', 'logo_zahara.png'),
    ]
    
    logo_base64 = ""
    found_path = None
    for path in possible_paths:
        if os.path.exists(path):
            found_path = path
            break
            
    if found_path:
        with open(found_path, "rb") as image_file:
            logo_base64 = base64.b64encode(image_file.read()).decode('utf-8')
    else:
        print(f"DEBUG: Logo not found in any of: {possible_paths}")
    
    template = get_template('finance/penjualan_pdf.html')
    html = template.render({
        'penjualan': penjualan,
        'details': details,
        'request': request,
        'logo_base64': logo_base64,
    })

    options = {
        'page-size': 'A4',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
    }
    
    try:
        pdf = pdfkit.from_string(html, False, options=options, configuration=get_pdfkit_config())
    except Exception as e:
        print(f"PDFKIT EXCEPTION: {e}")
        messages.error(request, f'Gagal membuat PDF. Error detail: {str(e)}')
        return redirect('finance:penjualan_list')

    response = HttpResponse(pdf, content_type='application/pdf')
    filename = f"Nota_{penjualan.no_nota}_{penjualan.dinas.nama_dinas}.pdf"

    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response
