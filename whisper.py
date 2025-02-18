from openai import OpenAI
import ffmpeg
import os

def split_audio(input_file, chunk_duration=1000):
    # Get duration of input file
    probe = ffmpeg.probe(input_file)
    duration = float(probe['format']['duration'])
    chunks = []
    
    # Split into chunks
    for start in range(0, int(duration), chunk_duration):
        chunk_path = f"chunk_{len(chunks)}.mp3"
        end = min(start + chunk_duration, duration)
        
        stream = ffmpeg.input(input_file, ss=start, t=chunk_duration)
        stream = ffmpeg.output(stream, chunk_path, acodec='libmp3lame')
        ffmpeg.run(stream, overwrite_output=True, quiet=True)
        chunks.append(chunk_path)
    
    return chunks

client = OpenAI()
chunks = split_audio("./audio.mp3")
temp_files = []

full_transcription = []
for chunk_path in chunks:
    try:
        with open(chunk_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
            full_transcription.append(transcription)
        temp_files.append(chunk_path)
    except Exception as e:
        print(f"Error processing {chunk_path}: {e}")

# Save complete transcription
with open("transcription.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(full_transcription))

# Clean up temp files after everything is done
for temp_file in temp_files:
    try:
        os.remove(temp_file)
    except Exception as e:
        print(f"Could not remove {temp_file}: {e}")

print("Transcription saved to transcription.txt")