from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views.generic import ListView, DetailView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import UserProfile
from django.contrib.auth.models import User
from .forms import MemberRegistrationForm

def register_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')
        
    if request.method == 'POST':
        form = MemberRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful! Welcome to LibrarySphere.")
            return redirect('core:dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = MemberRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return super().get_success_url()

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {
        'user': request.user,
        'profile': request.user.profile
    })

class LibrarianRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.profile.is_librarian()

class MemberListView(LibrarianRequiredMixin, ListView):
    model = UserProfile
    template_name = 'accounts/member_list.html'
    context_object_name = 'members'
    
    def get_queryset(self):
        qs = UserProfile.objects.filter(role='MEMBER').select_related('user').order_by('-created_at')
        q = self.request.GET.get('q')
        status = self.request.GET.get('status')
        if q:
            qs = qs.filter(user__first_name__icontains=q) | qs.filter(user__last_name__icontains=q) | qs.filter(membership_number__icontains=q) | qs.filter(user__email__icontains=q)
        if status:
            qs = qs.filter(membership_status=status)
        return qs

class MemberDetailView(LibrarianRequiredMixin, DetailView):
    model = UserProfile
    template_name = 'accounts/member_detail.html'
    context_object_name = 'member_profile'

class MemberUpdateView(LibrarianRequiredMixin, UpdateView):
    model = UserProfile
    template_name = 'accounts/member_form.html'
    fields = ['phone_number', 'address', 'membership_status', 'membership_expiry_date', 'admin_notes']
    context_object_name = 'member_profile'

    def get_success_url(self):
        return reverse_lazy('accounts:member_detail', kwargs={'pk': self.object.pk})
        
    def form_valid(self, form):
        messages.success(self.request, "Member profile updated successfully.")
        return super().form_valid(form)
