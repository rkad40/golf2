from django.shortcuts import redirect, render

from .models import Article

def ArticleView(request, key):
    # Try to load the page, either by id or slug.
    try:
        if type(key) == int:
            article = Article.objects.get(id=key)
        else:
            article = Article.objects.get(slug=key)
    except:
        request.session['error'] = f'Invalid page "{key}".'
        return redirect('error')
        
    article.content = article.content.replace(r'<p>---</p>', '')
    
    if article.active == False and not request.user.is_authenticated:
        request.session['error'] = f'Invalid page "{key}".'
        return redirect('error')

    ## Render view.
    context = dict(
        title=article.title,
        article=article
    )
    return render(request, template_name='base.html', context=context)
