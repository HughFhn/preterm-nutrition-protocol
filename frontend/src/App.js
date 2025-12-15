import logo from './logo.svg';
import './App.css';
import { useState } from 'react';
import axios from 'axios';
import PopUp from './PopUp';

export default function App() {
  const [form, setForm] = useState({ en_volume: "", dol: "", weight: ""});
  const [result, setResult] = useState(null);
  const [popUpOpen, setPopUpOpen] = useState(false);

  const handleFormChange = (e) => {
    setForm({...form, [e.target.name]: e.target.value});
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const res = await axios.post('http://127.0.0.1:5000/calculate',
      {
        en_volume: Number(form.en_volume),
        dol: Number(form.dol),
        weight: parseFloat(form.weight)
      });
    setResult(res.data);
  };

  const handlePopUpOpen = () => {
    setPopUpOpen(true);
  };

  return(
    <div className='App'>
      <div className='header'>
        <h2>SPN Calculator</h2>
      </div>
      <div className="calculator-container">
        <div className="form-wrapper">
          <div className="calculator-card">
            <form onSubmit={handleSubmit}>
              <div className='input-group'>
                <label>EN Volume: </label>
                <input
                  name="en_volume"
                  type="number"
                  value={form.en_volume}
                  onChange={handleFormChange}
                  placeholder='EN Volume (mL)'
                />
              </div>
              <div className='input-group'>
                <label>Day of Life: </label>
                <input
                  name="dol"
                  type="number"
                  value={form.dol}
                  onChange={handleFormChange}
                  placeholder='Day of Life (Days)'
                />
              </div>
              <div className='input-group'>
                <label>Weight: </label>
                <input 
                  name="weight"
                  type="number"
                  value={form.weight}
                  onChange={handleFormChange}
                  placeholder='Weight (kg)'
                />
              </div>
              <button type="submit" className="calculate-button">Calculate</button>
            </form>
            {result && (
              <div>
                {"message" in result ? (
                  <h3>{result.message}</h3>
                ) : (
                  <>
                    <p><strong>CSPN Type:</strong> {result.cspn_type}</p>
                    <p><strong>Aqueous Volume: </strong> {result.target_a} mL/kg/d (min: {result.min_a}, max: {result.max_a} )</p>
                    <p><strong>Lipid Volume: </strong>{result.target_l} mL/kg/d</p>
                    <p><strong>Total SPN Volume: </strong>{result.target_total} mL/kg/d</p>
                    <p className='weight_paragraph'><strong>Aqueous Volume for patient weight: </strong>{result.targeta_with_weight} mL/kg/d</p>
                    <p className='weight_paragraph'><strong>Lipid Volume for patient weight: </strong>{result.targetl_with_weight} mL/kg/d </p>
                    <p className='weight_paragraph'><strong>Total SPN Volume for patient weight: </strong>{result.targettotal_with_weight} mL/kg/d</p>
                  </>
                )}
              </div>
            )}
            <p className="warning-text">Aim to provide target SPN volumes. Min SPN volumes meet lower end of nutrition recommendations. Do not exceed max SPN volumes.</p>
            <button onClick={handlePopUpOpen} className='fluid-button'>Fluid allowance less than SPN?</button>
          </div>
          </div>
        </div>
        <PopUp 
          isOpen={popUpOpen}
          onClose={() => setPopUpOpen(false)}
          message={
            <ol className='popup-list'>
              <li>Liberalise the daily fluid allowance as clinically acceptable</li>
              <li>Provide target lipid volume</li>
              <li>Reduce the Aqueous volume within the total fluid allowance.</li>
              <li>Example: 120 (Total SPN) - 40 (EN) - 18 (lipid) = 62 (Aqueous)</li>
            </ol>}
          option1={'Cancel'}
        />
      </div>
  )
};


