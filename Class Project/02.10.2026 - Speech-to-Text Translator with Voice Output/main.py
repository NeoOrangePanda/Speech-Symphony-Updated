## CHANGES ARE MARKED WITH COMMENTS - PLEASE CHECK

import speech_recognition as sr
import pyttsx3
from deep_translator import MyMemoryTranslator # !!!! LIBRARY CHANGE !!!! #

def speak(text, language="en"):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    voices = engine.getProperty('voices')

    if language == "en": engine.setProperty('voice', voices[0].id)
    else: engine.setProperty('voice', voices[1].id)

    engine.say(text)
    engine.runAndWait()

def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("???? Please speak now in English...")
        audio = recognizer.listen(source)

    try:
        print("???? Recognizing Speech...")
        text = recognizer.recognize_google(audio, language="en-US")
        print(f"✅ You said: {text}")
        return text

    except sr.UnknownValueError: print("❌ Could not understand the audio.")
    except sr.RequestError as e: print(f"❌ API Error: {e}")

    return ""

def translate_text(text, target_language="spanish"): # !!!! TEXT TRANSLATION PART !!!! #
    translator = MyMemoryTranslator(source="english",target=target_language)
    translation = translator.translate(text)
    print(f"🌐 Translated Text: {translation}")
    return translation

def display_language_options():
    print("???? Available translation languages: ")
    print("1. English")
    print("2. French")
    print("3. Spanish - Default")
    print("4. Bangla")
    print("5. Hindi")
    print("6. Arabic")
    print("7. Chinese")
    print("8. Malayalam")
    print("9. Indonesian")

    choice = input("Please select the target language number (1-9): ")

    language_dict = { # !!!! DICTIONARY CHANGED - USE REGIONAL CODES BESIDE THE ACTUAL LANGUAGE !!!! #
        "1": "en-US",
        "2": "fr-FR",
        "3": "es-ES",
        "4": "bn-IN",
        "5": "hi-IN",
        "6": "ar-SA",
        "7": "zh-CN",
        "8": "ml-IN",
        "9": "id-ID"
    }

    return language_dict.get(choice, 'es-ES')

def main():
    target_language = display_language_options()
    original_text = speech_to_text()
    if original_text:
        translated_text = translate_text(original_text, target_language=target_language)
        speak(translated_text, language=target_language)
        print("✅ Translation Spoken Out!")

if __name__ == "__main__": main()