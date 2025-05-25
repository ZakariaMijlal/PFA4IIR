from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from .models import Course, CourseMaterial
from .forms import CourseMaterialForm, CourseForm

def home(request):
    return render(request, 'core/home.html')

@login_required
def dashboard(request):
    if request.user.groups.filter(name='Professors').exists():
        # Handle course creation
        course_form = CourseForm(request.POST or None)
        material_form = CourseMaterialForm(request.user, request.POST or None, request.FILES or None)

        if request.method == 'POST':
            # Handle course creation
            if 'create_course' in request.POST and course_form.is_valid():
                new_course = course_form.save(commit=False)
                new_course.professor = request.user
                new_course.save()
                return redirect('dashboard')

            # Handle material upload
            if 'upload_material' in request.POST and material_form.is_valid():
                new_material = material_form.save(commit=False)
                new_material.uploaded_by = request.user
                new_material.save()
                return redirect('dashboard')

        # Get professor's data
        professor_courses = Course.objects.filter(professor=request.user)
        professor_materials = CourseMaterial.objects.filter(uploaded_by=request.user)

        return render(request, 'core/professor_dashboard.html', {
            'course_form': course_form,
            'material_form': material_form,
            'courses': professor_courses,
            'materials': professor_materials
        })

    elif request.user.groups.filter(name='Students').exists():
        # Students see all courses with their materials
        all_courses = Course.objects.all()
        return render(request, 'core/student_dashboard.html', {
            'courses': all_courses
        })

    else:
        return render(request, 'core/home.html', {
            'error': 'You are not assigned to a role (Student/Professor).'
        })