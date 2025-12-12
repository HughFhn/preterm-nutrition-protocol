from flask import Flask, render_template, request
from protocol.pnProtocol import PNProtocol
from protocol.tnProtocol import TNProtocol
from io import StringIO
import sys

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def calculate_protocol():
    output = None
    error = None
    
    if request.method == 'POST':
        try:
            # Get data from form
            en_vol = int(request.form.get('en_vol'))
            dol = int(request.form.get('dol'))
            weight = float(request.form.get('weight'))
            
            # Redirect stdout to capture print statements
            old_stdout = sys.stdout
            std_output = StringIO()
            sys.stdout = std_output
            
            try:
                # Determine which protocol to use
                if en_vol >= 40 and dol >= 2:
                    protocol = TNProtocol()
                elif 0 <= en_vol < 40:
                    protocol = PNProtocol()
                else:
                    print("Unable to determine protocol - check EN volume")
                    protocol = None
                
                if protocol:
                    # Set values directly (don't call get_user_inputs)
                    protocol.en_volume = en_vol
                    protocol.dol = dol
                    protocol.weight = weight
                    protocol.determine_phase()
                    
                    # Only display results if in a valid phase
                    if protocol.pnPhase or protocol.tnPhase:
                        protocol.display_results()
                    else:
                        print("Invalid protocol phase determined")
                
                output = std_output.getvalue()
                
            finally:
                sys.stdout = old_stdout
                
        except ValueError as e:
            error = f"Error: {str(e)}"
        except Exception as e:
            error = f"An unexpected error occurred: {str(e)}"
    
    return render_template('index.html', output=output, error=error)

if __name__ == '__main__':
    app.run(debug=True)