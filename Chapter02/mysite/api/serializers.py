from rest_framework import serializers
from blog.models import Comment, Post


class CommentSerializer(serializers.ModelSerializer):
    post = serializers.StringRelatedField(source="post.title")

    class Meta:
        model = Comment
        fields = ['post', 'name', 'body', 'active']


class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(source="author.username")
    status = serializers.ChoiceField(choices=[('DF', 'Draft'),
                                              ('PB', 'Published')])
    comments = CommentSerializer(many=True, required=False)

    class Meta:
        model = Post
        fields = ['title', 'author', 'body', 'status', 'comments']


class RequestToDownload(serializers.Serializer):
    file_format = serializers.ChoiceField(choices=['csv', 'zip'])
