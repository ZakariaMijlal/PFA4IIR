from django import forms
from .models import Course, CourseMaterial

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'code']

class CourseMaterialForm(forms.ModelForm):
    class Meta:
        model = CourseMaterial
        fields = ['course', 'title', 'file']

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['course'].queryset = Course.objects.filter(professor=user)