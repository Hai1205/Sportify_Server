import uuid
from django.db import models
from django.core.exceptions import ValidationError

class GenreMixin:
    """Mixin dùng để lưu danh sách thể loại và validate JSON field"""
    GENRE_CHOICE = [
        ('pop', 'Pop'),
        ('rock', 'Rock'),
        ('hip-hop', 'Hip-Hop'),
        ('country', 'Country'),
        ('r&b', 'R&B'),
        ('electronic', 'Electronic'),
        ('dance', 'Dance'),
        ('jazz', 'Jazz'),
        ('classical', 'Classical'),
        ('folk', 'Folk'),
        ('indie', 'Indie'),
        ('alternative', 'Alternative'),
        ('metal', 'Metal'),
        ('punk', 'Punk'),
        ('blues', 'Blues'),
        ('reggae', 'Reggae'),
        ('soul', 'Soul'),
        ('disco', 'Disco'),
        ('house', 'House'),
        ('techno', 'Techno'),
        ('trance', 'Trance'),
        ('ambient', 'Ambient'),
        ('latin', 'Latin'),
        ('k-pop', 'K-Pop'),
        ('j-pop', 'J-Pop'),
        ('afrobeat', 'Afrobeat'),
        ('gospel', 'Gospel'),
        ('soundtrack', 'Soundtrack'),
    ]
    
    GENRE_KEYS = [genre[0] for genre in GENRE_CHOICE]

    @staticmethod
    def validate_genres(value):
        # Nếu là chuỗi, chuyển thành list
        if isinstance(value, str):
            value = [value]
        # Nếu không phải list, báo lỗi
        elif not isinstance(value, list):
            raise ValidationError("Genre must be a list or a single string.")

        # Kiểm tra từng phần tử trong list
        for genre in value:
            if genre not in GenreMixin.GENRE_KEYS:
                raise ValidationError(f"'{genre}' is an invalid genre.")

        return value