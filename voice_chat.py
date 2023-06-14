import argparse
import os
import speech_recognition as sr
from enum import Enum
from dotenv import load_dotenv

from modules.companion import Companion

class ProcessInputStatus(Enum):
    SAY = 0
    LOG = 1
    EXIT = 2
def load_keys_from_env():
    load_dotenv()
    return os.environ.get('OPENAI_API_KEY'), os.environ.get('ELEVENLABS_API_KEY')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Have GPT talk to you')
    parser.add_argument('--openai_api_key', help='Your OpenAI API key.')
    parser.add_argument('--elevenlabs_api_key', help='Your elevenlabs.io API key.')
    parser.add_argument('--debug', action='store_true', help='enable logging', default=False)
    parser.add_argument('--name', help='Name of the chatbot (default is OpenAI)')
    parser.add_argument('--context', help='Context to start the conversation with (default is "The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly.")')
    parser.add_argument('--openai_model', help='OpenAI model to use (default is gpt-3.5-turbo)')
    parser.add_argument('--openai_temperature', help='OpenAI temperature to use (default is 1.2)')
    parser.add_argument('--openai_max_reply_tokens', help='OpenAI max tokens to reply with (default is 200)', type=int)
    parser.add_argument('--voice_id', help='Voice ID for custom ElevenLabs model (default is c, Bella Premade Voice)')
    parser.add_argument('--voice_recognition', help='Enable voice input')
    parser.add_argument('--openai_retry_attempts', help='Number of times to retry OpenAI API calls (default is 3)')
    parser.add_argument('--gui', action='store_true', help='Enable the GUI', default=False)
    args = parser.parse_args()

    openai_api_key, elevenlabs_api_key = args.openai_api_key, args.elevenlabs_api_key
    env_dict = vars(args)

    if not openai_api_key or not elevenlabs_api_key:
        openai_api_key, elevenlabs_api_key = load_keys_from_env()
        if not openai_api_key or not elevenlabs_api_key:
            parser.print_help()
            exit(1)
        env_dict['openai_api_key'] = openai_api_key
        env_dict['elevenlabs_api_key'] = elevenlabs_api_key
    if __name__ == '__main__':
        args_dict = vars(args)  # Convert the Namespace object to a dictionary
        companion = Companion(args_dict)

        while True:
            with Companion(env_dict, debug=args.debug) as Companion:
                if args.voice_recognition:
                    recognizer = sr.Recognizer()
                    microphone = sr.Microphone()

                    print("Listening for voice input...")

                    while True:
                        with microphone as source:
                            audio = recognizer.listen(source)

                        try:
                            user_input = recognizer.recognize_google(audio)
                            print("You:", user_input)
                        except sr.UnknownValueError:
                            print("Error: Could not understand the audio.")
                            continue
                        except sr.RequestError:
                            print("Error: Could not request results from Google Speech Recognition service.")
                            continue

                        if user_input.lower() == "exit":
                            break

                        status = Companion.process_input(user_input, is_voice=True)
                        if status.status == Companion.ProcessInputStatus.EXIT:
                            break
                        elif status.status == Companion.ProcessInputStatus.LOG:
                            print(status.response)
                        elif status.status == Companion.ProcessInputStatus.SAY:
                            Companion.say(status.response)
                        else:
                            print(status.response)
                            Companion.say(status.response)
                        
                        companion.loop_voice_input()

            restart = input("Do you want to start a new conversation? (yes/no): ")
            if restart.lower() != "yes":
                break

            elif args.gui:
                try:
                    import gradio as gr

                    Companion.add_gradio_interface(gr)

                    print("Running the GUI... Press Ctrl+C to exit.")
                    gr.Interface.fn = Companion.process_input
                    gr.Interface(  # pylint: disable=no-member
                        fn=gr.Interface.fn,
                        inputs=[gr.TextInput(label="User input")],
                        outputs=[gr.TextBlock(label="Response")],
                        title="GPT Voice Companion",
                    ).launch()
                except ImportError:
                    print("Please install the 'gradio' package to use the GUI.")
                    exit(1)
            else:
                print("Please enable either voice recognition or the GUI.")