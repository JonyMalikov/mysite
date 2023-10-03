import markdown
from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords_html
from django.urls import reverse_lazy

from .models import Post


class LatestPostsFeed(Feed):
    """
    Новостныe ленты для постов блога.
    """

    title = "My blog"
    link = reverse_lazy("blog:post_list")
    description = "New posts of my blog."

    def items(self):
        """Возвращает 5 самых недавно опубликованных постов."""
        return Post.published.all()[:5]

    def item_title(self, item):
        """Возвращает заголовок поста."""
        return item.title

    def item_description(self, item):
        """Возвращает описание поста."""
        return truncatewords_html(markdown.markdown(item.body), 30)


def item_pubdate(self, item):
    """Возвращает дату публикации поста."""
    return item.publish
