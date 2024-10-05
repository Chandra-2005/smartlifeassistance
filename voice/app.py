
from flask import Flask, render_template, request, jsonify
from query_processing import process_query
from text_to_speech import speak

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/response', methods=['POST'])
def response():
    query = request.form['query']
    result = process_query(query)
    speak(result)  # Output the response through text-to-speech
    return render_template('response.html', query=query, result=result)

@app.route('/voice_query', methods=['POST'])
def voice_query():
    from speech_recognition import recognize_speech
    query = recognize_speech()  # Capture user's voice query
    result = process_query(query)
    speak(result)  # Output the response through text-to-speech
    return jsonify({'query': query, 'result': result})

if __name__ == '__main__':
    app.run(debug=True)