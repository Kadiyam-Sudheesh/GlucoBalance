from deep_translator import GoogleTranslator

# Create a long text (> 5000 chars)
long_text = "This is a sentence. " * 500

print(f"Text length: {len(long_text)}")

try:
    print("Attempting long translation...")
    translator = GoogleTranslator(source='auto', target='hi')
    # Use standard translate method
    result = translator.translate(long_text) 
    print(f"Success! Result length: {len(result)}")
except Exception as e:
    print(f"Error: {e}")
