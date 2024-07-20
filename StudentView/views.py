from django.shortcuts import render
from FacultyView.models import Student
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.utils import timezone
import datetime
import csv
import os

present = set()

def add_manually_post(request):
    if request.method == 'POST':
        student_roll = request.POST.get("student_id")
        if student_roll:
            student = Student.objects.get(s_roll=student_roll)
            
            # Get the current date and time in local timezone
            current_datetime = timezone.localtime()
            current_date = current_datetime.date()
            current_time = current_datetime.time()

            # Check if the cookie exists and is set for today
            if 'attendance_submitted' in request.COOKIES:
                cookie_date_str = request.COOKIES['attendance_submitted']
                cookie_date = datetime.datetime.strptime(cookie_date_str, '%Y-%m-%d').date()

                if cookie_date == current_date:
                    # Attendance already marked today from this device
                    return render(request, "StudentView/AlreadySubmitted.html")

            # Update last attendance timestamp
            student.last_attendance = current_datetime
            student.save()

            present.add(student)

            # Log the attendance submission to a CSV file
            log_file_path = "attendance_log.csv"
            log_exists = os.path.isfile(log_file_path)
            
            with open(log_file_path, "a", newline='') as csvfile:
                log_writer = csv.writer(csvfile)
                if not log_exists:
                    log_writer.writerow(["Student ID", "Date", "Time"])  # Write header if file doesn't exist
                log_writer.writerow([student_roll, current_date, current_datetime.strftime('%I:%M %p')])

            # Set a cookie to track attendance submission
            response = HttpResponseRedirect("/submitted")
            response.set_cookie('attendance_submitted', current_date.strftime('%Y-%m-%d'), max_age=2*60)  # Expires in 2 minutes

            return response

    return HttpResponseRedirect(reverse("home"))  # Replace "home" with your actual home URL name

def submitted(request):
    return render(request, "StudentView/Submitted.html")
