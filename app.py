from flask import Flask, request, jsonify
from flask_cors import CORS
from backend.pn_protocol import PNProtocol
from backend.tn_protocol import TNProtocol
from backend.enumClass import AqueousSPN

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        # Ensure we're getting JSON
        if not request.is_json:
            return jsonify({'message': 'Content-Type must be application/json'}), 415
        
        data = request.get_json()
        en_volume = data.get('en_volume')
        dol = data.get('dol')
        weight = data.get('weight')

        # Validate inputs
        if en_volume is None or dol is None or weight is None:
            return jsonify({'message': 'Missing required parameters'}), 400

        if dol < 0:
            return jsonify({'message': 'Invalid day of life'}), 400

        if en_volume < 0:
            return jsonify({'message': 'EN volume cannot be less than zero'}), 400

        if en_volume >= 120:
            return jsonify({'message': 'Stop SPN unless clinically indicated'}), 200

        # Determine which protocol to use based on EN volume
        if en_volume < 40:
            # PN Phase: EN < 40 mL/kg/d
            protocol = PNProtocol()
            protocol.pnPhase = True
        elif en_volume >= 40:
            # TN Phase: EN >= 40 mL/kg/d
            protocol = TNProtocol()
            protocol.tnPhase = True
        else:
            return jsonify({'message': 'Invalid EN volume'}), 400

        # Set protocol values
        protocol.en_volume = en_volume
        protocol.dol = dol
        protocol.weight = weight

        # Determine cSPN type based on DOL
        # Protocol: cSPN1 for DOL 1-2, cSPN2 for DOL 3+
        if dol <= 2:
            protocol.selected_cSPN = AqueousSPN.CSPN1
        else:
            protocol.selected_cSPN = AqueousSPN.CSPN2

        # Get row and calculate values
        row = protocol.get_row()
        aq_target, aq_min, aq_max, lip_target, total_target = protocol.calculate_protocol_spn(row)
        aq_target_ml, aq_min_ml, aq_max_ml, lip_target_ml, total_target_ml = protocol.calculate_patient_spn(row)

        # Return results matching frontend expectations
        return jsonify({
            'cspn_type': protocol.selected_cSPN.value,
            'target_aq': float(aq_target),
            'min_aq': float(aq_min),
            'max_aq': float(aq_max),
            'target_lip': float(lip_target),
            'target_total': float(total_target),
            'target_aq_weight': round(float(aq_target_ml), 2),
            'target_lip_weight': round(float(lip_target_ml), 2),
            'target_total_weight': round(float(total_target_ml), 2)
        }), 200

    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        print(f"Error: {e}")  # Debug print
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)