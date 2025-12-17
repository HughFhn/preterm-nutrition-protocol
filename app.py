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
        tfi = data.get('tfi', 120)  # Default to 120 if not provided
        
        # Validate inputs
        if en_volume is None or dol is None or weight is None:
            return jsonify({'message': 'Missing required parameters'}), 400
        
        if dol < 1:
            return jsonify({'message': 'Day of Life must be at least 1'}), 400
        
        if en_volume < 0:
            return jsonify({'message': 'EN volume cannot be less than zero'}), 400
        
        if weight <= 0:
            return jsonify({'message': 'Weight must be greater than 0'}), 400
        
        if tfi <= 0:
            return jsonify({'message': 'Total Fluid Intake must be greater than 0'}), 400
        
        if en_volume >= 120:
            return jsonify({'message': 'Stop SPN unless clinically indicated'}), 200
        
        # CRITICAL FIX: Determine phase based on EN AND DOL
        # Per PDF protocol:
        # - PN Phase: EN < 40 (any DOL) OR (EN >= 40 AND DOL == 1)
        # - TN Phase: EN >= 40 AND DOL >= 2
        
        if en_volume < 40:
            # PN Phase: EN < 40 mL/kg/d
            protocol = PNProtocol()
            protocol.pnPhase = True
            protocol.tnPhase = False
        elif en_volume >= 40 and dol == 1:
            # Edge case: DOL 1 with high EN - stays in PN phase
            # TN phase doesn't support DOL 1
            protocol = PNProtocol()
            protocol.pnPhase = True
            protocol.tnPhase = False
        elif en_volume >= 40 and dol >= 2:
            # TN Phase: EN >= 40 AND DOL >= 2
            protocol = TNProtocol()
            protocol.tnPhase = True
            protocol.pnPhase = False
        else:
            return jsonify({'message': 'Invalid combination of EN volume and DOL'}), 400
        
        # Set protocol values
        protocol.en_volume = en_volume
        protocol.dol = dol
        protocol.weight = weight
        protocol.tfi = tfi
        
        # Determine cSPN type based on DOL (per PDF protocol)
        if dol <= 2:
            protocol.selected_cSPN = AqueousSPN.CSPN1
        else:
            protocol.selected_cSPN = AqueousSPN.CSPN2
        
        # Get row and calculate values
        try:
            row = protocol.get_row()
        except ValueError as e:
            return jsonify({'message': str(e)}), 400
        
        aq_target, aq_min, aq_max, lip_target, total_target = protocol.calculate_protocol_spn(row)
        patient = protocol.calculate_patient_spn(row)
        
        # Extract patient-specific values
        aq_target_ml = patient["aqueous_ml_day"]
        lip_target_ml = patient["lipid_ml_day"]
        total_target_ml = patient["total_spn_ml"]
        status = patient["status"]
        
        # Return results matching frontend expectations
        return jsonify({
            'tn_phase': protocol.tnPhase,
            'pn_phase': protocol.pnPhase,
            'cspn_type': protocol.selected_cSPN.value,
            'target_aq': float(aq_target),
            'min_aq': float(aq_min),
            'max_aq': float(aq_max),
            'target_lip': float(lip_target),
            'target_total': float(total_target),
            'target_aq_weight': round(float(aq_target_ml), 2),
            'target_lip_weight': round(float(lip_target_ml), 2),
            'target_total_weight': round(float(total_target_ml), 2),
            'status': status,
            'available_fluid': round(float(tfi - en_volume), 2)
        }), 200
        
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'SPN Calculator'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)