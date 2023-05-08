from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib import messages
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.models import User

from django.views import generic

from .models import Student, Advisor, SearchCourse, Schedule, ScheduleCourse, CartCourse, Cart, Notification

from ics import Calendar, Event
from dateutil.rrule import rrule, WEEKLY

import json, requests


"""

citations

removing default login messages https://stackoverflow.com/questions/25744425/how-to-clean-up-django-login-message-from-framework

bootstrap getbootstrap.com/docs/5.0

cart / javascript https://www.youtube.com/watch?v=woORrr3QNh8&list=PL-51WBLyFTg0omnamUjL1TCVov7yDTRng&index=3

sorting by datetime https://stackoverflow.com/questions/5055812/sort-python-list-of-objects-by-date


"""

def studentView(request):
    if not request.user.groups.filter(name='Student').exists():
        return HttpResponseRedirect(reverse('scheduleadvisor:not_authorized'))
    
    student = Student.objects.get(user = request.user)
    notifications = Notification.objects.filter(student=student).order_by('-pub_date')

    if student.advisor == None:
        no_advisor = True
    else:
        no_advisor = False
        
    context = {
        'student': student,
        'notifications': notifications,
        'no_advisor': no_advisor
    }
    return render(request, 'scheduleadvisor/studentindex.html', context)
    

def approvedView(request):
    if not request.user.groups.filter(name='Advisor').exists():
        return HttpResponseRedirect(reverse('scheduleadvisor:not_authorized'))
    advisor = request.user.advisor
    students = advisor.student_set.all()
    approved_schedules = []
    for student in students:
        try:
            #all of the approved schedules of this student
            student_approved_schedules = Schedule.objects.filter(student=student, status="Approved")
            #rejected_schedule is looping through the rejected Schedule objects of the student
            #reformatting it into schedule which is the list of lists 
            #then append schedule to rejected_schedules which is list of all rejected schedules to pass to template
            if student_approved_schedules:
                for approved_schedule in student_approved_schedules:
                    # format of rejected_schedules is list of lists
                    # each list is made up of schedulecourses that belong to that student's rejected schedule
                    schedule = []
                    for course in approved_schedule.schedulecourse_set.all():
                        schedule.append(course)
                    approved_schedules.append(schedule)  
        except Schedule.DoesNotExist:
            continue

    context = {
        'students': students,
        'approvedschedules': approved_schedules
    }
    return render(request, 'scheduleadvisor/approved.html', context)

def rejectedView(request):
    if not request.user.groups.filter(name='Advisor').exists():
        return HttpResponseRedirect(reverse('scheduleadvisor:not_authorized'))
    advisor = request.user.advisor
    students = advisor.student_set.all()
    rejected_schedules = []
    for student in students:
        #all of the rejected schedules of this student
        student_rejected_schedules = Schedule.objects.filter(student=student, status="Rejected")
        #if student_rejected_schedules queryset is not empty
        if student_rejected_schedules:
            #rejected_schedule is looping through the rejected Schedule objects of the student
            #reformatting it into schedule which is the list of lists 
            #then append schedule to rejected_schedules which is list of all rejected schedules to pass to template
            for rejected_schedule in student_rejected_schedules:
                # format of rejected_schedules is list of lists
                # each list is made up of schedulecourses that belong to that student's rejected schedule
                schedule = []
                for course in rejected_schedule.schedulecourse_set.all():
                    schedule.append(course)
                rejected_schedules.append(schedule)

    context = {
        'students': students,
        'rejectedschedules': rejected_schedules
    }
    return render(request, 'scheduleadvisor/rejected.html', context)

def approve_schedule(request, pk):
    if not request.user.groups.filter(name='Advisor').exists():
        return HttpResponseRedirect(reverse('scheduleadvisor:not_authorized'))
    try: 
        schedule = Schedule.objects.get(id=pk)
    except Schedule.DoesNotExist:
        return HttpResponseRedirect(reverse('scheduleadvisor:advisor'))

    if schedule.student.advisor != request.user.advisor:
        return HttpResponseRedirect(reverse('scheduleadvisor:not_authorized'))

    schedule.status = "Approved"
    schedule.save()
    notif = Notification(
        student = schedule.student,
        schedule = schedule,
        notif = "Schedule " + schedule.title + " has been approved.",
        pub_date = timezone.now()
    )
    notif.save()
    return HttpResponseRedirect(reverse('scheduleadvisor:advisor'))

def reject_schedule(request, pk):
    if not request.user.groups.filter(name='Advisor').exists():
        return HttpResponseRedirect(reverse('scheduleadvisor:not_authorized'))
    
    try: 
        schedule = Schedule.objects.get(id=pk)
    except Schedule.DoesNotExist:
        return HttpResponseRedirect(reverse('scheduleadvisor:advisor'))

    if schedule.student.advisor != request.user.advisor:
        return HttpResponseRedirect(reverse('scheduleadvisor:not_authorized'))
    
    schedule.status = "Rejected"
    #schedule.comment =
    schedule.save()
    notif = Notification(
        student = schedule.student,
        schedule = schedule,
        notif = "Schedule " + schedule.title + " has been rejected.",
        pub_date = timezone.now()
    )
    notif.save()
    return HttpResponseRedirect(reverse('scheduleadvisor:advisor'))

def advisorView(request):
    if not request.user.groups.filter(name='Advisor').exists():
        return HttpResponseRedirect(reverse('scheduleadvisor:not_authorized'))
    advisor = request.user.advisor
    students = advisor.student_set.all()
    submitted_schedules = []
    for student in students:
        try:
            #if the student has a schedule that's pending approval, then add that to the submitted schedules list
            submitted_schedule = Schedule.objects.get(student=student, status="Pending Approval")
            # format of submitted_schedules is list of lists
            # each list is made up of schedulecourses that belong to that student's submitted schedule
            schedule = []
            for course in submitted_schedule.schedulecourse_set.all():
                schedule.append(course)
            submitted_schedules.append(schedule)           
        except Schedule.DoesNotExist:
            continue
    context = {
        'students': students,
        'submitted_schedules': submitted_schedules
    }
    return render(request, 'scheduleadvisor/advisorindex.html', context)

def indexView(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Student').exists():
            try:
                student = Student.objects.get(user=request.user)
            except Student.DoesNotExist:
                student = Student.objects.create(user=request.user, stud_name=request.user.get_full_name(), username=request.user.get_username(), email=request.user.email, advisor=None)
                cart = Cart.objects.create(student=student)
            return HttpResponseRedirect(reverse('scheduleadvisor:student'))
        if request.user.groups.filter(name='Advisor').exists():
            try:
                advisor = Advisor.objects.get(user=request.user)
            except Advisor.DoesNotExist:
                advisor = Advisor.objects.create(user=request.user, adv_name=request.user.get_full_name(), username=request.user.get_username(), email=request.user.email)
            return HttpResponseRedirect(reverse('scheduleadvisor:advisor'))
        else:
            return render(request, 'scheduleadvisor/assigntogroup.html')
    else:
        return render(request, '../templates/index.html')

def searchView(request):
    if not request.user.groups.filter(name='Student').exists():
        return HttpResponseRedirect(reverse('scheduleadvisor:not_authorized'))
    #if search button was clicked
    if request.method == "POST":
        #inputs from the searching filtering form
        #term = request.POST['term_text']
        subject = request.POST['subject_text']
        catalog_number = request.POST['catalog_number_text']
        keyword = request.POST['keyword_text']
        enrollment_status = request.POST.getlist('enrollment_status')

        if (subject=="") and (catalog_number=="") and (keyword == ""):
            messages.error(request, "Fill out at least one of the search criteria.")
            return HttpResponseRedirect(reverse('scheduleadvisor:search'))

        #default api link
        api_link = "https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassSearch?institution=UVA01"
        #add term to api link - default to fall 2023 
        api_link += "&term=1238" 
        #add subject to api link
        if subject != "":
            api_link += "&subject=" + subject.upper()
        #add catalog number to api link
        if catalog_number != "":
            api_link += "&catalog_nbr=" + catalog_number
        #add keyword to link
        if keyword != "":
            api_link += "&keyword=" + keyword
        #add enrollment status to link
        if len(enrollment_status) == 1:
            api_link += "&enrl_stat=O"
        #manually add page number
        #api_link += "&page=1"
        response = requests.get(api_link)
        data = json.loads(response.text) # data is a list of dictionaries

        #if any course models exist delete them to clear the page
        if SearchCourse.objects.all():
            SearchCourse.objects.all().delete()

        if data:
            #create the courses for the page we want to load. each data_item is a course
            for data_item in data:

                #formatting instructors e.g. Instructor 1, Instructor 2
                instructors_list = []
                for instructor in data_item['instructors']:
                    instructors_list.append(instructor['name'])
                instructors = ", ".join(instructors_list)

                #meetings
                meetings = data_item['meetings'][0] #dictionary
                days = meetings['days']
                start_time = meetings['start_time'][:5]
                if start_time!= "":
                    start_time = datetime.strptime(start_time, "%H.%M")
                    start_time = start_time.strftime("%I:%M %p")
                end_time = meetings['end_time'][:5]
                if end_time!="":
                    end_time = datetime.strptime(end_time, "%H.%M")
                    end_time = end_time.strftime("%I:%M %p")
                classroom = meetings['facility_descr']


                course = SearchCourse(

                    subject = data_item['subject'],
                    subject_description = data_item['subject_descr'],
                    catalog_number = data_item['catalog_nbr'],
                    title = data_item['descr'],
                    topic = data_item['topic'],
                    units = data_item['units'],
                    class_number = data_item['class_nbr'],
                    instructors = instructors,
                    days = days,
                    start_time = start_time,
                    end_time = end_time,
                    classroom = classroom,
                    enrollment_status = data_item['enrl_stat_descr'],
                    class_capacity = data_item['class_capacity'],
                    enrollment_total = data_item['enrollment_total'],
                    section_type = data_item['section_type'],
                    acad_career_descr = data_item['acad_career_descr']
                    )
                course.save()
            courses=SearchCourse.objects.all()

            context = {
                'data':data,
                'courses':courses
            }
        #if no courses are returned then return with error message
        else:
            error_message = "No courses were found."
            context = {
                'data':data,
                'error_message': error_message
            }

    #no search, empty page
    else:
        data = ""
        courses = ""
        context = {
            'data': data,
            'courses': courses
        }

    #TODO:change this to httpresponseredirect if dealing with post data
    return render(request, 'scheduleadvisor/search.html', context)

def cartView(request):
    if not request.user.groups.filter(name='Student').exists():
        return HttpResponseRedirect(reverse('scheduleadvisor:not_authorized'))
    student = request.user.student
    #gets the cart linked to the student user
    cart = Cart.objects.get(student=student)
    #gets all of the CartCourses that are linked to the student's cart
    cart_courses = cart.cartcourse_set.all()
    context = {
        'courses': cart_courses
    }
    return render(request, 'scheduleadvisor/cart.html', context)

def add_course_to_cart(request):
    if not request.user.groups.filter(name='Student').exists():
        return HttpResponseRedirect(reverse('scheduleadvisor:not_authorized'))
    #getting the data from cart.js
    data = json.loads(request.body)
    class_number = data['class_number']
    action = data['action']
    student = request.user.student
    cart = Cart.objects.get(student=student)

    #check if this course is already in cart
    try: 
        cart_course = CartCourse.objects.get(cart=cart, class_number=class_number)
    except CartCourse.DoesNotExist:
        #create the CartCourse object if that course class number isn't in this user's cart
        course = SearchCourse.objects.all().get(class_number=class_number)
        cart_course = CartCourse(
            cart=cart,
            subject = course.subject,
            subject_description = course.subject_description,
            catalog_number = course.catalog_number,
            title = course.title,
            topic = course.topic,
            units = course.units,
            class_number = course.class_number,
            instructors = course.instructors,
            days = course.days,
            start_time = course.start_time,
            end_time = course.end_time,
            classroom = course.classroom,
            enrollment_status = course.enrollment_status,
            class_capacity = course.class_capacity,
            enrollment_total = course.enrollment_total,
            section_type = course.section_type,
            acad_career_descr = course.acad_career_descr
            )
        cart_course.save()


    return JsonResponse("Add to cart", safe=False)

def delete_course_from_cart(request):
    if not request.user.groups.filter(name='Student').exists():
        return HttpResponseRedirect(reverse('scheduleadvisor:not_authorized'))
    #getting the data from cart.js
    data = json.loads(request.body)
    class_number = data['class_number']
    action = data['action']
    student = request.user.student
    cart = Cart.objects.get(student=student)
    cart_course = CartCourse.objects.all().get(cart=cart, class_number=class_number)
    cart_course.delete()
    return JsonResponse("Delete from cart", safe=False)


def create_schedule(request):
    if not request.user.groups.filter(name='Student').exists():
                return HttpResponseRedirect(reverse('scheduleadvisor:not_authorized'))
    title = request.POST.get('title')
    #if the user clicked the create schedule button without entering a title don't create schedule and reload page
    if title == "":
        messages.error(request, "A schedule title is required.")
        return HttpResponseRedirect(reverse('scheduleadvisor:schedules'))
    else: 
        try:
            #checks if there is already a schedule with this title
            schedule = Schedule.objects.get(student=request.user.student, title=title)
            messages.error(request, "A schedule with this title already exists.")
            return HttpResponseRedirect(reverse('scheduleadvisor:schedules'))

        except Schedule.DoesNotExist:
            #creates the new schedule
            schedule = Schedule()
            schedule.title = title
            schedule.status = "Work In Progress"
            schedule.student = request.user.student
            schedule.credits = "0"
            schedule.save()
            return HttpResponseRedirect(reverse('scheduleadvisor:schedulebuilder', args=(schedule.id,)))

def delete_schedule(request, pk):
    if not request.user.groups.filter(name='Student').exists():
                return HttpResponseRedirect(reverse('scheduleadvisor:not_authorized'))
    #pk is the id of the schedule to delete
    student = request.user.student
    try:
        schedule = Schedule.objects.all().get(student=student, id=pk)
    except Schedule.DoesNotExist:
        return HttpResponseRedirect(reverse('scheduleadvisor:student'))

    if schedule.student != request.user.student:
                return HttpResponseRedirect(reverse('scheduleadvisor:not_authorized'))

    schedule.delete()
    return HttpResponseRedirect(reverse('scheduleadvisor:schedules'))

def edit_schedule(request, pk):
    if not request.user.groups.filter(name='Student').exists():
        return HttpResponseRedirect(reverse('scheduleadvisor:not_authorized'))
    #pk is the schedule you want to edit
    student = request.user.student
    try:
        schedule = Schedule.objects.all().get(student=student, id=pk)
    except Schedule.DoesNotExist:
        return HttpResponseRedirect(reverse('scheduleadvisor:student'))

    if schedule.student != request.user.student:
        return HttpResponseRedirect(reverse('scheduleadvisor:not_authorized'))
    
    if schedule.status != "Work In Progress":
        return HttpResponseRedirect(reverse('scheduleadvisor:not_authorized'))

    return HttpResponseRedirect(reverse('scheduleadvisor:schedulebuilder', args=(pk,)))

def export_schedule(request, pk):
    if not request.user.groups.filter(name='Student').exists():
         return HttpResponseRedirect(reverse('scheduleadvisor:not_authorized'))
    # pk is the schedule you want to export
    student = request.user.student
    try:
        schedule = Schedule.objects.all().get(student=student, id=pk)
    except Schedule.DoesNotExist:
        return HttpResponseRedirect(reverse('scheduleadvisor:student'))
    
    if schedule.student != request.user.student:
        return HttpResponseRedirect(reverse('scheduleadvisor:not_authorized'))

    courses = schedule.schedulecourse_set.all()
    cal = Calendar()

    for c in courses:
        if "Mo" in c.days:
            event = Event()
            event.name = c.title
            event.begin = datetime(2023, 8, 21, datetime.strptime(c.start_time, "%H:%M %p").hour, datetime.strptime(c.start_time, "%H:%M %p").minute)
            event.end = datetime(2023, 8, 21, datetime.strptime(c.end_time, "%H:%M %p").hour, datetime.strptime(c.end_time, "%H:%M %p").minute)
            event.rrule = rrule(freq=WEEKLY, count=14)
            cal.events.add(event)
        if "Tu" in c.days:
            event = Event()
            event.name = c.title
            event.begin = datetime(2023, 8, 22, datetime.strptime(c.start_time, "%H:%M %p").hour, datetime.strptime(c.start_time, "%H:%M %p").minute)
            event.end = datetime(2023, 8, 22, datetime.strptime(c.end_time, "%H:%M %p").hour, datetime.strptime(c.end_time, "%H:%M %p").minute)
            event.rrule = rrule(freq=WEEKLY, count=14)
            cal.events.add(event)
        if "We" in c.days:
            event = Event()
            event.name = c.title
            event.begin = datetime(2023, 8, 23, datetime.strptime(c.start_time, "%H:%M %p").hour, datetime.strptime(c.start_time, "%H:%M %p").minute)
            event.end = datetime(2023, 8, 23, datetime.strptime(c.end_time, "%H:%M %p").hour, datetime.strptime(c.end_time, "%H:%M %p").minute)
            event.rrule = rrule(freq=WEEKLY, count=14)
            cal.events.add(event)
        if "Th" in c.days:
            event = Event()
            event.name = c.title
            event.begin = datetime(2023, 8, 24, datetime.strptime(c.start_time, "%H:%M %p").hour, datetime.strptime(c.start_time, "%H:%M %p").minute)
            event.end = datetime(2023, 8, 24, datetime.strptime(c.end_time, "%H:%M %p").hour, datetime.strptime(c.end_time, "%H:%M %p").minute)
            event.rrule = rrule(freq=WEEKLY, count=14)
            cal.events.add(event)
        if "Fr" in c.days:
            event = Event()
            event.name = c.title
            event.begin = datetime(2023, 8, 25, datetime.strptime(c.start_time, "%H:%M %p").hour, datetime.strptime(c.start_time, "%H:%M %p").minute)
            event.end = datetime(2023, 8, 25, datetime.strptime(c.end_time, "%H:%M %p").hour, datetime.strptime(c.end_time, "%H:%M %p").minute)
            event.rrule = rrule(freq=WEEKLY, count=14)
            cal.events.add(event)
    filename = f"{schedule.title}.ics"

    with open(filename, 'w') as f:
        f.write(str(cal))

    response = HttpResponse(str(cal), content_type='text/calendar')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response

def scheduleView(request):
    if not request.user.groups.filter(name='Student').exists():
                return HttpResponseRedirect(reverse('scheduleadvisor:not_authorized'))
    student = request.user.student

    monday_courses = []
    tuesday_courses = []
    wednesday_courses = []
    thursday_courses = []
    friday_courses = []

    #gets all of the ScheduleCourses linked to the schedules
    #schedule_courses = ScheduleCourse.objects.filter(schedule__in=schedules)
    #getting the schedule the student is currently enrolled in if it exists
    try:
        enrolled_schedule = Schedule.objects.get(student=student, status="Enrolled")
        schedule_courses = enrolled_schedule.schedulecourse_set.all()
        #organizing the schedule courses into days of the week so that they can be displayed
        for s in schedule_courses:
            days = s.days
            if "Mo" in days:
                monday_courses.append(s)
            if "Tu" in days:
                tuesday_courses.append(s)
            if "We" in days:
                wednesday_courses.append(s)
            if "Th" in days:
                thursday_courses.append(s)
            if "Fr" in days:
                friday_courses.append(s)

            #putting the courses into chronological order
            monday_courses.sort(key=lambda course: datetime.strptime(course.start_time, "%I:%M %p"))
            tuesday_courses.sort(key=lambda course: datetime.strptime(course.start_time, "%I:%M %p"))
            wednesday_courses.sort(key=lambda course: datetime.strptime(course.start_time, "%I:%M %p"))
            thursday_courses.sort(key=lambda course: datetime.strptime(course.start_time, "%I:%M %p"))
            friday_courses.sort(key=lambda course: datetime.strptime(course.start_time, "%I:%M %p"))
    except Schedule.DoesNotExist:
        enrolled_schedule = None    
    
    #filtering the schedules 
    if student.schedule_filter == "All":
        schedules = Schedule.objects.all().filter(student=student)
    else:
        schedules = Schedule.objects.all().filter(student=student, status=student.schedule_filter)

    context = {
        'schedules':schedules,
        'filter': student.schedule_filter,
        'enrolledschedule': enrolled_schedule,
        'mondaycourses': monday_courses,
        'tuesdaycourses': tuesday_courses,
        'wednesdaycourses': wednesday_courses,
        'thursdaycourses': thursday_courses,
        'fridaycourses': friday_courses
        #'schedulecourses': schedule_courses
        }

    return render(request, 'scheduleadvisor/schedules.html', context)

def scheduleBuilderView(request, pk):
    if not request.user.groups.filter(name='Student').exists():
        return HttpResponseRedirect(reverse('scheduleadvisor:not_authorized'))
    
    student = request.user.student
    cart = Cart.objects.get(student=student)
    #gets all of the CartCourses that are in the student's cart
    cart_courses = cart.cartcourse_set.all()
    #gets the schedule that you want to build
    try: 
        schedule = Schedule.objects.all().get(student=student, id=pk)
    except Schedule.DoesNotExist:
        return HttpResponseRedirect(reverse('scheduleadvisor:student'))
    
    if schedule.status != "Work In Progress":
        return HttpResponseRedirect(reverse('scheduleadvisor:not_authorized'))

    #gets the schedules that are currently part of that schedule
    schedule_courses = schedule.schedulecourse_set.all()
    #get schedule id
    schedule_id = schedule.id

    if schedule.student != request.user.student:
        return HttpResponseRedirect(reverse('scheduleadvisor:not_authorized'))

    monday_courses = []
    tuesday_courses = []
    wednesday_courses = []
    thursday_courses = []
    friday_courses = []

    #organizing the schedule courses into days of the week so that they can be displayed
    for s in schedule_courses:
        days = s.days
        if "Mo" in days:
            monday_courses.append(s)
        if "Tu" in days:
            tuesday_courses.append(s)
        if "We" in days:
            wednesday_courses.append(s)
        if "Th" in days:
            thursday_courses.append(s)
        if "Fr" in days:
            friday_courses.append(s)

        #putting the courses into chronological order
        monday_courses.sort(key=lambda course: datetime.strptime(course.start_time, "%I:%M %p"))
        tuesday_courses.sort(key=lambda course: datetime.strptime(course.start_time, "%I:%M %p"))
        wednesday_courses.sort(key=lambda course: datetime.strptime(course.start_time, "%I:%M %p"))
        thursday_courses.sort(key=lambda course: datetime.strptime(course.start_time, "%I:%M %p"))
        friday_courses.sort(key=lambda course: datetime.strptime(course.start_time, "%I:%M %p"))

    context = {
        'cartcourses': cart_courses,
        'schedule': schedule,
        'schedule_id': schedule_id,
        'mondaycourses': monday_courses,
        'tuesdaycourses': tuesday_courses,
        'wednesdaycourses': wednesday_courses,
        'thursdaycourses': thursday_courses,
        'fridaycourses': friday_courses

    }
    return render(request, 'scheduleadvisor/schedulebuilder.html', context)

def add_course_to_schedule(request, pk):
    if not request.user.groups.filter(name='Student').exists():
        return HttpResponseRedirect(reverse('scheduleadvisor:not_authorized'))
    #schedule you're adding to 
    try: 
        schedule = Schedule.objects.get(student=request.user.student, id=pk)
    except Schedule.DoesNotExist:
        return HttpResponseRedirect(reverse('scheduleadvisor:student'))

    if schedule.student != request.user.student:
        return HttpResponseRedirect(reverse('scheduleadvisor:not_authorized'))
    
    #class number of the course to delete
    class_number=request.POST['schedulecourse_classnumber']

    #check if this course has already been added to the schedule. if it has, then send error message
    try:
        course = ScheduleCourse.objects.get(schedule=schedule, class_number=class_number)
        messages.error(request, "This course has already been added to the schedule.")
        return HttpResponseRedirect(reverse('scheduleadvisor:schedulebuilder', args=(schedule.id,)))
    except ScheduleCourse.DoesNotExist:
        #pk is the schedule id that you're adding the course to
        cart = Cart.objects.all().get(student=request.user.student)
        #the course to add to schedule
        course = CartCourse.objects.all().get(cart=cart, class_number=class_number)

        # #check if the time is listed for the class because sometimes it's not listed yet
        # #if time isn't listed for a class, then don't allow enrollment
        # #TODO: later, allow enrollement, just add separate section for these classes like how SIS does
        try: 
            course_start_time = datetime.strptime(course.start_time, "%I:%M %p")
            course_end_time = datetime.strptime(course.end_time, "%I:%M %p")
        except ValueError:
            messages.error(request, "No listed time: can't enroll in this course")
            return HttpResponseRedirect(reverse('scheduleadvisor:schedulebuilder', args=(schedule.id,)))


        #check if the class is open
        if course.enrollment_status == "Closed":
            messages.error(request,"Error: This class is closed.")
            return HttpResponseRedirect(reverse('scheduleadvisor:schedulebuilder', args=(schedule.id,)))

        #check for time conflicts
        course_start_time = datetime.strptime(course.start_time, "%I:%M %p")
        course_end_time = datetime.strptime(course.end_time, "%I:%M %p")
        #the days that the added courses is for
        course_days = [course.days[i:i+2] for i in range(0, len(course.days), 2)]
        #the current courses already added to schedule
        current_courses = ScheduleCourse.objects.filter(schedule=schedule)
        for current_course in current_courses:
            #list of the days that the current course is for
            current_course_days = [current_course.days[i:i+2] for i in range(0, len(current_course.days), 2)]
            #if the added course and the current schedule course are on the same days (checking if there is overlap between the days lists)
            #this means there is potentially a time conflict
            if bool(set(course_days) & set(current_course_days)):
                current_course_start_time = datetime.strptime(current_course.start_time, "%I:%M %p")
                current_course_end_time = datetime.strptime(current_course.end_time, "%I:%M %p")

                if ((course_start_time < current_course_end_time) and not(course_end_time < current_course_start_time)) or ((course_end_time > current_course_start_time) and not(course_start_time > current_course_end_time)): 
                    messages.error(request, "Error: time conflict between courses.")
                    return HttpResponseRedirect(reverse('scheduleadvisor:schedulebuilder', args=(schedule.id,)))
    
        #creating the schedulecourse for the schedule
        schedule_course = ScheduleCourse(
            schedule=schedule,
            subject = course.subject, 
            subject_description = course.subject_description, 
            catalog_number = course.catalog_number,
            title = course.title,
            topic = course.topic,
            units = course.units,
            class_number = course.class_number,
            instructors = course.instructors,
            days = course.days,
            start_time = course.start_time,
            end_time = course.end_time,
            classroom = course.classroom,
            enrollment_status = course.enrollment_status,
            class_capacity = course.class_capacity,
            enrollment_total = course.enrollment_total,
            section_type = course.section_type,
            acad_career_descr = course.acad_career_descr
            )

        schedule_course.save()

        #TODO: credits 1 - 3
        #adding credits for schedule
        credits = int(schedule.credits) + int(course.units)
        schedule.credits = credits
        schedule.save()

        return HttpResponseRedirect(reverse('scheduleadvisor:schedulebuilder', args=(schedule.id,)))

def delete_course_from_schedule(request, pk):
    if not request.user.groups.filter(name='Student').exists():
                return HttpResponseRedirect(reverse('scheduleadvisor:not_authorized'))
    #schedule you're deleting from 
    try: 
        schedule = Schedule.objects.get(student=request.user.student, id=pk)
    except Schedule.DoesNotExist:
        return HttpResponseRedirect(reverse('scheduleadvisor:student'))

    if schedule.student != request.user.student:
                return HttpResponseRedirect(reverse('scheduleadvisor:not_authorized'))

    course = ScheduleCourse.objects.all().get(schedule=schedule, class_number=request.POST['delete_schedulecourse'])
    course.delete()
    return HttpResponseRedirect(reverse('scheduleadvisor:schedulebuilder', args=(pk,)))

def submit_schedule(request, pk):
    if not request.user.groups.filter(name='Student').exists():
                return HttpResponseRedirect(reverse('scheduleadvisor:not_authorized'))
    if request.user.student.advisor is None:
        messages.error(request, "You currently do not have an advisor.")
        return HttpResponseRedirect(reverse('scheduleadvisor:schedules'))
    try:
        #check if this student has already a schedule that is pending approval
        schedule = Schedule.objects.get(student=request.user.student, status="Pending Approval")
        #if yes, give error message
        if pk==schedule.id:
            messages.error(request, "This schedule is currently already submitted for approval.")
        else:
            #check if the schedule belongs to the user/student
            try:
                s = Schedule.objects.get(student=request.user.student, id=pk)
                messages.error(request, "Only one schedule can be submitted for approval at a time.")
            except Schedule.DoesNotExist:
                        return HttpResponseRedirect(reverse('scheduleadvisor:not_authorized'))
        return HttpResponseRedirect(reverse('scheduleadvisor:schedules'))
    except Schedule.DoesNotExist:
        #pk is schedule being submitted to advisor
        schedule = Schedule.objects.get(student=request.user.student, id=pk)

        #check if schedule is empty
        courses = schedule.schedulecourse_set.all()
        if not courses:
             messages.error(request, "Error: schedule is empty")
             return HttpResponseRedirect(reverse('scheduleadvisor:schedules'))

        schedule.status = "Pending Approval"
        schedule.save()
        messages.success(request, "Your schedule has been submitted for approval.")
        return HttpResponseRedirect(reverse('scheduleadvisor:schedules'))

def clear_notifs(request):
    if not request.user.groups.filter(name='Student').exists():
                return HttpResponseRedirect(reverse('scheduleadvisor:not_authorized'))
    student = request.user.student
    notifs = Notification.objects.filter(student=student)
    notifs.delete()
    return HttpResponseRedirect(reverse('scheduleadvisor:student'))

def button_to_schedules(request):
    if not request.user.groups.filter(name='Student').exists():
                return HttpResponseRedirect(reverse('scheduleadvisor:not_authorized'))
    return HttpResponseRedirect(reverse('scheduleadvisor:schedules'))

def filter_schedules(request):
    if not request.user.groups.filter(name='Student').exists():
                return HttpResponseRedirect(reverse('scheduleadvisor:not_authorized'))
    filter = request.POST['filter']
    student = request.user.student
    student.schedule_filter = filter
    student.save()
    return HttpResponseRedirect(reverse('scheduleadvisor:schedules'))

def cancel_schedule_submission(request, pk):
    if not request.user.groups.filter(name='Student').exists():
                return HttpResponseRedirect(reverse('scheduleadvisor:not_authorized'))
    try: 
        schedule = Schedule.objects.get(student=request.user.student, id=pk)
    except Schedule.DoesNotExist:
        return HttpResponseRedirect(reverse('scheduleadvisor:student'))
    schedule.status = "Work In Progress"
    schedule.save()
    messages.success(request, "Your schedule submission has been canceled.")
    return HttpResponseRedirect(reverse('scheduleadvisor:schedules'))

def enroll(request, pk):
    if not request.user.groups.filter(name='Student').exists():
                return HttpResponseRedirect(reverse('scheduleadvisor:not_authorized'))
    try:
        enrolled_schedule = Schedule.objects.get(student=request.user.student, status="Enrolled")
        messages.error(request, "Disenroll from your currently enrolled schedule before enrolling.")
    except Schedule.DoesNotExist:
        schedule = Schedule.objects.get(student=request.user.student, id=pk)
        #check for waitlisted courses
        schedule_courses = schedule.schedulecourse_set.all()
        for course in schedule_courses:
            if course.enrollment_status != "Open":
                messages.error(request, "All classes in schedule must be open to enroll.")
                return HttpResponseRedirect(reverse('scheduleadvisor:schedules'))
        schedule.status = "Enrolled"
        schedule.save()
        messages.success(request, "You've enrolled in a schedule.")
    return HttpResponseRedirect(reverse('scheduleadvisor:schedules'))

def disenroll(request, pk):
    if not request.user.groups.filter(name='Student').exists():
                return HttpResponseRedirect(reverse('scheduleadvisor:not_authorized'))
    try:
        schedule = Schedule.objects.get(student=request.user.student, id=pk)
    except Schedule.DoesNotExist:
        return HttpResponseRedirect(reverse('scheduleadvisor:index'))
    schedule.status = "Approved"
    schedule.save()
    messages.success(request, "You've disenrolled from your schedule.")
    return HttpResponseRedirect(reverse('scheduleadvisor:schedules'))

def scheduleDetailsView(request, pk):
    if not request.user.groups.filter(name='Student').exists():
                return HttpResponseRedirect(reverse('scheduleadvisor:not_authorized'))
    try:
        schedule = Schedule.objects.get(student=request.user.student, id=pk)
    except Schedule.DoesNotExist:
        return HttpResponseRedirect(reverse('scheduleadvisor:index'))
    #gets the schedules that are currently part of that schedule
    schedule_courses = schedule.schedulecourse_set.all()
    #get schedule id
    schedule_id = schedule.id

    monday_courses = []
    tuesday_courses = []
    wednesday_courses = []
    thursday_courses = []
    friday_courses = []

    #organizing the schedule courses into days of the week so that they can be displayed
    for s in schedule_courses:
        days = s.days
        if "Mo" in days:
            monday_courses.append(s)
        if "Tu" in days:
            tuesday_courses.append(s)
        if "We" in days:
            wednesday_courses.append(s)
        if "Th" in days:
            thursday_courses.append(s)
        if "Fr" in days:
            friday_courses.append(s)

        #putting the courses into chronological order
        monday_courses.sort(key=lambda course: datetime.strptime(course.start_time, "%I:%M %p"))
        tuesday_courses.sort(key=lambda course: datetime.strptime(course.start_time, "%I:%M %p"))
        wednesday_courses.sort(key=lambda course: datetime.strptime(course.start_time, "%I:%M %p"))
        thursday_courses.sort(key=lambda course: datetime.strptime(course.start_time, "%I:%M %p"))
        friday_courses.sort(key=lambda course: datetime.strptime(course.start_time, "%I:%M %p"))

    context = {
        'schedule': schedule,
        'schedule_id': schedule_id,
        'mondaycourses': monday_courses,
        'tuesdaycourses': tuesday_courses,
        'wednesdaycourses': wednesday_courses,
        'thursdaycourses': thursday_courses,
        'fridaycourses': friday_courses

    }
    return render(request, 'scheduleadvisor/scheduledetails.html', context)

def button_to_details(request, pk):
    if not request.user.groups.filter(name='Student').exists():
                return HttpResponseRedirect(reverse('scheduleadvisor:not_authorized'))
    try: 
        schedule = Schedule.objects.all().get(student=request.user.student, id=pk)
    except Schedule.DoesNotExist:
        return HttpResponseRedirect(reverse('scheduleadvisor:index'))
    return HttpResponseRedirect(reverse('scheduleadvisor:schedule_details_view', args=(pk,)))

def adviseesListView(request):
    if not request.user.groups.filter(name='Advisor').exists():
                return HttpResponseRedirect(reverse('scheduleadvisor:not_authorized'))
    
    advisor = request.user.advisor

    #get all advisees of the advisor
    advisees = advisor.student_set.all()

    #get users in group Student who do not have advisors 
    students_without_advisor = []
    users = User.objects.filter(groups__name='Student')
    print(users)
    for user in users:
        try:
            #get the student object associated with the user
            student = Student.objects.get(user=user)
        except Student.DoesNotExist:
            student = Student.objects.create(user=user, stud_name=user.get_full_name(), username=user.get_username(), email=user.email, advisor=None)
            cart = Cart.objects.create(student=student)
        #if student doesn't have an advisor add to list
        if student.advisor is None:
            students_without_advisor.append(student)

    context={
        'advisees': advisees,
        'students_without_advisor': students_without_advisor
    }

    return render(request, 'scheduleadvisor/advisees.html', context)

def add_student_as_advisee(request, pk):
    if not request.user.groups.filter(name='Advisor').exists():
        return HttpResponseRedirect(reverse('scheduleadvisor:not_authorized'))
    try:
        student = Student.objects.get(id=pk)
    except Student.DoesNotExist:
        return HttpResponseRedirect(reverse('scheduleadvisor:index'))

    student.advisor = request.user.advisor
    student.save()
    return HttpResponseRedirect(reverse('scheduleadvisor:advisees_list_view'))

def notAuthorized(request):
    return render(request, 'scheduleadvisor/notauthorized.html')
