from django.db import models
from django.db.models import Q, Case, When, IntegerField
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.conf import settings

class SearchMixin:
    """Mixin to add search functionality to ViewSets"""
    
    def get_search_queryset(self, queryset, search_term):
        """Override in subclasses to define search logic"""
        return queryset
    
    def apply_search(self, queryset):
        search = self.request.query_params.get('search')
        if search:
            return self.get_search_queryset(queryset, search)
        return queryset

class JobSearchMixin(SearchMixin):
    def get_search_queryset(self, queryset, search_term):
        # Use PostgreSQL full-text search if available
        if 'postgresql' in settings.DATABASES['default']['ENGINE']:
            return queryset.annotate(
                search=SearchVector('title', 'description', 'location', 'employer__company_name')
            ).filter(search=SearchQuery(search_term)).annotate(
                rank=SearchRank(SearchVector('title', 'description'), SearchQuery(search_term))
            ).order_by('-rank', '-is_featured', '-created_at')
        
        # Enhanced SQLite search with ranking
        search_terms = search_term.lower().split()
        q_objects = Q()
        
        for term in search_terms:
            q_objects |= (
                Q(title__icontains=term) |
                Q(description__icontains=term) |
                Q(location__icontains=term) |
                Q(employer__company_name__icontains=term) |
                Q(skills__icontains=term)
            )
        
        return queryset.filter(q_objects).annotate(
            search_rank=Case(
                When(title__icontains=search_term, then=3),
                When(employer__company_name__icontains=search_term, then=2),
                When(location__icontains=search_term, then=1),
                default=0,
                output_field=IntegerField()
            )
        ).order_by('-search_rank', '-is_featured', '-created_at')

class UserSearchMixin(SearchMixin):
    def get_search_queryset(self, queryset, search_term):
        return queryset.filter(
            Q(email__icontains=search_term) |
            Q(first_name__icontains=search_term) |
            Q(last_name__icontains=search_term)
        )

class CandidateSearchMixin(SearchMixin):
    def get_search_queryset(self, queryset, search_term):
        return queryset.filter(
            Q(user__email__icontains=search_term) |
            Q(user__first_name__icontains=search_term) |
            Q(user__last_name__icontains=search_term) |
            Q(education__icontains=search_term) |
            Q(experience__icontains=search_term)
        )

class EmployerSearchMixin(SearchMixin):
    def get_search_queryset(self, queryset, search_term):
        return queryset.filter(
            Q(company_name__icontains=search_term) |
            Q(domain__icontains=search_term) |
            Q(company_description__icontains=search_term) |
            Q(user__email__icontains=search_term)
        )