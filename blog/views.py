from django.contrib.postgres.search import (
    SearchQuery,
    SearchRank,
    SearchVector,
)
from django.core.mail import send_mail
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from taggit.models import Tag

from blog.forms import CommentForm, EmailPostForm, SearchForm
from blog.models import Post


def post_list(request, tag_slug=None):
    """
    Представление списка постов
    """
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get("page", 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, "blog/post/list.html", {"posts": posts, "tag": tag})


def post_detail(request, year, month, day, post):
    """
    Представление полнлного поста
    """
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day,
    )
    comments = post.comments.filter(active=True)
    form = CommentForm()
    post_tags_ids = post.tags.values_list("id", flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(
        id=post.id
    )
    similar_posts = similar_posts.annotate(same_tags=Count("tags")).order_by(
        "-same_tags", "-publish"
    )[:4]
    return render(
        request,
        "blog/post/detail.html",
        {
            "post": post,
            "comments": comments,
            "form": form,
            "similar_posts": similar_posts,
        },
    )


def post_share(request, post_id):
    """
    Представление рекомендации постов по электронной почте
    """
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False
    if request.method == "POST":
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read " f"{post.title}"
            message = (
                f"Read {post.title} at {post_url}\n\n"
                f"{cd['name']}'s comments: {cd['comments']}"
            )
            send_mail(subject, message, "your_account@gmail.com", [cd["to"]])
            sent = True
    else:
        form = EmailPostForm()
    return render(
        request,
        "blog/post/share.html",
        {"post": post, "form": form, "sent": sent},
    )


@require_POST
def post_comment(request, post_id):
    """
    Представление комментарии
    """
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
    comment.post = post
    comment.save()
    return render(
        request,
        "blog/post/comment.html",
        {"post": post, "form": form, "comment": comment},
    )


def post_search(request):
    """Представления поиска."""
    form = SearchForm()
    query = None
    results = []
    if "query" in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data["query"]
            search_vector = SearchVector("title", "body", config="russian")
            search_query = SearchQuery(query, config="russian")
            results = (
                Post.published.annotate(
                    search=search_vector,
                    rank=SearchRank(search_vector, search_query),
                )
                .filter(search=search_query)
                .order_by("-rank")
            )
    return render(
        request,
        "blog/post/search.html",
        {"form": form, "query": query, "results": results},
    )
