from django.shortcuts import render
from django.db.models import Count, Prefetch
from blog.models import Comment, Post, Tag
from django.shortcuts import get_object_or_404


def serialize_post(post):
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': post.comments__count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()],
        'first_tag_title': post.tags.all()[0].title,
    }


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.posts__count,
    }


def index(request):
    prefetch_tags = Prefetch('tags', queryset=Tag.objects.annotate(Count('posts')))
    most_popular_posts = Post.objects.popular() \
                             .prefetch_related('author', prefetch_tags)[:5] \
        .fetch_with_comments_count()

    fresh_posts = Post.objects.annotate(Count('comments')) \
        .order_by('-published_at') \
        .prefetch_related('author', prefetch_tags)
    most_fresh_posts = reversed(fresh_posts[:5])


    most_popular_tags = Tag.objects.popular()[:5]

    context = {
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
        'page_posts': [serialize_post(post) for post in most_fresh_posts],
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    posts = Post.objects.popular().prefetch_related("author", "comments")
    most_popular_posts = posts[:5].fetch_with_comments_count()

    comments = Comment.objects.all().prefetch_related("author")

    post = get_object_or_404(posts, slug=slug)
    serialized_post = {
        "title": post.title,
        "text": post.text,
        "author": post.author.username,
        "comments": comments.filter(post=post),
        "likes_amount": post.likes__count,
        "image_url": post.image.url if post.image else None,
        "published_at": post.published_at,
        "slug": post.slug,
        "tags": post.tags.all(),
    }

    tags = Tag.objects.popular()
    most_popular_tags = tags[:5]

    context = {
        "post": serialized_post,
        "popular_tags": most_popular_tags,
        "most_popular_posts": most_popular_posts,
    }
    return render(request, "post-details.html", context)


def tag_filter(request, tag_title):

    tag = get_object_or_404(Tag, title=tag_title)
    popular_tags = Tag.objects.popular()
    most_popular_tags = popular_tags[:5]

    prefetch_tags = Prefetch('tags', queryset=Tag.objects.annotate(Count('posts')))
    most_popular_posts = Post.objects.popular() \
                             .prefetch_related('author', prefetch_tags)[:5] \
        .fetch_with_comments_count()

    related_posts = tag.posts.annotate(Count('comments')).prefetch_related('author', prefetch_tags)[:20]

    context = {
        'tag': tag.title,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'posts': [serialize_post(post) for post in related_posts],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'posts-list.html', context)



def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})
