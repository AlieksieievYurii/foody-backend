from django.urls import path

from users.views import UserListView, UserRoleView, UserRolesView, RegisterUserView, confirm_user, UserView, become_cook

urlpatterns = [
    path('register', RegisterUserView.as_view()),
    path('confirm/<str:email>/<str:token>', confirm_user),
    path('roles/', UserRolesView.as_view()),
    path('become-cook/', become_cook),
    path('role/<int:pk>', UserRoleView.as_view()),
    path('<int:pk>', UserView.as_view()),
    path('', UserListView.as_view()),
]
