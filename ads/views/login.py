from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib import messages

def user_login(request):
    """
    Vista para el formulario de inicio de sesión.
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user) # Inicia sesión al usuario
            messages.success(request, f"¡Bienvenido, {user.username}!")
            # Redirige al usuario a la página de estadísticas después de iniciar sesión
            # o a la URL especificada en LOGIN_REDIRECT_URL en settings.py
            return redirect('ads:ad_statistics')
        messages.error(request, "Nombre de usuario o contraseña incorrectos.")
    else:
        form = AuthenticationForm() # Formulario vacío para GET request

    return render(request, 'ads/login.html', {'form': form})


@login_required # Opcional: También puedes proteger el logout si quieres que solo usuarios logueados puedan hacer logout.
def user_logout(request):
    """
    Vista para cerrar la sesión del usuario.
    """
    logout(request) # Cierra la sesión del usuario
    messages.info(request, "Has cerrado tu sesión exitosamente.")
    # Redirige a la página de login después de cerrar sesión
    return redirect('ads:login')
