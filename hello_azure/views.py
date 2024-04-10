from django.http import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
import azure.cognitiveservices.speech as speechsdk
from openai import AzureOpenAI
from django.views.decorators.csrf import csrf_exempt 
from django.views.decorators.http import require_http_methods
# import sounddevice as sd
# import soundfile as sf
# import wave
# import pyaudio

stop_speech_synthesis = False
speech_config = speechsdk.SpeechConfig(subscription="d1cca89c7c0b4bb3ad3826708743a035", region="eastus")
file_name = "outputaudio.wav"
audio_output_config = speechsdk.audio.AudioOutputConfig(filename=file_name)
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_output_config)
stop_playback = False

def one(request):
    print("start")
    return render(request,'index.html')

@csrf_exempt
def ask_openai(request):
    global stop_playback
    stop_playback = False
    print("saghd",request.POST['send'])
    if request.method=='POST':
        client = AzureOpenAI(
                azure_endpoint="https://casggpt-4.openai.azure.com/",
                api_key="62f99aff986e40a1918058887856b41d",
                api_version="2023-05-15"
                )
        deployment_id="gpt-35-turbo-16k"
        tts_sentence_end = [ ".", "!", "?", ";", "。", "！", "？", "；", "\n" ]
 
      
        # Ask Azure OpenAI in streaming way
        response = client.chat.completions.create(model=deployment_id, max_tokens=200, stream=True, messages=[
            {"role": "user", "content": request.POST['send']}
        ])
        collected_messages = []
        last_tts_request = None

        # iterate through the stream response stream
        try:
            for chunk in response:                
                if len(chunk.choices) > 0:
                    chunk_message = chunk.choices[0].delta.content  # extract the message
                    if chunk_message is not None:
                        collected_messages.append(chunk_message)  # save the message
                        if chunk_message in tts_sentence_end: # sentence end found
                            text = ''.join(collected_messages).strip() # join the recieved message together to build a sentence
                            if text != '' and stop_speech_synthesis!=True: # if sentence only have \n or space, we could skip
                                print(f"Speech synthesized to speaker for: {text}")
                                last_tts_request = speech_synthesizer.speak_text_async(text)                               
                                collected_messages.clear()
                                
        except Exception as e:
            print("Erroe",e)
        if last_tts_request:
            last_tts_request.get()
        # my_view(request)
        # play_wav_file(file_name)
        return JsonResponse({'message': 'Speech synthesis completed'}, status=200)

    return JsonResponse({'error': 'Invalid request method'}, status=400)


#stop speech listening
@csrf_exempt
def signal_stop_speech(request):
    print("enter stop")
    global stop_speech_synthesis
    stop_speech_synthesis = True
    if stop_speech_synthesis==True:
            speech_synthesizer.stop_speaking_async()
            stop_speech_synthesis = False
            return JsonResponse({'status': 'success'}) 
   





# def my_view(request):
#     # print("hello")
#     # return None
#     data, fs = sf.read('outputaudio.wav')
#     sd.play(data, fs)
#     sd.wait()

# def my_view(request):
    # # Your server-side logic here
    # data = {'message': 'Hello from Django!'}
    # return JsonResponse(data)







#playing stored audio file
# def play_wav_file(file_path):
#     global stop_playback
#     s=file_path
#     chunk = 1024
#     wf = wave.open(file_path, 'rb')
#     p = pyaudio.PyAudio()

#     # Open stream
#     stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
#                     channels=wf.getnchannels(),
#                     rate=wf.getframerate(),
#                     output=True)

#     # Read data
#     data = wf.readframes(chunk)

#     # Play stream
#     while data and not stop_playback:
#         stream.write(data)
#         data = wf.readframes(chunk)

#     # Stop stream
#     stream.stop_stream()
#     stream.close()

#     # Close PyAudio
#     p.terminate()
#     empty_wav_file(s)



# after new response received the file to remove any existing data
# def empty_wav_file(file_path):
#     with open(file_path, 'wb') as wf:
#         wf.truncate()



#stop read date when click stopResponse button
@csrf_exempt
@require_http_methods(["POST"])
def stop_playback_handler(data):
    return None
    # global stop_playback
    # stop_playback = True
    # return JsonResponse({'status': 'success'})


# def stop_playback_handler():
#     return None