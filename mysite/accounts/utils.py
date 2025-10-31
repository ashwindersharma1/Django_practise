from django.shortcuts import redirect

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        # ✅ Check if user is logged in
        if not request.session.get('user_id'):
            return redirect('login')

        # ✅ Check if admin
        if request.session.get('user_role') == 'admin':
            return view_func(request, *args, **kwargs)

        # ✅ If not admin, redirect to user home
        return redirect('user_dashboard')
    return wrapper


def user_required(view_func):
    def wrapper(request, *args, **kwargs):
        # ✅ Check if user is logged in
        if not request.session.get('user_id'):
            return redirect('login')

        # ✅ If not admin, allow access
        if request.session.get('user_role') != 'admin':
            return view_func(request, *args, **kwargs)

        # ✅ Admins should go to admin dashboard
        return redirect('admin_dashboard')
    return wrapper
