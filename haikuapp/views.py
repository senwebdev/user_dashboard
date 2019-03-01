from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from haikuapp.backend import EmailBackend
from django.shortcuts import render, redirect, get_object_or_404
from haikuapp.decorators import check_card_owner
from haikuapp.forms import TemlpateFieldForm, UpdateCardForm
from haikuapp.models import UserActivate, Category, Template, Card, CardField, TemplateFields, ImageCard
from . import forms


def home(request):
    return redirect(wizard)


def login(request):
    """
    Login view
    :param request:
    :return:
    """
    context = {"url": "login"}
    if request.method == 'POST':
        form = forms.LoginForm(request.POST)
        context['form'] = form
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = EmailBackend.authenticate(request, username=email, password=password)
            if user:
                auth_login(request, user)
                return redirect(wizard)
            else:
                messages.add_message(request, messages.WARNING, "Wrong email or password")
                return render(request, 'login.html', context)
        else:
            return render(request, 'login.html', context)
    else:
        context['form'] = forms.LoginForm()
    return render(request, 'login.html', context)


@login_required
def logout(request):
    """
    Logout view
    :param request:
    :return:
    """
    auth_logout(request)
    return redirect(login)


@login_required
def wizard(request):
    """
    Dashboard view
    :param request:
    :return:
    """
    return render(request, 'wizard.html')


@login_required()
def cards(request):
    """
    User cards view
    :param request:
    :return:
    """
    card_list = Card.objects.filter(owner=request.user).all()
    return render(request, 'cards.html', {'cards': card_list})


@check_card_owner
def card_delete(request, card_id):
    """
    Delete card
    :param request:
    :param card_id:
    :return:
    """
    try:
        get_object_or_404(Card, pk=card_id).delete()
        messages.add_message(request, messages.SUCCESS, "Card was deleted successfully")
    except:  # except what? (I think try..except not needed here)
        messages.add_message(request, messages.WARNING, "Card wasn't deleted")
    return redirect('cards')


@check_card_owner
def card(request, card_id):
    """
    View card
    :param request:
    :param card_id:
    :return:
    """
    if request.method == 'POST':
        form = UpdateCardForm(request.POST, request.FILES, card_id=card_id)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            card = Card.objects.filter(pk=card_id)
            for key, value in list(cleaned_data.items()):
                if key.startswith("field_id_"):
                    card_field_id = key.replace("field_id_", "")
                    card_field = get_object_or_404(CardField, pk=card_field_id)
                    card_field.value = value
                    card_field.save()
                    del cleaned_data[key]
            update_dict = dict()
            if cleaned_data['date'] == 'specificDate':
                update_dict["date_from"] = cleaned_data['date_from']
                update_dict["date_to"] = cleaned_data['date_to']
                if cleaned_data['hour'] == 'specificHour':
                    update_dict["time_from"] = cleaned_data['time_from']
                    update_dict["time_to"] = cleaned_data['time_to']
                else:
                    update_dict["time_from"] = None
                    update_dict["time_to"] = None
            else:
                update_dict["date_from"] = None
                update_dict["date_to"] = None
                update_dict["time_from"] = None
                update_dict["time_to"] = None
            card.update(**update_dict)
            messages.add_message(request, messages.SUCCESS, "Card was updated successfully")
            return redirect('cards')
        else:
            messages.add_message(request, messages.WARNING, "Card wasn't updated")
    card = get_object_or_404(Card, pk=card_id)
    fields = card.fields.all()
    return render(request, 'card.html', {'card': card, 'fields': fields})


@login_required
def category(request):
    """
    Category view
    :param request:
    :return:
    """
    category = Category.objects.all()
    return render(request, 'category.html', {'category': category})


@login_required
def templates(request, category_id):
    """
    Templates view
    :param request:
    :param category_id:
    :return:
    """
    category = get_object_or_404(Category, pk=category_id)
    template = Template.objects.filter(category_id=category).all()
    return render(request, 'templates.html', {'category': category, 'template': template})


@login_required
def create_card(request, template_id):
    """
    Create vard view
    :param request:
    :param template_id:
    :return:
    """
    template = get_object_or_404(Template, pk=template_id)
    fields = template.fields.all()
    if request.method == 'POST':
        form = TemlpateFieldForm(request.POST, request.FILES, template_id=template_id)
        #files = request.FILES.getlist('images')
        if form.is_valid():
            cleaned_data = form.cleaned_data
            card = Card()
            card.template = template
            card.owner = request.user
            card.user_input = cleaned_data['user_input']
            #card.image_url = cleaned_data['images']
            if cleaned_data['date'] == 'specificDate':
                card.date_from = cleaned_data['date_from']
                card.date_to = cleaned_data['date_to']
                if cleaned_data['hour'] == 'specificHour':
                    card.time_from = cleaned_data['time_from']
                    card.time_to = cleaned_data['time_to']
            card.save()
            for key, value in list(cleaned_data.items()):
                if key.startswith("field_id_"):
                    template_field_id = key.replace("field_id_", "")
                    card_field = CardField()
                    card_field.card = card
                    card_field.variable = variable
                    card_field.template_field = get_object_or_404(TemplateFields, pk=template_field_id)
                    card_field.value = value
                    card_field.save()
                    del cleaned_data[key]
            #for file in files:
            #    card_image = ImageCard()
            #    card_image.card = card
            #    card_image.image_url = file
            #    card_image.save()
            messages.add_message(request, messages.SUCCESS, "Card was created successfully")
            return redirect('cards')
        else:
            errors = dict(data={f: e.get_json_data() for f, e in form.errors.items()})
            for key, value in errors['data'].items():
                messages.add_message(request, messages.WARNING, '{} - {}'.format(key.capitalize(), value[0]['message']))
            messages.add_message(request, messages.WARNING, "Card wasn't created")
    return render(request, 'create_card.html', {'fields': fields, 'template': template})


def activation(request):
    """
    Activation view
    :param request:
    :return:
    """
    context = {"url": "activation"}
    if request.method == 'POST':
        form = forms.RegisterForm(request.POST)
        context['form'] = form
        if form.is_valid():
            password = form.cleaned_data.get('password')
            activation_token = request.POST.get('activation_token')
            user_activate = UserActivate.objects.filter(token=activation_token).first()
            if user_activate.user.is_active is False:
                user_activate.user.set_password(password)
                user_activate.user.is_active = True
                user_activate.user.save()
            user = EmailBackend.authenticate(request, username=user_activate.user.email, password=password)
            if user:
                auth_login(request, user)
            return redirect('wizard')
        else:
            return render(request, 'register.html', context)
    else:
        token = request.GET.get('token')
        if not token:
            return redirect(login)
        user_token = UserActivate.objects.filter(token=token).first()
        if user_token is not None:
            user = user_token.user
            if user.is_active is True:
                messages.add_message(request, messages.INFO, "Account already activated")
                return redirect(login)
            else:
                context['form'] = forms.RegisterForm()
                context['token'] = token
                messages.add_message(request, messages.INFO,
                                     "Please enter your new password. Your email - {}".format(user_token.user.email))
                return render(request, 'register.html', context)
        else:
            messages.add_message(request, messages.WARNING, "Wrong url")
            return redirect(login)
