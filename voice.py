    import speech_recognition as sr
    from gtts import gTTS
    import os
    import playsound
    import pandas as pd

    # Load recommendations from CSV files
    food_df = pd.read_csv('food_recommendations.csv')
    exercise_df = pd.read_csv('exercise_recommendations.csv')

    # Function to speak a given text
    def speak(text):
        tts = gTTS(text=text, lang='en')
        tts_file = 'voice_bot.mp3'
        tts.save(tts_file)
        playsound.playsound(tts_file)
        os.remove(tts_file)  # Remove the file after playing

    # Function to listen to voice input
    def listen():
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            audio = recognizer.listen(source)

            try:
                command = recognizer.recognize_google(audio)
                print(f"You said: {command}")
                return command.lower()
            except sr.UnknownValueError:
                print("Sorry, I did not understand that.")
                return ""
            except sr.RequestError:
                print("Could not request results from Google Speech Recognition service.")
                return ""

    # Function to recommend food and exercises based on the disease
    def recommend(disease):
        food_recommendation = food_df.loc[food_df['Disease'].str.lower() == disease]
        exercise_recommendation = exercise_df.loc[exercise_df['Disease'].str.lower() == disease]

        if not food_recommendation.empty:
            recommended_foods = food_recommendation['Recommended Foods'].values[0]
            not_recommended_foods = food_recommendation['Not Recommended Foods'].values[0]
            speak(f"For {disease}, I recommend the following foods: {recommended_foods}. Avoid: {not_recommended_foods}.")
        else:
            speak("I don't have food recommendations for that disease.")

        if not exercise_recommendation.empty:
            recommended_exercises = exercise_recommendation['Recommended Exercises'].values[0]
            speak(f"For {disease}, I recommend these exercises: {recommended_exercises}.")
        else:
            speak("I don't have exercise recommendations for that disease.")

    # Main function to run the voice bot
    def main():
        speak("Hello, I am your health bot. Please tell me your disease or allergy.")
        while True:
            command = listen()

            if "exit" in command or "quit" in command:
                speak("Goodbye!")
                break
            elif "diabetes" in command:
                recommend("diabetes")
            elif "hypertension" in command:
                recommend("hypertension")
            elif "gluten" in command:
                recommend("gluten intolerance")
            else:
                speak("I'm sorry, I can't provide recommendations for that. Please tell me another disease or allergy.")

    if __name__ == "__main__":
        main()
