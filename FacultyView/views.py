from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Student
import qrcode
import socket
from StudentView.views import present
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont


def qrgenerator():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()

    # Generate a unique identifier using the current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    link = f"http://{ip}:8000/add_manually?ts={timestamp.replace(' ', '_').replace(':', '-')}"
    
    # Function to generate and display a QR code
    def generate_qr_code(link, timestamp):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(link)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white").convert('RGB')

        # Add the timestamp to the image
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()  # Load a default font

        # Load a TrueType font and set the size
        font_path = "Arial.ttf"  # Update with the path to your .ttf file
        font_size = 20  # Set the desired font size
        font = ImageFont.truetype(font_path, font_size)

        # Calculate the position to draw the text
        text_position = (110, img.size[1] - 20)
        draw.text(text_position, timestamp, font=font, fill="black")

        # Save the image
        img.save("FacultyView/static/FacultyView/qrcode.png")

    generate_qr_code(link, timestamp)

# Call the function
qrgenerator()


def faculty_view(request):
    if request.method == "POST":
        student_roll = request.POST["student_id"]
        student = Student.objects.get(s_roll=student_roll)
        if student in present:
            present.remove(student)
        return HttpResponseRedirect("/")

    else:
        qrgenerator()
        return render(
            request,
            "FacultyView/FacultyViewIndex.html",
            {
                "students": present,
            },
        )


def add_manually(request):
    students = Student.objects.all().order_by("s_roll")
    return render(
        request,
        "StudentView/StudentViewIndex.html",
        {
            "students": students,
        },
    )
