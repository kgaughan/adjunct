"""
Gravatar support.

For information on the parameters, see [the SDK](https://docs.gravatar.com/sdk/images/).
"""

import hashlib
from urllib import parse


def make_gravatar_img(
    email: str,
    size: int = 64,
    default: str = "identicon",
    rating: str = "pg",
) -> str:
    """Generate a Gravatar `<img>` tag for the given email address.

    Args:
        email: an email address
        size: the size of the gravatar to generate
        default: default image to generate
        rating: the rating associated with the image

    Returns:
        An `<img>` tag with suitable attributes.
    """
    url = make_gravatar(email, size, default, rating)
    return f'<img src="{url}" width="{size}" height="{size}" alt="">'


def make_gravatar(
    email: str,
    size: int = 64,
    default: str = "identicon",
    rating: str = "pg",
) -> str:
    """Generate a gravatar image URL.

    Args:
        email: an email address
        size: the size of the gravatar to generate
        default: default image to generate
        rating: the rating associated with the image

    Returns:
        A Gravatar URL.
    """
    params = {
        "s": str(size),
        "d": default,
        "r": rating,
    }

    # Omit the protocol so it'll work cleanly over both HTTP and HTTPS.
    digest = hashlib.md5(email.strip().lower().encode("utf-8")).hexdigest()  # noqa: S324
    return f"//www.gravatar.com/avatar/{digest}?{parse.urlencode(params)}"
