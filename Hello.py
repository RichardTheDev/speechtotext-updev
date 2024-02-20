import streamlit as st
import sounddevice as sd
import soundfile as sf
from tempfile import mktemp
import os
from openai import OpenAI
import constant

client = OpenAI(api_key=st.secrets["openaikey"])


# Function to record audio
def record_audio(duration=5, fs=44100):
    """Record audio from the microphone."""
    st.write("Recording...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=2, dtype='float64')
    sd.wait()  # Wait until recording is finished
    return recording, fs


# Function to save the recording into a WAV file
def save_recording(recording, fs, filename="temp_audio.wav"):
    """Save the recording into a WAV file."""
    sf.write(filename, recording, fs)
    return filename


def generate_corrected_transcript( text_transcribed):
    system_prompt = "You are a helpful assistant for the company ZyntriQix. Your task is to correct any spelling discrepancies in the transcribed text. Make sure that the names of the following products are spelled correctly: ZyntriQix, Digique Plus, CynapseFive, VortiQore V8, EchoNix Array, OrbitalLink Seven, DigiFractal Matrix, PULSE, RAPT, B.R.I.C.K., Q.U.A.R.T.Z., F.L.I.N.T. Only add necessary punctuation such as periods, commas, and capitalization, and use only the context provided."
    response = client.chat.completions.create(
        model="gpt-4",
        temperature=1,
        messages=[
            {
                "role": "system",
                "content": constant.SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": text_transcribed
            }
        ]
    )
    return(response.choices[0].message.content)
    # return completion.choices[0].message.content

def transcribe(audio_file_path, prompt=""):
    """
    Transcribes the given audio file to text using OpenAI's Whisper model.

    :param audio_file_path: The path to the audio file to be transcribed.
    :param prompt: An optional prompt to improve transcription accuracy.
    :return: The transcribed text.
    """

    with open(audio_file_path, "rb") as audio_file:
        transcript_response = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text"  # Ensure response is in text format for direct access
        )
    print(transcript_response)
    # Directly accessing the 'text' field from the response
    # transcribed_text = transcript_response["text"] if "text" in transcript_response else "Transcription failed."

    result =generate_corrected_transcript(transcript_response)
    return [transcript_response,result]


# App title
st.title("MUXLAB Demo - Audio Recorder and Transcriber")

st.info("This is a demo for MUXLAB project ,try something like :'Put some music in the airport lounge'")
# Record audio
if st.button('Record Audio'):
    duration = st.number_input("Enter the duration to record in seconds:", min_value=1, value=5)
    recording, fs = record_audio(duration=duration)
    filename = save_recording(recording, fs, mktemp(prefix="audio_", suffix=".wav"))
    st.session_state['recorded_audio'] = filename  # Save filename to session state
    st.audio(filename, format='audio/wav', start_time=0)

# Transcribe audio
if st.button('Transcribe Audio'):
    if 'recorded_audio' in st.session_state and st.session_state['recorded_audio']:
        transcription = transcribe(st.session_state['recorded_audio'])
        st.text_area("Transcription", transcription[0], height=150)
        st.json(transcription[1])
        os.remove(st.session_state['recorded_audio'])  # Clean up the temporary file
        del st.session_state['recorded_audio']  # Clear the recorded audio from session state
    else:
        st.warning("Please record an audio first.")

