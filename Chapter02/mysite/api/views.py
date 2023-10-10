import rest_framework.pagination
from django.shortcuts import render, get_object_or_404
from blog.models import Post, Comment, FileModel
from rest_framework.views import APIView
from rest_framework import request, status
from rest_framework.response import Response
from .serializers import PostSerializer, CommentSerializer, RequestToDownload
from .permissions import IsOwnerOrReadOnly
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
import csv

from django.http import FileResponse
import uuid
from django.core.files.base import File

User = get_user_model()


class PostList(APIView, PageNumberPagination):

    def get(self, request: request):
        query_params: dict = request.query_params
        if query_params.get('all', False) == 'true':
            posts = Post.objects.raw('select * from blog_post')
        else:
            posts = Post.published.all()

        self.page_size = 3
        results = self.paginate_queryset(posts, request, view=self)

        serializer = PostSerializer(results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetail(APIView):
    permission_classes = [IsOwnerOrReadOnly]

    def get_object(self, pk) -> Post | None:
        return get_object_or_404(Post, pk=pk)

    def get(self, request: request, pk: int):
        post = self.get_object(pk=pk)
        serializer = PostSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request: request, pk: int):
        post = self.get_object(pk=pk)
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request: request, pk: int) -> None:
        self.get_object(pk=pk).delete()


class CommentList(APIView):

    def get(self, request: request):
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CommentDetail(APIView):

    def post(self, request: request, pk: int):
        serializer = CommentSerializer(data=request.data)
        post = get_object_or_404(Post, pk=pk)
        if serializer.is_valid():
            serializer.save(post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, pk) -> Comment | None:
        return get_object_or_404(Comment, pk=pk)

    def get(self, request: request, pk: int):
        comment = self.get_object(pk)
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request: request, pk: int):
        comment = self.get_object(pk=pk)
        serializer = CommentSerializer(comment, data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request: request, pk: int):
        self.get_object(pk).delete()


class BackUP(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: request):
        posts = Post.objects.all()
        uid = uuid.uuid4()
        if posts:
            try:
                with open("/static/sample.csv", "w+") as tmp:
                    writer = csv.writer(tmp)
                    for p in posts:
                        writer.writerow([p.title, p.body])
                    FileModel(uuid=uid, file=File(tmp)).save()
            except Exception as e:
                return Response({"error": f"{e}"},
                                status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"url": f"http://127.0.0.1:8000/api/v1/files/download/{uid}"},
            status=status.HTTP_200_OK)


class Download(APIView):

    def get(self, request:request, uuid: uuid):
        file_object = get_object_or_404(FileModel, pk=uuid)
        file: FileModel = file_object.file
        if file is None:
            return Response(
                {'status_message': 'Resource does not contian image'})

        response = FileResponse(file)
        response['Content-Type'] = 'application/x-binary'
        response[
            'Content-Disposition'] = 'attachment; filename="{}.csv"'.format(
            uuid)
        return response
