from django.conf import settings


def get_applications(include=None, exclude=None):
    if include:
        return include
    apps = settings.INSTALLED_APPS
    if exclude:
        apps = tuple(set(apps) - set(exclude))
    return apps