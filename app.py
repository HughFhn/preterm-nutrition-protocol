from flask import Flask, render_template, request
from protocol.pnProtocol import PNProtocol
from protocol.tnProtocol import TNProtocol
from io import StringIO
import sys

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def calculate_protocol():
    output = None
    if request.method == 'POST':
        # Get data from form
        en_vol = int(request.form.get('en_vol'))
        dol = int(request.form.get('dol'))
        weight = float(request.form.get('weight'))

        # redirect stdout to capture print
        old_stdout = sys.stdout
        std_output = StringIO()
        sys.stdout = std_output

        try:
            if en_vol >= 40 and dol >= 2:
                protocol = TNProtocol()
            elif 0 < en_vol < 40:
                protocol = PNProtocol()
            else:
                print("Unable to determine protocol")
                protocol = None

            if protocol:
                protocol.en_volume = en_vol
                protocol.dol = dol
                protocol.weight = weight
                protocol.determine_phase()
                protocol.run()

            output = std_output.getvalue()
        finally:
            sys.stdout = old_stdout

    return render_template('index.html', output=output)

if __name__ == '__main__':
    app.run(debug=True)
