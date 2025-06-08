from django.urls import path

from . import views as view

urlpatterns = [
  path('', view.Home, name='root'),
  path('home', view.Home, name='home'),
  path('home/prev', view.Prev, name='home-prev'),
  path('home/next', view.Home, name='home-next'),
  path('team/scorecard/update', view.AjaxUpdateScores, name='update-scores'),
  path('team/scorecard/<team_name>', view.ScoreCardStaff, name='score-card'),
  path('team/scorecard', view.ScoreCard, name='score-card'),
  path('admin/actions', view.AdminActions, name='admin-actions'),
  path('create-table', view.CreateTable, name='create-table'),
  path('verify-table', view.VerifyTable, name='verify-table'),
  path('team/login', view.TeamLogin, name='team-login'),
  path('team/logout', view.TeamLogout, name='team-logout'),
  path('team/info/mkjb3f453e2jpxdjp8dy', view.AjaxTeamInfo, name='team-info'),
  path('teams', view.TeamsList, name='teams-list'),
  path('results', view.FinalizeResults, name='results'),
  path('past/results', view.PastTouraments, name='past-results'),
  path('error', view.Error, name='error'),
  path('player/select', view.PlayerSelect, name='player-select'),
  path('player/profile/<int:id>', view.PlayerProfileID, name='player-profile-id'),
  path('player/profile/<str:name>', view.PlayerProfileName, name='player-profile-name'),
  # path('email/contact/<int:id>',     view.EmailContact, name='email-contact-id'),
  # path('email/contact',              view.EmailContact, name='email-contact-select'),
]

