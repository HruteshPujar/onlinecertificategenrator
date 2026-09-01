from .models import Participant


def get_participant(pk):

    return Participant.objects.select_related(
        "event"
    ).get(pk=pk)


def get_event_participants(event):

    return Participant.objects.select_related(
        "event"
    ).filter(
        event=event
    )