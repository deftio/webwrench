"""01 - Hello World

The simplest possible webwrench app: a title and some text.
Run: python examples/01_hello_world.py
"""

import webwrench as ww

ww.title("Hello World")
ww.text("Welcome to webwrench!")
ww.markdown("This is a **minimal** example with zero configuration.")

if __name__ == "__main__":
    ww.serve()
