from crewai.tools import BaseTool
import pyaudio
import wave
import speech_recognition as sr

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 15
WAVE_OUTPUT_FILENAME = "output.wav"

class SpeechTranscriptionTool(BaseTool):
    name: str = "Speech Transcription Tool"
    description: str = (
        "Captura voz ({RECORD_SECONDS} segundos) y transcribe las palabras."
        "Devuelve el texto de lo hablado."
    )

    def _run(self) -> str:
        """
            Devuelve → texto de la transcripción de voz
        """
        def record_audio(filename=WAVE_OUTPUT_FILENAME, duration=RECORD_SECONDS):
            p = pyaudio.PyAudio()
            stream = p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate= RATE,
                input=True,
                frames_per_buffer=CHUNK
            )            
            ans =input(f"Listo para hablar (máximo {RECORD_SECONDS} seg)?? ")
            print("* Grabando tu pedido...... ")

            frames = []
            for i in range(0, int(RATE / CHUNK * duration)):
                data = stream.read(CHUNK)
                frames.append(data)

            print("* Finalizó grabación ......")

            stream.stop_stream()
            stream.close()
            p.terminate()

            wf= wave.open(filename,'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            return filename

        def transcribe_audio(audio_file):
            r = sr.Recognizer()
            with sr.AudioFile(audio_file) as source:
                audio = r.record(source)

            try:
                text = r.recognize_google(audio, language = "es-ES")
                print("Transcripción: " + text)
                return text
            except sr.UnknownValueError:
                print("No se pudo entender el audio")
                return None
            except sr.RequestError as e:
                print(f"No hay resultados del servicio de reconocimiento: {e}")
                return None

        recorded_file = record_audio()
        if recorded_file:
            transcription = transcribe_audio(recorded_file)
            if transcription:
                print(f"Transcripción final: {transcription}")
                return transcription

# import whisper
# def transcribe_with_whisper(audio_file):
#     model = whisper.load_model("base") 
#     result = model.transcribe(audio_file)
#     print("Transcripción con Whisper: "+ result["text"])
#     return result["text"]

# if __name__=="__main__":
#     recorded_file = record_audio()
#     if recorded_file:
#         transcription = transcribe_audio(recorded_file)
#         if transcription:
#             print(f"Transcripción final: {transcription}")


# Instancia lista para usar en los agentes
speech_transcription_tool = SpeechTranscriptionTool()