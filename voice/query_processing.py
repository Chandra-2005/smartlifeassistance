
import requests
import wikipedia
import wolframalpha
import openai
import spacy
from transformers import pipeline
import pandas as pd
from fuzzywuzzy import process  # Add fuzzy matching library
from sklearn.model_selection import train_test_split  # ML
import pyaudio
import numpy as np
import librosa
import speech_recognition as sr
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import torch
from gtts import gTTS
import pygame
import os

emotion_detector = pipeline("text-classification", model="bhadresh-savani/distilbert-base-uncased-emotion")
# Move model to evaluation mode

# NewsAPI setup (replace with your own API key)
news_api_key = '982b688217f14fc5a5002a992eb48a90'
news_api_url = 'https://newsapi.org/v2/top-headlines'

# WolframAlpha API setup (replace with your own APP_ID)
wolfram_client = wolframalpha.Client('G6XY23-29WQ37KYRA')

# OpenAI API setup (replace with your own API key)
openai.api_key = 'asst_veqG9Z1s9fypXDpMXoCAN64B'

# Load spaCy NLP model
nlp = spacy.load("en_core_web_sm")

# Transformers model for conversational AI
chatbot = pipeline("text-generation", model="gpt2")

# Load the Nutrient dataset
nutrient_df = pd.read_csv('Nutrient.csv')

# Load the Disease-Food Recommendation dataset
disease_food_df = pd.read_csv('disease_food_recommendation.csv')

# Load the Disease-Exercise Recommendation dataset
exercise_recommendation_df = pd.read_csv('disease_exercise_recommendation.csv')
# Load the Weight Loss and Weight Gain datasets
weight_loss_df = pd.read_csv('weight_loss_food.csv')
weight_gain_df = pd.read_csv('weight_gain_food.csv')

emotion_classifier = pipeline("text-classification", model="bhadresh-savani/distilbert-base-uncased-emotion")

# New function to recommend foods for weight loss or gain
def recommend_food_for_weight(query, category, current_recommendations=[]):
    """
    Recommends food for weight loss or gain based on user preference for veg or non-veg.
    If the user is not satisfied with a previous recommendation, it will give another option.
    
    Parameters:
    - query: 'weight loss' or 'weight gain'
    - category: 'Veg' or 'Non-Veg'
    - current_recommendations: List of foods already recommended
    
    Returns:
    - A food recommendation based on the query and category
    """
    try:
        if 'loss' in query.lower():
            food_df = weight_loss_df
        elif 'gain' in query.lower():
            food_df = weight_gain_df
        else:
            return "Please specify if you want food recommendations for weight loss or gain."

        # Filter based on Veg or Non-Veg preference
        filtered_foods = food_df[food_df['Veg/Non-Veg'].str.contains(category, case=False, na=False)]

        # Exclude previously recommended foods
        if current_recommendations:
            filtered_foods = filtered_foods[~filtered_foods['Name'].isin(current_recommendations)]

        if filtered_foods.empty:
            return f"Sorry, I have no more recommendations for {category} foods for {query}."

        # Recommend a random food item
        recommended_food = filtered_foods.sample().iloc[0]
        current_recommendations.append(recommended_food['Name'])

        return f"How about trying {recommended_food['Name']}? It contains {recommended_food['Calories']} calories, " \
               f"{recommended_food['Protein (g)']}g of protein, and {recommended_food['Carbohydrate (g)']}g of carbohydrates."

    except Exception as e:
        print(f"Error recommending food for weight {query}: {e}")
        return "Sorry, I couldn't retrieve weight-related food recommendations at the moment."

# New function to check if a food is suitable for weight loss or gain
def is_food_for_weight(query, food_name):
    """
    Checks if the given food is appropriate for weight loss or weight gain.
    
    Parameters:
    - query: 'weight loss' or 'weight gain'
    - food_name: Name of the food to check
    
    Returns:
    - A message confirming if the food is suitable for weight loss/gain
    """
    try:
        # Search for the food in the appropriate dataset
        if 'loss' in query.lower():
            food_df = weight_loss_df
        elif 'gain' in query.lower():
            food_df = weight_gain_df
        else:
            return "Please specify whether you're asking about weight loss or gain."

        food_info = food_df[food_df['Name'].str.contains(food_name, case=False, na=False)]

        if food_info.empty:
            return f"Sorry, I couldn't find any information about {food_name}."

        # Confirm if it's suitable for the requested category
        if 'loss' in query.lower():
            return f"{food_name} is suitable for weight loss."
        else:
            return f"{food_name} is suitable for weight gain."

    except Exception as e:
        print(f"Error checking food for weight {query}: {e}")
        return "Sorry, I couldn't check the suitability of the food at the moment."



# Function to fetch nutrient information
def fetch_nutrient_info(food_name):
    try:
        # Search for the food in the dataset
        food_info = nutrient_df[nutrient_df['Main food description'].str.contains(food_name, case=False, na=False)]
        
        if food_info.empty:
            return f"Sorry, I couldn't find any nutritional information for {food_name}."

        # Extract and format nutritional data
        nutrient_data = food_info.iloc[0]
        nutrient_summary = f"Nutritional information for {nutrient_data['Main food description']}:\n"
        nutrient_summary += f"- Energy: {nutrient_data['Energy (kcal)']} kcal\n"
        nutrient_summary += f"- Protein: {nutrient_data['Protein (g)']} g\n"
        nutrient_summary += f"- Carbohydrate: {nutrient_data['Carbohydrate (g)']} g\n"
        nutrient_summary += f"- Sugars: {nutrient_data['Sugars, total (g)']} g\n"
        nutrient_summary += f"- Fiber: {nutrient_data['Fiber, total dietary (g)']} g\n"
        nutrient_summary += f"- Total Fat: {nutrient_data['Total Fat (g)']} g\n"
        nutrient_summary += f"- Saturated Fat: {nutrient_data['Fatty acids, total saturated (g)']} g\n"
        nutrient_summary += f"- Vitamin A: {nutrient_data['Vitamin A, RAE (mcg_RAE)']} mcg\n"
        nutrient_summary += f"- Vitamin C: {nutrient_data['Vitamin C (mg)']} mg\n"
        nutrient_summary += f"- Calcium: {nutrient_data['Calcium (mg)']} mg\n"
        nutrient_summary += f"- Iron: {nutrient_data['Iron (mg)']} mg\n"
        nutrient_summary += f"- Potassium: {nutrient_data['Potassium (mg)']} mg\n"
        
        return nutrient_summary

    except Exception as e:
        print(f"Error fetching nutrient info: {e}")
        return "Sorry, I couldn't retrieve nutritional information at the moment."

# Function to recommend food for a disease
def recommend_food_for_disease(query):
    try:
        # Combine diseases and symptoms into a single list for more flexible matching
        disease_symptom_list = disease_food_df['Disease/Symptom'].tolist() + disease_food_df['Symptoms'].tolist()

        # Clean the query by lower-casing it
        query_lower = query.lower()

        # Use fuzzy matching to find the closest match in the combined disease and symptom list
        closest_match, match_score = process.extractOne(query_lower, disease_symptom_list)

        # Set a reasonable threshold for match accuracy (e.g., 75%)
        if match_score < 75:
            return f"Sorry, I couldn't find any close food recommendations for '{query}'. Please try rephrasing your question."

        # Search for the closest matching disease in the dataset
        disease_info = disease_food_df[disease_food_df['Disease/Symptom'].str.contains(closest_match, case=False) | 
                                       disease_food_df['Symptoms'].str.contains(closest_match, case=False)]
        
        # Extract and format food recommendations
        recommended_foods = disease_info.iloc[0]['Recommended Foods']
        not_recommended_foods = disease_info.iloc[0]['Not Recommended Foods']
        
        recommendation = f"For {closest_match}, it is recommended to eat: {recommended_foods}.\n"
        recommendation += f"Avoid the following foods: {not_recommended_foods}."
        
        return recommendation

    except Exception as e:
        print(f"Error recommending food for disease: {e}")
        return "Sorry, I couldn't retrieve food recommendations at the moment."


# New function to recommend exercise for a disease
def recommend_exercise_for_disease(query):
    try:
        # Combine diseases into a list for matching
        disease_list = exercise_recommendation_df['Disease'].tolist()

        # Use fuzzy matching to find the closest match in the disease list
        closest_match, match_score = process.extractOne(query.lower(), disease_list)

        # Set a reasonable threshold for match accuracy (e.g., 75%)
        if match_score < 75:
            return f"Sorry, I couldn't find any exercise recommendations for '{query}'."

        # Search for the closest matching disease in the dataset
        exercise_info = exercise_recommendation_df[exercise_recommendation_df['Disease'].str.contains(closest_match, case=False)]

        # Extract and format exercise recommendations
        recommended_exercise = exercise_info.iloc[0]['Recommended Exercise']
        avoid_exercise = exercise_info.iloc[0]['Avoid']

        recommendation = f"For {closest_match}, it is recommended to do: {recommended_exercise}.\n"
        recommendation += f"Avoid: {avoid_exercise}."

        return recommendation

    except Exception as e:
        print(f"Error recommending exercise for disease: {e}")
        return "Sorry, I couldn't retrieve exercise recommendations at the moment."

# Function to fetch news
def fetch_news(country=None, category=None):
    try:
        params = {
            'apiKey': news_api_key,
            'language': 'en',
            'pageSize': 5
        }

        if country:
            params['country'] = country
        if category:
            params['category'] = category

        response = requests.get(news_api_url, params=params)
        data = response.json()
        articles = data.get('articles', [])
        
        if articles:
            news_summary = "Here are the latest news headlines:\n\n"
            for article in articles:
                news_summary += f"- {article['title']} ({article['source']['name']})\n"
            return news_summary
        else:
            return "No news articles found."
    except Exception as e:
        print(f"Error fetching news: {e}")
        return "Sorry, I couldn't fetch the news at the moment."
import pygame
import os

def text_to_speech(text):
    try:
        # Initialize gTTS and save the audio file
        tts = gTTS(text=text, lang='en')
        audio_file = "response.mp3"
        tts.save(audio_file)

        # Initialize pygame mixer and play the audio file
        pygame.mixer.init()
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()

        # Wait for the sound to finish playing
        while pygame.mixer.music.get_busy():
            continue

        # Remove the audio file
        os.remove(audio_file)

    except Exception as e:
        print(f"Error in text_to_speech: {e}")

def process_query(query):
    query_lower = query.lower()  # For case-insensitive matching
     # Check if the query is about exercises for a disease
    if "exercise" in query_lower or "workout" in query_lower:
        exercise_response = recommend_exercise_for_disease(query_lower)
        text_to_speech(exercise_response)
        return

    # Check if the query contains a disease or symptom keyword
    if any(disease in query_lower for disease in disease_food_df['Disease/Symptom'].str.lower()):
        food_response = recommend_food_for_disease(query_lower)
        text_to_speech(food_response)
        return

    # Other query handling
    if "how are you" in query_lower:
        response = "I'm doing well, thank you! How can I assist you today?"
        text_to_speech(response)
        return

    if "world news" in query_lower:
        news_response = fetch_news()
        text_to_speech(news_response)
        return

    if "nutritional information" in query_lower:
        # Extract food name from the query
        doc = nlp(query)
        food_name = None
        for ent in doc.ents:
            if ent.label_ == "FOOD":
                food_name = ent.text
                break

        if food_name:
            nutrient_response = fetch_nutrient_info(food_name)
            text_to_speech(nutrient_response)
        else:
            response = "Please provide a specific food item for nutritional information."
            text_to_speech(response)
        return

    # Query WolframAlpha for factual information
    try:
        res = wolfram_client.query(query)
        answer = next(res.results).text
        text_to_speech(answer)
        return
    except Exception as e:
        print(f"WolframAlpha query error: {e}")

    # Query Wikipedia for general knowledge
    try:
        summary = wikipedia.summary(query, sentences=2)
        text_to_speech(summary)
        return
    except wikipedia.exceptions.DisambiguationError:
        text_to_speech("There are multiple results for this query. Can you be more specific?")
        return
    except wikipedia.exceptions.PageError:
        pass

    # Fallback to OpenAI for AI-based responses
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": query}]
        )
        ai_response = response['choices'][0]['message']['content']
        text_to_speech(ai_response)
        return
    except Exception as e:
        print(f"OpenAI query error: {e}")
        text_to_speech("Sorry, I couldn't generate a response from the AI at the moment.")
