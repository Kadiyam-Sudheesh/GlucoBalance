from deep_translator import GoogleTranslator

try:
    print("Attempting translation...")
    translator = GoogleTranslator(source='auto', target='hi')
    result = translator.translate("Hello world")
    print(f"Success! Result: {result}")
except Exception as e:
    print(f"Error: {e}")
