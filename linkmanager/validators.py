import re


def color(c_str, color='\033[1;42m'):
    return '{color}{c_str}{cb}'.format(color=color, c_str=c_str, cb='\033[1;m')


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
            color(self.message, color='\033[7;40;31m')
            + color(' %s ' % value, color='\033[5;41;37m')
        )
        return False


class URLValidator(RegexValidator):
    regex = re.compile(
        r'^(?:[a-z0-9\.\-]*)://'  # scheme is validated separately
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    message = 'Enter a valid URL:'
    schemes = ['http', 'https']

    def __init__(self, schemes=None, **kwargs):
        super(URLValidator, self).__init__(**kwargs)
        if schemes is not None:
            self.schemes = schemes

    def __call__(self, value):
        return super(URLValidator, self).__call__(value)
