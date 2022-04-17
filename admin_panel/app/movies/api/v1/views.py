from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.list import BaseListView
from django.views.generic.detail import BaseDetailView

from movies.models import Filmwork, PersonFilmWork


class MoviesApiMixin:
    model = Filmwork
    http_method_names = ['get']

    def get_array_agg_by_role(self, role: str) -> ArrayAgg:
        return ArrayAgg(
            'persons__full_name',
            filter=Q(personfilmwork__role=role),
            distinct=True
        )

    def get_queryset_annotate(self, queryset):
        return queryset.annotate(
            genres=ArrayAgg('genres__name', distinct=True),
            actors=self.get_array_agg_by_role('actor'),
            directors=self.get_array_agg_by_role('director'),
            writers=self.get_array_agg_by_role('writer')
        )

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class MoviesListApi(MoviesApiMixin, BaseListView):

    paginate_by = 50

    def get_queryset(self):
        qs = self.model.objects.prefetch_related('genres', 'persons')
        qs = qs.values(
            'id', 'title', 'description', 'creation_date', 'rating', 'type'
        )
        qs = self.get_queryset_annotate(qs)
        return qs

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = self.get_queryset()
        paginator, page, queryset, is_paginated = self.paginate_queryset(
            queryset,
            self.paginate_by
        )
        prev = page.previous_page_number() if page.has_previous() else None
        next = page.next_page_number() if page.has_next() else None

        return {
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'prev': prev,
            'next': next,
            'results': list(queryset)
        }


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):

    def get_queryset(self):
        qs = self.model.objects.filter(pk=self.kwargs['pk'])
        qs = qs.values(
            'id', 'title', 'description', 'creation_date', 'rating', 'type'
        )
        qs = self.get_queryset_annotate(qs)
        return qs

    def get_context_data(self, **kwargs):
        return self.get_object(queryset=self.get_queryset())
