from django.contrib import admin
from .models import Genre, Filmwork, GenreFilmwork, Person, PersonFilmWork


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')


class GenreFilmworkInline(admin.TabularInline):
    model = GenreFilmwork


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('full_name',)


class PersonFilmWorkInline(admin.TabularInline):
    model = PersonFilmWork


@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    inlines = (
        GenreFilmworkInline, PersonFilmWorkInline
    )
    list_display = ('title', 'type', 'creation_date', 'rating')
    list_filter = ('type', 'creation_date',)
    search_fields = ('title', 'description', 'id')
    list_prefetch_related = ('genres', 'persons')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related(*self.list_prefetch_related)
