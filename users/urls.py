from django.conf.urls import url

from users.views import CreateUserView, UserListView

urlpatterns = [
    url('register', CreateUserView.as_view()),
    url('', UserListView.as_view()),

]
