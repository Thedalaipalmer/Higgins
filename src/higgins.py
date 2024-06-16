import time
import speech_recognition as sr
import os
import openai
import pyttsx3
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Function to send email
def send_email(subject, body, to_email):
    from_email = os.getenv('EMAIL_ADDRESS')
    from_password = os.getenv('EMAIL_PASSWORD')
    to_email = os.getenv('RECIPIENT_EMAIL')
    
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Connect to the Gmail server
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_email, from_password)
    
    # Send the email
    server.sendmail(from_email, to_email, msg.as_string())
    server.quit()

# Function to transcribe audio, send to ChatGPT, and read aloud
def listen_and_respond(after_prompt=True):
    """
    Transcribes audio, sends to ChatGPT, and responds in speech
    
    Args:
    after_prompt: bool, whether the response comes directly
    after the user says "Hey, Higgins!" or not
    
    """
    # Default is don't start listening, until I tell you to
    start_listening = False

    with microphone as source:
        if after_prompt:
            recognizer.adjust_for_ambient_noise(source)
            print("Say 'Hey, Higgins!' to start")
            audio = recognizer.listen(source, phrase_time_limit=5)
            try:
                transcription = recognizer.recognize_google(audio)
                if transcription.lower() == "hey higgins":
                    start_listening = True
                else:
                    start_listening = False
            except sr.UnknownValueError:
                start_listening = False
        else:
            start_listening = True
        
        if start_listening:
            try:
                print("Listening for question...")
                audio = recognizer.record(source, duration=5)
                transcription = recognizer.recognize_google(audio)
                print(f"Input text: {transcription}")
                
                # Send the transcribed text to the ChatGPT3 API
                response = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=transcription,
                    temperature=0.9,
                    max_tokens=512,
                    top_p=1,
                    presence_penalty=0.6
                )

                # Get the response text from the ChatGPT3 API
                response_text = response.choices[0].text.strip()

                # Print the response from the ChatGPT3 API
                print(f"Response text: {response_text}")

                # Send the response via email
                send_email("ChatGPT Response", response_text, "recipient@example.com")

                # Say the response
                engine.say(response_text)
                engine.runAndWait()
            
            except sr.UnknownValueError:
                print("Unable to transcribe audio")

# pyttsx3 engine parameters
engine = pyttsx3.init()
engine.setProperty('rate', 150) 
engine.setProperty('voice', 'english_north')

# My OpenAI API Key
openai.api_key = os.getenv("API_KEY")

recognizer = sr.Recognizer()
microphone = sr.Microphone()

# First question
first_question = True

# Initialize last_question_time to current time
last_question_time = time.time()

# Set threshold for time elapsed before requiring "Hey, Higgins!" again
threshold = 60 # 1 minute

while True:
    if (first_question == True) | (time.time() - last_question_time > threshold):
        listen_and_respond(after_prompt=True)
        first_question = False
    else:
        listen_and_respond(after_prompt=False)

# Can run in terminal with following command to suppress warnings:
# python higgins.py 2>/dev/null
