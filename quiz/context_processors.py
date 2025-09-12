def user_role(request):
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.is_staff:
            return {"user_role": "admin"}
        else:
            return {"user_role": "user"}
    return {"user_role": None}
