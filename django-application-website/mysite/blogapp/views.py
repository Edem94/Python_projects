from django.contrib.syndication.views import Feed
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Article
from django.urls import reverse, reverse_lazy


class ArticlesListView(ListView):
    # template_name = "blogapp/article_list.html"
    # context_object_name = "articles"
    queryset = (
        Article.objects
        .select_related("author", "category")
        .prefetch_related("tags")
        .defer('content')
        .filter(pub_date__isnull=False)
        .order_by('-pub_date')
    )


class ArticleDetailView(DetailView):
    model = Article


class LatestArticlesFeed(Feed):
    title = 'Blog articles (Latest)'
    link = reverse_lazy('blogapp:articles')
    description = "Updates on changes and addition blog articles"

    def items(self):
        return (
            Article.objects
            .select_related("author", "category")
            .prefetch_related("tags")
            .defer('content')
            .filter(pub_date__isnull=False)
            .order_by('-pub_date')[:5]
        )

    def item_title(self, item: Article):
        return item.title

    def item_description(self, item: Article):
        return item.content[:200]

    # # item_link is only needed if NewsItem has no get_absolute_url method.
    # def item_link(self, item: Article):
    #     return reverse('blogapp:article', kwargs={'pk': item.pk})
