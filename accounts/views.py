from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from .models import UserProfile


def user_directory(request):
    """Lista y registra perfiles de usuario (app reutilizable independiente del núcleo)."""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        role = request.POST.get('role', 'ESTUDIANTE').strip()
        department = request.POST.get('department', 'Software — UNEMI').strip()

        if username and first_name:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email or f'{username}@unemi.edu.ec',
                },
            )
            if created:
                user.set_password('Unemi2026*')
                user.save()
                UserProfile.objects.create(
                    user=user,
                    role=role,
                    department=department,
                    institutional_id=f'UNEMI-{user.id:04d}',
                )
                messages.success(request, f'Usuario "{username}" agregado al módulo reutilizable accounts.')
            else:
                messages.warning(request, f'El usuario "{username}" ya existe en el directorio.')
        else:
            messages.error(request, 'Complete al menos el nombre de usuario y el primer nombre.')
        return redirect('accounts:directory')

    profiles = UserProfile.objects.select_related('user').all()
    return render(
        request,
        'accounts/directory.html',
        {
            'profiles': profiles,
            'role_choices': UserProfile.ROLE_CHOICES,
        },
    )
