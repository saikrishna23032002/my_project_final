from django.urls import path
from . import views

urlpatterns = [

    path("booking/", views.bench_search, name="bench_search"),

    path("available/", views.available_benches, name="available_benches"),

   
    path("book/<int:bench_id>/", views.book_ticket, name="book_ticket"),
    path("benches/", views.display_bench_list, name="bench_list"),
    path("booked-benches/", views.booked_benches, name="booked_benches"),
    path('recently-booked/', views.recently_booked_benches, name='recently_booked_benches'),


]