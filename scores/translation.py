from modeltranslation.translator import register, TranslationOptions
from .models import Reason


@register(Reason)
class ReasonTranslationOptions(TranslationOptions):
    fields = ('name',)
