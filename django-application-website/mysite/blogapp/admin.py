from django.contrib import admin
from .models import Article, Author, Category, Tag


class TagInline(admin.StackedInline):
    model = Article.tags.through


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    inlines = [
        TagInline,
    ]
    list_display = "id", "title", "content", "pub_date", "author_verbose", "category_verbose"

    def get_queryset(self, request):
        return Article.objects.select_related("author", "category").prefetch_related("tags")

    def author_verbose(self, obj: Article) -> str:
        return obj.author.name

    def category_verbose(self, obj: Article) -> str:
        return obj.category.name


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = "pk", "name", "bio"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = "pk", "name"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = "pk", "name"
