# -*- coding: utf-8 -*-
!pip install SpeechRecognition pydub

from google.colab import drive
drive.mount('/content/drive')

from google.colab import files
import speech_recognition as sr
from pydub import AudioSegment
import zipfile


uploaded = files.upload()


recognizer = sr.Recognizer()

recognized_text = ""

for filename in uploaded.keys():

    if filename.lower().endswith('.zip'):
        with zipfile.ZipFile(filename, 'r') as zip_ref:
            zip_ref.extractall('.')
            for extracted_file in zip_ref.namelist():
                if extracted_file.lower().endswith(('.wav', '.mp3', '.flac', '.ogg')):
                    filename = extracted_file
                    break


    if not filename.lower().endswith('.wav'):
        audio = AudioSegment.from_file(filename)
        audio.export(filename[:-4] + '.wav', format='wav')
        filename = filename[:-4] + '.wav'

    with sr.AudioFile(filename) as source:
        audio_data = recognizer.record(source)
        try:
            recognized_text = recognizer.recognize_google(audio_data)
            print(f"Recognized text: {recognized_text}")
        except sr.UnknownValueError:
            print("Sorry, I could not understand the audio.")
        except sr.RequestError:
            print("Sorry, I could not request results from Google Speech Recognition service.")

import nltk
nltk.download('punkt')

nltk.download('stopwords')

nltk.download('averaged_perceptron_tagger')

nltk.download('wordnet')

!pip install googletrans==4.0.0-rc1

from googletrans import Translator
translator = Translator()


def translate_to_english(text):

    detected_lang = translator.detect(text).lang


    if detected_lang != 'en':
        translation = translator.translate(text, dest='en')
        translated_text = translation.text
        return translated_text
    else:
        return text

trans=translate_to_english("അവൻ സ്കൂളിലേക്ക് പോകുന്നു")
trans

from nltk.tokenize import word_tokenize

def tokenize_sentence(sentence):
    tokens = word_tokenize(sentence)
    return tokens

tokens=tokenize_sentence(trans)
tokens

from nltk.corpus import stopwords

def words_filtering(tokens):

    stop_words = set(stopwords.words('english'))


    subject_pronouns = {'he', 'she', 'it', 'they', 'we', 'i', 'you','me'}

    question_words = {'how', 'what', 'why', 'where', 'when', 'who', 'which','whom'}


    filtered_list = [word for word in tokens if word.lower() in subject_pronouns or word.lower() in question_words or word.lower() not in stop_words]

    return filtered_list

st=words_filtering(tokens)
st

from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet

stemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()

def preprocess_text(tokens):

    stemmed_tokens = [stemmer.stem(token) for token in tokens]


    def get_wordnet_pos(treebank_tag):
        if treebank_tag.startswith('J'):
            return wordnet.ADJ
        elif treebank_tag.startswith('V'):
            return wordnet.VERB
        elif treebank_tag.startswith('N'):
            return wordnet.NOUN
        elif treebank_tag.startswith('R'):
            return wordnet.ADV
        else:
            return wordnet.NOUN

    pos_tags = nltk.pos_tag(tokens)
    lemmatized_tokens = [lemmatizer.lemmatize(token, get_wordnet_pos(pos_tag)) for token, pos_tag in pos_tags]

    return lemmatized_tokens

from nltk.corpus import wordnet
from nltk import pos_tag

def reorder_to_isl_structure(tokens):
    pos_tags = pos_tag(tokens)
    subject = []
    verb = []
    obj = []
    adjectives = []
    adverbs = []
    question_words_list = []
    others = []

    subject_pronouns = {'he', 'she', 'it', 'they', 'we', 'i', 'you', 'great', 'someone','me'}

    question_words = {'how', 'what', 'why', 'where', 'when', 'who', 'which'}

    for token, pos in pos_tags:
        token_lower = token.lower()


        if token_lower in question_words:
            question_words_list.append(token)

        elif token_lower in subject_pronouns:
            subject.append(token)

        elif pos.startswith('N'):
            if not subject:
                subject.append(token)
            else:
                obj.append(token)

        elif pos.startswith('V'):
            verb.append(token)


        elif pos.startswith('J'):
            adjectives.append(token)

        elif pos.startswith('R'):
            adverbs.append(token)

        else:
            others.append(token)

    ordered_subject = adjectives + subject
    ordered_verb = adverbs + verb


    return ordered_subject + obj + ordered_verb + others + question_words_list

import os
from moviepy.editor import VideoFileClip, concatenate_videoclips, TextClip
import subprocess

def convert_mpg_to_mp4(input_file, output_file):
    """Converts MPG to MP4 using ffmpeg"""
    try:
        command = ['ffmpeg', '-i', input_file, '-vcodec', 'libx264', '-acodec', 'aac', output_file]
        subprocess.run(command, check=True)
        print(f"Converted {input_file} to {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error converting {input_file} to {output_file}: {e}")

def fetch_and_merge_videos(lemmatized_tokens, base_video_directory, fallback_directory, output_video):
    clips = []

    # Loop through each token (word or number)
    for token in lemmatized_tokens:
        # If the token is a digit or a multi-digit number
        if token.isdigit():
            for digit in token:
                video_directory = os.path.join(base_video_directory, 'Numbers')  # Numbers directory

                video_filename_mp4 = f"{digit}.mp4"
                video_filename_mpg = f"{digit}.mpg"
                video_path_mp4 = os.path.join(video_directory, video_filename_mp4)
                video_path_mpg = os.path.join(video_directory, video_filename_mpg)

                # Check if the MP4 video file exists for the number
                if os.path.isfile(video_path_mp4):
                    try:
                        clip = VideoFileClip(video_path_mp4)
                        clips.append(clip)
                    except Exception as e:
                        print(f"Error loading video for number '{digit}': {e}")

                # If MP4 doesn't exist, check for MPG and convert
                elif os.path.isfile(video_path_mpg):
                    convert_mpg_to_mp4(video_path_mpg, video_path_mp4)
                    try:
                        clip = VideoFileClip(video_path_mp4)
                        clips.append(clip)
                    except Exception as e:
                        print(f"Error loading converted video for number '{digit}': {e}")
                else:
                    print(f"Video for number '{digit}' not found.")

        else:
            # Handle words
            first_letter = token[0].upper()  # Get the first letter of the token and convert to uppercase
            video_directory = os.path.join(base_video_directory, first_letter)  # Path to the subfolder for the word's first letter

            video_filename_mp4 = f"{token}.mp4"
            video_filename_mpg = f"{token}.mpg"
            video_path_mp4 = os.path.join(video_directory, video_filename_mp4)
            video_path_mpg = os.path.join(video_directory, video_filename_mpg)

            # Check if an MP4 file exists in the base directory
            if os.path.isfile(video_path_mp4):
                try:
                    clip = VideoFileClip(video_path_mp4)
                    clips.append(clip)
                except Exception as e:
                    print(f"Error loading MP4 video for '{token}': {e}")

            # If MP4 file doesn't exist, check for MPG file and convert it
            elif os.path.isfile(video_path_mpg):
                convert_mpg_to_mp4(video_path_mpg, video_path_mp4)
                try:
                    clip = VideoFileClip(video_path_mp4)
                    clips.append(clip)
                except Exception as e:
                    print(f"Error loading converted MP4 video for '{token}': {e}")

            # If not found, check in fallback directory
            else:
                print(f"Video for '{token}' not found in base directories, checking fallback directory.")
                fallback_video_mp4 = os.path.join(fallback_directory, video_filename_mp4)
                fallback_video_mpg = os.path.join(fallback_directory, video_filename_mpg)

                if os.path.isfile(fallback_video_mp4):
                    try:
                        clip = VideoFileClip(fallback_video_mp4)
                        clips.append(clip)
                    except Exception as e:
                        print(f"Error loading MP4 video for '{token}' in fallback directory: {e}")

                elif os.path.isfile(fallback_video_mpg):
                    convert_mpg_to_mp4(fallback_video_mpg, fallback_video_mp4)
                    try:
                        clip = VideoFileClip(fallback_video_mp4)
                        clips.append(clip)
                    except Exception as e:
                        print(f"Error loading converted video for '{token}' in fallback directory: {e}")

                # If not found, break the word into letters and search for each letter in the fallback directory
                else:
                    print(f"Video for '{token}' not found in fallback directory, breaking it down into individual letters.")
                    for letter in token:
                        letter_upper = letter.upper()  # Convert to uppercase for letter lookup
                        letter_video_mp4 = os.path.join(fallback_directory, f"{letter_upper}.mp4")
                        letter_video_mpg = os.path.join(fallback_directory, f"{letter_upper}.mpg")

                        # Check for MP4 file first
                        if os.path.isfile(letter_video_mp4):
                            try:
                                letter_clip = VideoFileClip(letter_video_mp4)
                                clips.append(letter_clip)
                            except Exception as e:
                                print(f"Error loading MP4 video for letter '{letter_upper}': {e}")

                        # If MP4 doesn't exist, check for MPG file and convert it
                        elif os.path.isfile(letter_video_mpg):
                            convert_mpg_to_mp4(letter_video_mpg, letter_video_mp4)
                            try:
                                letter_clip = VideoFileClip(letter_video_mp4)
                                clips.append(letter_clip)
                            except Exception as e:
                                print(f"Error loading converted video for letter '{letter_upper}': {e}")

                        # If neither file exists, create a text-based clip for the letter
                        else:
                            print(f"Video for letter '{letter_upper}' not found, creating text-based video for letter instead.")
                            letter_text_clip = (TextClip(letter_upper, fontsize=70, color='white', bg_color='black')
                                                .set_duration(1))  # Adjust duration for individual letters
                            clips.append(letter_text_clip)

    # Check if the clips list is not empty
    if clips:
        try:
            # Concatenate all the clips into a single video
            final_clip = concatenate_videoclips(clips, method="compose")

            # Write the final video to a file
            final_clip.write_videofile(output_video, codec='libx264')
        except Exception as e:
            print(f"Error during concatenation or writing file: {e}")
    else:
        print("No video clips found, unable to create a video.")

# Example usage:
lemmatized_tokens = ["Habitat", "protection", "3"]  # Example tokens
base_video_directory = '/content/drive/MyDrive'
fallback_directory = '/content/drive/MyDrive/INDIAN SIGN LANGUAGE ANIMATED VIDEOS'
output_video = '/content/drive/MyDrive/output_video.mp4'
fetch_and_merge_videos(lemmatized_tokens, base_video_directory, fallback_directory, output_video)

#sentence = "He went to college and learned skills"
translated_s= translate_to_english(recognized_text)
tokens = tokenize_sentence(recognized_text)
filtered_words=words_filtering(tokens)
preprocessed_tokens = preprocess_text(filtered_words)
sov_order_tokens = reorder_to_isl_structure(preprocessed_tokens)
capitalized=capitalize_tokens(sov_order_tokens)
fetch_and_merge_videos(capitalized,'/content/drive/MyDrive','/content/drive/MyDrive/INDIAN SIGN LANGUAGE ANIMATED VIDEOS','final_isl_video.mp4')

from IPython.display import HTML
from base64 import b64encode

def display_video(video_path):
    with open(video_path, "rb") as video_file:
        video_base64 = b64encode(video_file.read()).decode('ascii')

    video_html = f'''
    <video width="640" height="480" controls>
        <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
    </video>
    '''
    return HTML(video_html)
output_video_path = output_video
display_video_in_colab(output_video_path)



