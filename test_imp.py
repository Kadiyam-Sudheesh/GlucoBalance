try:
    import flask
    print("flask: OK")
except ImportError as e:
    print(f"flask: FAIL {e}")

try:
    from deep_translator import GoogleTranslator
    print("dt: OK")
except ImportError as e:
    print(f"dt: FAIL {e}")
