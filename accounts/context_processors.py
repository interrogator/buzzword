from django.contrib.auth.forms import AuthenticationForm


def forms(request):
    return {"login_form": AuthenticationForm()}
