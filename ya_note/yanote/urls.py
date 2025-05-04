from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.urls import include, path
from django.views.decorators.http import require_POST
from django.views.generic import CreateView

urlpatterns = [
    path('', include('notes.urls')),
    path('admin/', admin.site.urls),
]

auth_urls = ([
    path(
        'login/',
        auth_views.LoginView.as_view(),
        name='login',
    ),
    path(
        'logout/',
        require_POST(
            login_required(
                auth_views.LogoutView.as_view(
                    next_page='notes:home',
                ),
                login_url='users:login',
                redirect_field_name='next',
            )
        ),
        name='logout',
    ),
    path(
        'signup/',
        CreateView.as_view(
            form_class=UserCreationForm,
            success_url='/',
            template_name='registration/signup.html',
        ),
        name='signup'
    ),
], 'users')

urlpatterns += [path('auth/', include(auth_urls))]
