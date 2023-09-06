
from flask import Flask, request, jsonify, render_template
from models import ManualModel
from controllers import ManualController
from pdf_processor import process_pdfs

app = Flask(__name__)

# Process the PDFs and store them in Redis when the application starts
process_pdfs()

model = ManualModel()
controller = ManualController(model)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/sendMessage', methods=['POST'])
def send_message():
    try:
        message = request.json.get('message')
        response, manual_key = controller.handle_query(message)
        
        # Print the data being returned
        print(f"Response: {response}, Manual Key: {manual_key}")
        
        return jsonify({"response": response, "manualKey": manual_key})

    except Exception as e:
        print(f"Error in send_message: {str(e)}")
        return jsonify({"response": f"Error: {str(e)}", "manualKey": None})


if __name__ == '__main__':
    app.run(debug=True)

#if __name__ == '__main__':
#    app.run(host='0.0.0.0', port=5000)

