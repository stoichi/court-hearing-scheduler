from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models import Prefetch, QuerySet

from .forms import CourtHearingForm
from .models import CourtHearing

from accounts.models import User


def is_htmx(request: HttpRequest) -> bool:
    """
    Check whether the incoming request was made via HTMX.

    Parameters:
    - request: the Django request to inspect

    Return:
    - True if the HX-Request header is set to "true", False otherwise
    """
    return request.headers.get("HX-Request") == "true"


def htmx_refresh_response() -> HttpResponse:
    """
    Build an empty HTMX response that triggers a client-side refresh of the hearings list.

    Return:
    - 204 No Content response with the HX-Trigger header set to "refresh-hearings"
    """
    return HttpResponse(status=204, headers={"HX-Trigger": "refresh-hearings"})


class HearingQuerysetMixin:
    """
    Provide a shared optimized queryset for CourtHearing views.

    The queryset prefetches hearing participants and each participant's role
    to avoid N+1 queries when rendering or resolving hearing objects.

    Return:
    - Ordered queryset of CourtHearing instances with related participants prefetched
    """

    def get_queryset(self) -> QuerySet[CourtHearing]:
        """
        Build the hearing queryset with participants and their roles prefetched to avoid N+1 queries.

        Return:
        - Ordered queryset of CourtHearing instances with related participants prefetched
        """
        participants_qs = User.objects.select_related("role")
        return (
            CourtHearing.objects
            .prefetch_related(Prefetch("participants", queryset=participants_qs))
            .order_by("date", "start_time")
        )


class HearingListView(HearingQuerysetMixin, ListView):
    """
    Display the list of hearings.
    """
    model = CourtHearing
    context_object_name = "hearings"

    def get_template_names(self) -> list[str]:
        """
        Pick the template used to render the hearing list.

        Return:
        - ["hearing_list.html#rows"] when the request is an HTMX partial refresh
        - ["hearing_list.html"] for a full page render
        """
        if is_htmx(self.request):
            return ["hearing_list.html#rows"]
        return ["hearing_list.html"]


class HearingCreateView(CreateView):
    """
    Create a new hearing.
    """
    model = CourtHearing
    form_class = CourtHearingForm
    template_name = "hearing_form.html"
    success_url = reverse_lazy("hearings:hearing-list")

    def form_valid(self, form: CourtHearingForm) -> HttpResponse:
        """
        Persist the new hearing and respond appropriately for HTMX or standard requests.

        Parameters:
        - form: the validated hearing form to save

        Return:
        - HTMX refresh response when the request came from HTMX
        - Standard redirect response to the success URL otherwise
        """
        self.object = form.save()
        if is_htmx(self.request):
            return htmx_refresh_response()
        return super().form_valid(form)


class HearingUpdateView(HearingQuerysetMixin, UpdateView):
    """
    Update an existing hearing.
    """
    model = CourtHearing
    form_class = CourtHearingForm
    template_name = "hearing_form.html"
    success_url = reverse_lazy("hearings:hearing-list")

    def form_valid(self, form: CourtHearingForm) -> HttpResponse:
        """
        Persist the updated hearing and respond appropriately for HTMX or standard requests.

        Parameters:
        - form: the validated hearing form to save

        Return:
        - HTMX refresh response when the request came from HTMX
        - Standard redirect response to the success URL otherwise
        """
        self.object = form.save()
        if is_htmx(self.request):
            return htmx_refresh_response()
        return super().form_valid(form)


class HearingDeleteView(HearingQuerysetMixin, DeleteView):
    """
    Delete an existing hearing.
    """
    model = CourtHearing
    template_name = "hearing_confirm_delete.html"
    success_url = reverse_lazy("hearings:hearing-list")

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Delete the hearing and respond appropriately for HTMX or standard requests.

        Parameters:
        - request: the incoming delete request

        Return:
        - HTMX refresh response when the request came from HTMX
        - Standard redirect response to the success URL otherwise
        """
        if is_htmx(request):
            self.get_object().delete()
            return htmx_refresh_response()
        return super().post(request, *args, **kwargs)