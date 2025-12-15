from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/message')
def get_message():
    return jsonify({"message": "Hello, World!"})

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    en_volume = data.get('en_volume')
    dol = data.get('dol')
    weight = data.get('weight')

    cspn_type = None
    target_a = None
    min_a = None
    max_a = None
    target_l = None
    target_total = None

    match (en_volume, dol):
        case (ev, d) if ev < 40 and d == 1:
            cspn_type = "cSPN1"
            target_a = 65
            min_a = 65
            max_a = 65
            target_l = 6
            target_total = 71

        case (ev, d) if ev < 40 and d == 2:
            cspn_type = "cSPN1"
            target_a = 80
            min_a = 65
            max_a = 90
            target_l = 12
            target_total = 92

        case (ev, d) if ev < 40 and d == 3:
            cspn_type = "cSPN2"
            target_a = 95
            min_a = 75
            max_a = 120
            target_l = 18
            target_total = 113

        case (ev, d) if ev < 40 and d >= 4:
            cspn_type = "cSPN2"
            target_a = 105
            min_a = 75
            max_a = 120
            target_l = 18
            target_total = 123

        case (ev, d) if 40 <= ev < 50 and d == 2:
            cspn_type = "cSPN1"
            target_a = 60
            min_a = 45
            max_a = 70
            target_l = 12
            target_total = 112

        case (ev, d) if 40 <= ev < 50 and d >= 3:
            cspn_type = "cSPN2"
            target_a = 95
            min_a = 55
            max_a = 100
            target_l = 18
            target_total = 153

        case (ev, d) if 50 <= ev < 60 and d == 2:
            cspn_type = "cSPN1"
            target_a = 55
            min_a = 40
            max_a = 70
            target_l = 12
            target_total = 117

        case (ev, d) if 50 <= ev < 60 and d >= 3:
            cspn_type = "cSPN2"
            target_a = 85
            min_a = 50
            max_a = 95
            target_l = 18
            target_total = 153

        case (ev, d) if 60 <= ev < 70 and d == 2:
            cspn_type = "cSPN1"
            target_a = 50
            min_a = 40
            max_a = 65
            target_l = 12
            target_total = 122

        case (ev, d) if 60 <= ev < 70 and d >= 3:
            cspn_type = "cSPN2"
            target_a = 80
            min_a = 45
            max_a = 90
            target_l = 12
            target_total = 152

        case (ev, d) if 70 <= ev < 80:
            cspn_type = "cSPN2"
            target_a = 70
            min_a = 40
            max_a = 85
            target_l = 12
            target_total = 152

        case (ev, d) if 80 <= ev < 90:
            cspn_type = "cSPN2"
            target_a = 60
            min_a = 40
            max_a = 75
            target_l = 12
            target_total = 152

        case (ev, d) if 90 <= ev < 100:
            cspn_type = "cSPN2"
            target_a = 50
            min_a = 30
            max_a = 65
            target_l = 12
            target_total = 152

        case (ev, d) if 100 <= ev < 110:
            cspn_type = "cSPN2"
            target_a = 40
            min_a = 20
            max_a = 55
            target_l = 12
            target_total = 152

        case (ev, d) if 110 <= ev < 120:
            cspn_type = "cSPN2"
            target_a = 30
            min_a = 10
            max_a = 45
            target_l = 12
            target_total = 152

        case (ev, d) if ev >= 120:
            return jsonify({
                "message": "Stop SPN unless clinically indicated"
            }), 200

    
    return jsonify({
        "cspn_type": cspn_type,
        "target_a": target_a,
        "targeta_with_weight": target_a * weight,
        "min_a": min_a,
        "max_a": max_a,
        "target_l": target_l,
        "targetl_with_weight": target_l * weight,
        "target_total": target_total,
        "targettotal_with_weight": target_total * weight
    })



if __name__ == '__main__':
    app.run(debug=True)