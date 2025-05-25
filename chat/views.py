from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from django.views.generic import ListView, CreateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.http import JsonResponse
from .models import ChatMessage
from .forms import ChatMessageForm
from core.models import Course
import requests
import re
import markdown
from django.utils.safestring import mark_safe
from django.utils.html import escape
import json
from django.views.decorators.http import require_POST
from django.http import JsonResponse

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(lambda u: u.groups.filter(name='Students').exists()), name='dispatch')
class CourseChatView(CreateView, ListView):
    model = ChatMessage
    template_name = 'chat/chat_interface.html'
    form_class = ChatMessageForm
    # fields = ['message']
    context_object_name = 'messages'

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        return ChatMessage.objects.filter(
            course_id=course_id,
            user=self.request.user
        ).order_by('timestamp')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = Course.objects.get(id=self.kwargs['course_id'])
        return context

    def form_valid(self, form):
        course = Course.objects.get(id=self.kwargs['course_id'])
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.course = Course.objects.get(id=self.kwargs['course_id'])
        self.object.response = self.get_ai_response(self.object.message)
        self.object.is_ai_response = True
        self.object.save()
        return super().form_valid(form)


    def clean_and_convert_markdown(text):
        """Process AI response to clean and convert markdown"""
        # Remove <think> patterns first
        # text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)

        # Convert markdown to HTML
        html = markdown.markdown(
            text,
            extensions=[
                'fenced_code',  # For code blocks
                'nl2br',       # Convert newlines to <br>
                'tables',      # For markdown tables
            ]
        )
        return mark_safe(html)

    def get_ai_response(self, prompt):
        try:
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': 'deepseek-r1:8b',
                    'prompt': prompt,
                    'stream': False
                },
            )
            raw_response = response.json().get('response', 'Error processing response')

            # Only convert markdown without any content filtering
            html_response = markdown.markdown(
                raw_response,
                extensions=[
                    'fenced_code',  # For code blocks
                    'tables',       # For markdown tables
                    'nl2br',        # Convert newlines to <br>
                    'mdx_math'      # For LaTeX math support (optional)
                ],
                extension_configs={
                    'mdx_math': {
                        'enable_dollar_delimiter': True
                    }
                }
            )
            return mark_safe(html_response)

        except Exception as e:
            return mark_safe(f"<div class='ai-error'>AI Service Error: {str(e)}</div>")

    def get_success_url(self):
        return reverse_lazy('course-chat', kwargs={'course_id': self.kwargs['course_id']})