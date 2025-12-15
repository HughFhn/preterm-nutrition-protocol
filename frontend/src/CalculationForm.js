import { useState } from 'react';
import axios from 'axios';
import './CalculationForm.css';

const CalculationForm = ({ initialValues, onClose }) => {
  const [form, setForm] = useState({
    en_volume: initialValues?.en_volume || "",
    dol: initialValues?.dol || "",
  });

  const [result, setResult] = useState(null);

  const handleFormChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const res = await axios.post(
        'http://127.0.0.1:5000/calculate-again',
        {
          en_volume: Number(form.en_volume),
          dol: Number(form.dol),
        }
      );

      setResult(res.data);
    } catch (err) {
      setResult({ message: "Calculation failed" });
    }
  };

  return (
    <div className="calculation-form">
      <form onSubmit={handleSubmit}>
        <div className="input-group">
          <label>EN Volume:</label>
          <input
            name="en_volume"
            type="number"
            value={form.en_volume}
            onChange={handleFormChange}
            placeholder="EN Volume (mL/kg/d)"
          />
        </div>

        <div className="input-group">
          <label>Day of Life:</label>
          <input
            name="dol"
            type="number"
            value={form.dol}
            onChange={handleFormChange}
            placeholder="Day of Life"
          />
        </div>

        <button type="submit">Calculate</button>
      </form>

      {result && (
        <div className="result">
          {"message" in result ? (
            <h3>{result.message}</h3>
          ) : (
            <>
              <p>
                <strong>Aqueous Volume Required:</strong>{" "}
                {result.target_a} mL/kg/d
              </p>

              <p>
                <strong>Lipid Volume:</strong>{" "}
                {result.target_l} mL/kg/d
              </p>


              {result.warning && (
                <p className="warning"> {result.warning}</p>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default CalculationForm;
