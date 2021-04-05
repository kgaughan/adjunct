"""
A reCAPTCHA_ client library.

.. _reCAPTCHA: http://www.google.com/recaptcha
"""

from urllib import parse, request

__all__ = ["make_markup", "check"]


VERIFY_URL = "http://www.google.com/recaptcha/api/verify"

MARKUP = """
<script type="text/javascript"
 src="//www.google.com/recaptcha/api/challenge?%(params)s"></script>
<noscript>
<iframe src="//www.google.com/recaptcha/api/noscript?%(params)s"
 height="300" width="500" frameborder="0"></iframe><br>
<textarea name="recaptcha_challenge_field" rows="3" cols="40"></textarea>
<input type="hidden" name="recaptcha_response_field" value="manual_challenge">
</noscript>
""".replace(
    "\n", ""
)


def make_markup(public_key, error=None):
    """
    Generate the HTML to display the CAPTCHA.
    """
    keys = {"k": public_key}
    if error is not None:
        keys["error"] = error
    return MARKUP % {"params": parse.urlencode(keys)}


def check(private_key, remote_ip, challenge, response):
    """
    Validate the CAPTCHA response.
    """
    if challenge.strip() == "" or response.strip() == "":
        return (False, "incorrect-captcha-sol")

    params = {
        "privatekey": private_key,
        "remoteip": remote_ip,
        "challenge": challenge,
        "response": response,
    }
    with request.urlopen(VERIFY_URL, parse.urlencode(params)) as fh:
        response = fh.read().splitlines()
        if response[0] == "false":
            return (False, response[1])
        return (True, "")
