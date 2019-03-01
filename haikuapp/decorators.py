from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from haikuapp.models import Card


def check_card_owner(func):
    @login_required
    def check_owner(request, *args, **kwargs):
        card_id = kwargs["card_id"]
        try:
            card = Card.objects.get(pk=card_id)
        except Card.DoesNotExist:
            messages.add_message(request, messages.WARNING, "Card not found")
            return redirect('cards')

        if not (card.owner.id == request.user.id):
            messages.add_message(request, messages.WARNING, "It is not yours ! You are not permitted !")
            return redirect('cards')
        return func(request, *args, **kwargs)
    return check_owner

