import os
import gettext as gettext_module
from threading import local

# Translations are cached in a dictionary for every language+app tuple.
# The active translations are stored by threadid to make them thread local.
_translations = {}
_active = local()
# The default translation is based on the settings file.
_default = None


def to_locale(language, to_lower=False):
    """
    Turns a language name (en-us) into a locale name (en_US). If 'to_lower' is
    True, the last component is lower-cased (en_us).
    """
    p = language.find('-')
    if p >= 0:
        if to_lower:
            return language[:p].lower() + '_' + language[p + 1:].lower()
        else:
            # Get correct locale for sr-latn
            if len(language[p + 1:]) > 2:
                return language[:p].lower() + '_' + language[p + 1].upper()
                + language[p + 2:].lower()
            return language[:p].lower() + '_' + language[p + 1:].upper()
    else:
        return language.lower()


def to_language(locale):
    """Turns a locale name (en_US) into a language name (en-us)."""
    p = locale.find('_')
    if p >= 0:
        return locale[:p].lower() + '-' + locale[p + 1:].lower()


class LinkManagerTranslation(gettext_module.GNUTranslations):
    """
    This class sets up the GNUTranslations context with regard to output
    charset.
    """
    def __init__(self, *args, **kw):
        gettext_module.GNUTranslations.__init__(self, *args, **kw)
        self.set_output_charset('utf-8')
        self.linkmanager_output_charset = 'utf-8'
        self.__language = '??'

    def merge(self, other):
        self._catalog.update(other._catalog)

    def set_language(self, language):
        self.__language = language
        self.__to_language = to_language(language)

    def language(self):
        return self.__language

    def to_language(self):
        return self.__to_language

    def __repr__(self):
        return "<LinkManagerTranslation lang:%s>" % self.__language


def translation(language):
    """
    Returns a translation object.

    This translation object will be constructed out of multiple GNUTranslations
    objects by merging their catalogs. It will construct a object for the
    requested language and add a fallback to the default language, if it's
    different from the requested language.
    """
    LANGUAGE_CODE = 'fr'
    global _translations

    t = _translations.get(language, None)
    if t is not None:
        return t

    globalpath = os.path.join('linkmanager', 'locale')

    def _fetch(lang, fallback=None):

        global _translations

        res = _translations.get(lang, None)
        if res is not None:
            return res

        loc = to_locale(lang)

        def _translation(path):
            try:
                t = gettext_module.translation(
                    'linkmanager', path, [loc], LinkManagerTranslation
                )
                t.set_language(lang)
                return t
            except IOError:
                return None

        res = _translation(globalpath)

        # We want to ensure that, for example,  "en-gb" and "en-us" don't share
        # the same translation object (thus, merging en-us with a local update
        # doesn't affect en-gb), even though they will both use the core "en"
        # translation. So we have to subvert Python's internal gettext caching.
        base_lang = lambda x: x.split('-', 1)[0]
        if base_lang(lang) in [base_lang(trans) for trans in _translations]:
            res._info = res._info.copy()
            res._catalog = res._catalog.copy()

        def _merge(path):
            t = _translation(path)
            if t is not None:
                if res is None:
                    return t
                else:
                    res.merge(t)
            return res

        if res is None:
            if fallback is not None:
                res = fallback
            else:
                return gettext_module.NullTranslations()
        _translations[lang] = res
        return res

    default_translation = _fetch(LANGUAGE_CODE)
    current_translation = _fetch(language, fallback=default_translation)

    return current_translation


def do_translate(message, translation_function):
    """
    Translates 'message' using the given 'translation_function' name -- which
    will be either gettext or ugettext. It uses the current thread to find the
    translation object to use. If no current translation is activated, the
    message will be run through the default translation object.
    """
    LANGUAGE_CODE = 'fr'
    global _default

    # str() is allowing a bytestring message to remain bytestring on Python 2
    eol_message = message.replace(
        str('\r\n'), str('\n')
    ).replace(
        str('\r'), str('\n')
    )
    t = getattr(_active, "value", None)
    if t is not None:
        result = getattr(t, translation_function)(eol_message)
    else:
        if _default is None:
            _default = translation(LANGUAGE_CODE)
        result = getattr(_default, translation_function)(eol_message)
    return result


def gettext(message):
    """
    Returns a string of the translation of the message.
    """
    return do_translate(message, 'gettext')
