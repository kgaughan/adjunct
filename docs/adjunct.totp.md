# adjunct.totp

_Adjunct_ has a [TOTP](https://www.rfc-editor.org/rfc/rfc6238) implementation,
providing a second factor of authentication.

```py
from adjunct import totp

# Instantiate a TOTP object with a reasonable set of defaults
t = totp.TOTP()

# Generate a token
print(t.generate())
```

To allow the object to be stored in a user's profile, you can use the `to_dict`
method to you can serialise it as JSON or another format, and subsequently
recreate the object using the `from_dict` class method.

```py
import json

# Dump it as JSON
t1 = totp.TOTP()
as_json = json.dumps(t1.to_dict())

# Take some previously serialised JSON and recreate the object.
t2 = totp.TOTP.from_dict(json.loads(as_json))
```

It can also be converted into an [OTP key URI], which can be presented to the
user so they can add it to their OTP generator.

[OTP key URI]: https://github.com/google/google-authenticator/wiki/Key-Uri-Format

```py
print(t1.to_url("jane.doe@example.com", issuer="Yoyodyne"))
```

Finally, to check a code, pass it to `generate` method to check a code provided by the user.

```py
while True:
    otp = input("Enter your TOTP: ")
    if t1.check(otp):
        break
    print("Invalid! Try again.")
print("Valid")
```

By default it uses the current window and the previous one. You can use the `window` named argument to change this from the default.

::: adjunct.totp
    options:
      show_root_heading: false
      show_source: false
