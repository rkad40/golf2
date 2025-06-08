from django.urls import path

from . import views as view

urlpatterns = [
  path('admin/login',                             view.LoginUser,               name='admin-user-login'),
  path('staff/dashboard',                         view.StaffDashboard,          name='staff-dashboard'),
  path('user/login/',                             view.LoginUser,               name='user-login'),
  path('user/logout/',                            view.LogoutUser,              name='user-logout'),
  path('user/profile/edit/',                      view.UserProfile,             name='user-edit-profile'),
  path('user/password/change/',                   view.ChangePassword,          name='user-change-password'),
  path('user/password/reset/',                    view.PasswordResetInit,       name='user-password-reset-init'),
  path('user/password/reset/wait/',               view.PasswordResetEmailSent,  name='user-password-reset-wait'),
  path('user/password/reset/<str:token>/',        view.PasswordResetFinal,      name='user-password-reset-final'),
  path('user/register/',                          view.UserSignup,              name='user-register'),
  path('user/activate/<str:uidb64>/<str:token>/', view.ActivateAccount,         name='user-activate')
]
