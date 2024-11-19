from flask import Flask, render_template, jsonify
from sensor_program_asli import capture_data

app = Flask(__name__)

@app.route('/')
def index():
    # Tidak perlu mengirim sensor_data di route ini
    return render_template('asli.html')

@app.route('/sensor_data')
def sensor_data():
    data = capture_data()  # Memanggil fungsi untuk mendapatkan data sensor
    return jsonify(data)    # Mengembalikan data dalam format JSON
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
