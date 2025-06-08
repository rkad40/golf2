from django.urls import path

from . import views as view

urlpatterns = [
  path('article/view/<int:key>', view.ArticleView, name='article-view'),
  path('article/view/<str:key>', view.ArticleView, name='article-view'),
]
