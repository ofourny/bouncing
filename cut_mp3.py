
from pydub import AudioSegment

# Load your MP3 file
audio = AudioSegment.from_mp3("mid/ball16.mp3")

# Length of the audiofile in milliseconds
length_audio = len(audio)

# Start and end in milliseconds
start = 0
end = 500

# Splitting the audio file into 1-second parts
while start < length_audio:
    # Define the audio segment from start to end
    split = audio[start:end]

    file =  'output_{:04d}.mp3'.format(start // 500)

    # Export the split audio
    split.export(file, format="mp3")

    # Update start and end for the next segment
    start += 500
    end += 500