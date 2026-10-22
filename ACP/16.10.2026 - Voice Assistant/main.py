import re
import pyttsx3
import colorama
import os, shutil, platform, subprocess, urllib.request, time
import speech_recognition as sr
from colorama import Fore
from datetime import datetime
from openai import OpenAI

colorama.init(autoreset=True)

HOST = "http://localhost:11434"

client = OpenAI(
    base_url=f"{HOST}/v1",
    api_key="ollama"
)

recognizer = sr.Recognizer()

MODEL = "llama3.2"

SYSTEM_PROMPT = (
    "You are a helpful, friendly AI assistant. "
    "Reply in short plain sentences with no markdown, bullet points or emojis."
)
MAX_HISTORY = 20
messages = [
    {
        "role": "system", 
        "content": SYSTEM_PROMPT
    }
]

def is_running():
    try:
        urllib.request.urlopen(HOST, timeout=2)
        return True
    except Exception:
        return False

def find_ollama():
    path = shutil.which("ollama")
    if path:
        return path
 
    if platform.system() == "Windows":
        local = os.environ.get("LOCALAPPDATA", "")
        candidate = os.path.join(local, "Programs", "Ollama", "ollama.exe")
        if os.path.exists(candidate):
            return candidate
 
    return None

def install_ollama():
    try:
        if platform.system() == "Windows":
            command = "irm https://ollama.com/install.ps1 | iex"
            subprocess.run(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],check=True)
            return True
        else:
            command = "curl -fsSL https://ollama.com/install.sh | sh"
            subprocess.run(["bash", "-c", command], check=True)
            return True
    except Exception as e:
        print(f"{Fore.LIGHTRED_EX}Error: {e}")
        return None

def start_server(exe):
    print(f"{Fore.LIGHTGREEN_EX}Starting Ollama server...")
    subprocess.Popen([exe, "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(30):
        if is_running():
            return True
        time.sleep(0.5)
    return False

def has_model(exe, model):
    result = subprocess.run([exe, "list"], capture_output=True, text=True)
    for line in result.stdout.splitlines()[1:]:
        name = line.split()[0] if line.split() else ""
        if name == model or name.split(":")[0] == model:
            return True
    return False
 
 
def ensure_ollama(model):
    exe = find_ollama()
 
    if not exe:
        answer = input(f"{Fore.LIGHTCYAN_EX}⬇️  Ollama is not installed. Install it now? [y/N] ").strip().lower()
        if answer != "y": return False
        if not install_ollama(): print(f"{Fore.LIGHTRED_EX}❌ Installation failed."); return False
        exe = find_ollama()
        if not exe: print(f"{Fore.LIGHTRED_EX}❌ Installed, but not found on PATH yet. Restart your terminal and run again."); return False
 
    if not is_running():
        if not start_server(exe):
            print("Could not start the Ollama server.")
            return False
 
    if not has_model(exe, model):
        print(f"Downloading model {model}...")
        if subprocess.run([exe, "pull", model]).returncode != 0:
            print("Model download failed.")
            return False
 
    return True

def clean_for_speech(text):
    text = re.sub(r"[*_`#>]+", "", text)
    return re.sub(r"\s+", " ", text).strip()

def speak(text):
    engine = pyttsx3.init()
    engine.setProperty("rate", 150)
    engine.say(clean_for_speech(text))
    engine.runAndWait()

def say(text):
    print(f"\n{Fore.LIGHTGREEN_EX}{text}\n")
    speak(text)

def get_audio():
    with sr.Microphone() as source:
        print(f"{Fore.LIGHTMAGENTA_EX}🎙️ Speak now....")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)

        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            command = recognizer.recognize_google(audio)
            print(f"✅ You said: {command}")
            return command.lower()

        except sr.WaitTimeoutError:
            print(f"{Fore.LIGHTRED_EX}⏱️ No speech detected")
        except sr.UnknownValueError:
            print(f"{Fore.LIGHTRED_EX}❌ Could not understand audio")
        except sr.RequestError as e:
            print(f"{Fore.LIGHTRED_EX}❌ API error: {e}")

    return ""


def create_ai_response(command):
    messages.append({
        "role": "user", 
        "content": command
    })

    try:
        response = client.chat.completions.create(model=MODEL, messages=messages)
        answer = response.choices[0].message.content or ""
        answer = re.sub(r"<think>.*?</think>", "", answer, flags=re.DOTALL).strip()
        messages.append({"role": "assistant", "content": answer})

        if len(messages) > MAX_HISTORY + 1: del messages[1:len(messages) - MAX_HISTORY]

        print(f"\n{Fore.LIGHTGREEN_EX}{answer}\n")
        print(type(answer))
        speak(answer)

    except KeyboardInterrupt:
        print(f"{Fore.LIGHTRED_EX}❌ Keyboard Interrupt")
        messages.pop()

    except Exception as e:
        print(f"\n{Fore.LIGHTRED_EX}Error: {e}\n")
        if messages[-1]["role"] == "user":
            messages.pop()


def respond_to_command(command):
    words = set(re.findall(r"[a-z']+", command))

    if words & {"exit", "quit", "goodbye"}:
        say("Goodbye!")
        return False

    if "hello" in words or "hi" in words:
        say("Hi there! How can I help you?")

    elif "your name" in command:
        say("I am your Python voice assistant.")

    elif "time" in words and len(words) <= 5:
        say(f"The time is {datetime.now().strftime('%H:%M')}")

    else:
        create_ai_response(command)

    return True


def main():
    if not ensure_ollama(MODEL):
        return

    speak("Voice assistant activated. Say something!")

    try:
        while True:
            command = get_audio()
            if command and not respond_to_command(command):
                break
    except KeyboardInterrupt:
        print(f"\n{Fore.LIGHTRED_EX}❌ Keyboard Interrupt")


if __name__ == "__main__":
    main()