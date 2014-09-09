import re

from clint.textui.colored import black, white


class RegexValidator(object):
    regex = ''
    message = 'Enter a valid value.'

    def __init__(self, regex=None, message=None):
        if regex is not None:
            self.regex = regex
        if message is not None:
            self.message = message

        # Compile the regex if it was not passed pre-compiled.
        if isinstance(self.regex, str):
            self.regex = re.compile(self.regex)

    def __call__(self, value):
        """
        Validates that the input matches the regular expression.
        """
        if self.regex.search(value):
            return True
        print(
            black(self.message, bold=True, bg_color='red')
            + white(value, bg_color='red')
        )
        return False


class URLValidator(RegexValidator):
    regex = re.compile(
        # scheme is validated separately
        r'^(?:[a-z0-9\.\-]*)://'
        # domain...
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)'
        '+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        # localhost...
        r'localhost|'
        # ...or ipv4
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'
        # ...or ipv6
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'
        # optional port
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    message = 'Enter a valid URL: '
    schemes = ['http', 'https']

    def __init__(self, schemes=None, **kwargs):
        super(URLValidator, self).__init__(**kwargs)
        if schemes is not None:
            self.schemes = schemes

    def __call__(self, value):
        """
        Validate the URL
        """
        return super(URLValidator, self).__call__(value)
