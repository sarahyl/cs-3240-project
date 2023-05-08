from django.urls import path

from . import views

app_name = 'scheduleadvisor'
urlpatterns = [
    path('', views.indexView, name='index'),
    path('studentindex', views.studentView, name='student'),
    path('studentindex/clearnotifs', views.clear_notifs, name="clear_notifs"),
    path('advisorindex', views.advisorView, name='advisor'),
    path('advisorindex/approveschedule/<int:pk>', views.approve_schedule, name='approve_schedule'),
    path('advisorindex/rejectschedule/<int:pk>', views.reject_schedule, name='reject_schedule'),
    path('approved', views.approvedView, name='approved'),
    path('rejected', views.rejectedView, name='rejected'),
    path('search', views.searchView, name='search'),
    path('schedules/', views.scheduleView, name='schedules'),
    path('schedules/submitschedule/<int:pk>', views.submit_schedule, name='submit_schedule'),
    path('schedules/createschedule', views.create_schedule, name='create_schedule'),
    path('schedules/deleteschedule/<int:pk>', views.delete_schedule, name='delete_schedule'),
    path('schedules/editschedule/<int:pk>', views.edit_schedule, name='edit_schedule'),
    path('schedules/exportschedule/<int:pk>', views.export_schedule, name='export_schedule'),
    path('schedules/filterschedules', views.filter_schedules, name='filter_schedules'),
    path('schedules/cancelschedulesubmission/<int:pk>', views.cancel_schedule_submission, name="cancel_schedule_submission"),
    path('schedules/enroll/<int:pk>', views.enroll, name='enroll'),
    path('schedules/disenroll/<int:pk>', views.disenroll, name='disenroll'),
    path('schedules/buttontodetails/<int:pk>', views.button_to_details, name='button_to_details'),
    path('schedulebuilder/<int:pk>', views.scheduleBuilderView, name='schedulebuilder'),
    path('schedulebuilder/<int:pk>/addcoursetoschedule', views.add_course_to_schedule, name="add_course_to_schedule"),
    path('schedulebuilder/<int:pk>/deletecoursetoschedule', views.delete_course_from_schedule, name="delete_course_from_schedule"),
    path('schedulerbuilder/buttontoschedules', views.button_to_schedules, name='button_to_schedules'),
    path('cart', views.cartView, name='cart'),
    path('studentindex/addtocart', views.add_course_to_cart, name='add_course_to_cart'),
    path('cart/deletefromcart', views.delete_course_from_cart, name='delete_course_from_cart'),
    path('scheduledetails/<int:pk>', views.scheduleDetailsView, name="schedule_details_view"),
    path('advisees', views.adviseesListView, name="advisees_list_view"),
    path('advisees/addadvisee/<int:pk>', views.add_student_as_advisee, name="add_student_as_advisee"),
    path('notauthorized', views.notAuthorized, name="not_authorized")
]
