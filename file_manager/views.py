from django.contrib import messages
from django.shortcuts import redirect, render
from .models import Attachment


def attachment_list(request):
    """Lista y carga archivos técnicos en el módulo reutilizable file_manager."""
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        reference_tag = request.POST.get('reference_tag', 'SPL-DOC').strip()
        category = request.POST.get('category', 'SPEC').strip()
        uploaded_by = request.POST.get('uploaded_by', 'Equipo SPL').strip()
        uploaded_file = request.FILES.get('file')

        if title:
            size_kb = max(1, (uploaded_file.size // 1024)) if uploaded_file else 64
            Attachment.objects.create(
                title=title,
                reference_tag=reference_tag or 'SPL-DOC',
                category=category,
                file=uploaded_file,
                uploaded_by=uploaded_by or 'Equipo SPL',
                size_kb=size_kb,
            )
            messages.success(request, f'Documento "{title}" registrado en file_manager.')
        else:
            messages.error(request, 'Ingrese un título para el archivo.')
        return redirect('file_manager:list')

    attachments = Attachment.objects.all()
    return render(
        request,
        'file_manager/list.html',
        {
            'attachments': attachments,
            'category_choices': Attachment.CATEGORY_CHOICES,
        },
    )
