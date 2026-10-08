import speech_recognition as sr
import colorama
from colorama import Fore
from typing import Literal
from deep_translator import MyMemoryTranslator

colorama.init(autoreset=True)

def display_language_options(method: Literal["speaking", "translation", "sentence"]):
    if method not in ["speaking", "translation", "sentence"]: raise Exception("Not options")

    language_dict = {
        '1': ['English', 'en-US'],
        '2': ['Chinese', 'zh-CN'],
        '3': ['Hindi', 'hi-IN'],
        '4': ['Spanish', 'es-ES', 'default'],
        '5': ['French', 'fr-FR'],
        '6': ['Arabic', 'ar-SA'],
        '7': ['Bengali', 'bn-IN'],
        '8': ['Portuguese', 'pt-BR'],
        '9': ['Russian', 'ru-RU'],
        '10': ['Urdu', 'ur-PK'],
        '11': ['Indonesian', 'id-ID'],
        '12': ['German', 'de-DE'],
        '13': ['Japanese', 'ja-JP']
    }

    print(f"{Fore.GREEN}📋 Choose one of the languages for {method}")

    for sl, ln_data in language_dict.items():
        (lang_name, reg_code, *tags) = ln_data
        default_tag = " - Default" if "default" in tags else ""
        print(f"{Fore.LIGHTWHITE_EX}[{Fore.LIGHTBLACK_EX}{sl}{Fore.LIGHTWHITE_EX}]. {Fore.LIGHTCYAN_EX}{lang_name} ({reg_code}){default_tag}")

    lang_choice = input(f"{Fore.LIGHTBLUE_EX}📋 Choose one of the languages (1-13): ")

    if lang_choice in language_dict:
        language = language_dict[lang_choice]
        print(f"{Fore.LIGHTMAGENTA_EX}🔡 Chosen Language: {language[0]}")
    else:
        language = language_dict['4']
        print(f"{Fore.LIGHTMAGENTA_EX}❌ Invalid input or no input. Default Chosen Language: {language[0]}")

    return language

def speech_to_text():
    recognizer = sr.Recognizer()
    speaking_language = display_language_options("speaking")

    try:
        with sr.Microphone() as source:
            print(f"{Fore.LIGHTMAGENTA_EX}🗣️  Please speak in {speaking_language[0]}...")
            audio = recognizer.listen(source)

        text = recognizer.recognize_google(audio, language=speaking_language[1])

        print(f"{Fore.LIGHTMAGENTA_EX}🌍 Spoken Language: {speaking_language[1]}")
        print(f"{Fore.LIGHTMAGENTA_EX}📝 You said: {text}")

        return text, speaking_language

    except sr.WaitTimeoutError: raise Exception(f"{Fore.RED}❌ Timeout. Please try again.")
    except sr.UnknownValueError: raise Exception(f"{Fore.RED}❌ Could not understand the audio.")
    except sr.RequestError as e: raise Exception(f"{Fore.RED}❌ API Error: {e}")

def translate_text(text, source_language="es-ES", target_language="es-ES"):
    translator = MyMemoryTranslator(source=source_language,target=target_language)
    translation = translator.translate(text)
    print(f"{Fore.LIGHTMAGENTA_EX}🌐 Translated Text: {translation}")
    return translation

def main():
    target_language = display_language_options("translation")
    translation_method_input = input("❓ Write or Speak? (1 = Write, 2 = Speak):").strip()
    if translation_method_input == '1':
        selected_language = display_language_options("sentence")
        original_text = input(f"{Fore.LIGHTMAGENTA_EX}📝 Write the sentence in {selected_language[0]}: ")
    elif translation_method_input == '2':
        original_text, spoken_language = speech_to_text()
    else: raise ValueError(f"{Fore.RED}❌ Invalid input. Please try again.")

    if original_text:
        translated_text = translate_text(original_text, 
                                         source_language=selected_language[1] if translation_method_input == '1' else spoken_language[1],
                                         target_language=target_language[1])
    

if __name__ == "__main__":
    main()