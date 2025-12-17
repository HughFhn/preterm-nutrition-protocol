import "./App.css";
import { useState } from "react";
import axios from "axios";
import PopUp from "./PopUp";

// Use relative path since backend and frontend are on same domain
const API_URL =
	process.env.NODE_ENV === "production" ? "/api" : "http://127.0.0.1:5000";

export default function App() {
	const [form, setForm] = useState({
		en_volume: "",
		dol: "",
		weight: "",
		tfi: 120,
	});
	const [result, setResult] = useState(null);
	const [popUpOpen, setPopUpOpen] = useState(false);
	const [loading, setLoading] = useState(false);

	const handleFormChange = (e) => {
		setForm({ ...form, [e.target.name]: e.target.value });
	};

	const handleSubmit = async (e) => {
		e.preventDefault();
		setLoading(true);
		try {
			const res = await axios.post(
				`${API_URL}/calculate`,
				{
					en_volume: Number(form.en_volume),
					dol: Number(form.dol),
					weight: parseFloat(form.weight),
				},
				{
					headers: {
						"Content-Type": "application/json",
					},
				}
			);
			setResult(res.data);
		} catch (error) {
			console.error("Error:", error);
			if (error.response) {
				setResult({
					message: error.response.data.message || "An error occurred",
				});
			} else {
				setResult({ message: "Unable to connect to server" });
			}
		} finally {
			setLoading(false);
		}
	};

	const handlePopUpOpen = () => {
		setPopUpOpen(true);
	};

	return (
		<div className="App">
			<div className="calculator-container">
				<div className="element-container">
					<div className="header">
						<h2>SPN Calculator</h2>
					</div>
					<div className="calculator-card">
						<form onSubmit={handleSubmit}>
							<div className="input-group">
								<label>EN Volume: </label>
								<input
									name="en_volume"
									type="number"
									value={form.en_volume}
									onChange={handleFormChange}
									placeholder="EN Volume (mL/kg/d)"
									required
								/>
							</div>
							<div className="input-group">
								<label>Day of Life: </label>
								<input
									name="dol"
									type="number"
									value={form.dol}
									onChange={handleFormChange}
									placeholder="Day of Life (Days)"
									required
								/>
							</div>
							<div className="input-group">
								<label>Weight: </label>
								<input
									name="weight"
									type="number"
									step="0.01"
									value={form.weight}
									onChange={handleFormChange}
									placeholder="Weight (kg)"
									required
								/>
							</div>
							<button
								type="submit"
								className="calculate-button"
								disabled={loading}
							>
								{loading ? "Calculating..." : "Calculate"}
							</button>
						</form>
						{result && (
							<div className="results">
								{"message" in result ? (
									<div className="result-error">
										{result.message}
									</div>
								) : (
									<>
										<div className="result-section">
											<h3>Summary</h3>
											<div className="result-row">
												<span>CSPN Type: </span>
												<strong>
													{result.cspn_type}
												</strong>
											</div>
										</div>

										<div className="result-section">
											<h4>Volumes (mL/kg/day)</h4>

											<div className="result-row">
												<span>Aqueous: </span>
												<strong>
													{result.target_aq}
													<span className="muted">
														{" "}
														({result.min_aq}–
														{result.max_aq})
													</span>
												</strong>
											</div>

											<div className="result-row">
												<span>Lipid: </span>
												<strong>
													{result.target_lip}
												</strong>
											</div>

											<div className="result-row highlight">
												<span>
													{result.pn_phase
														? "Total SPN: "
														: "Total Fluid: "}
												</span>
												<strong>
													{result.target_total}
												</strong>
											</div>
										</div>

										<div className="result-section">
											<h4>Volumes (Weight applied)</h4>

											<div className="result-row">
												<span>Aqueous: </span>
												<strong>
													{result.target_aq_weight}{" "}
													mL/d
												</strong>
											</div>

											<div className="result-row">
												<span>Lipid: </span>
												<strong>
													{result.target_lip_weight}{" "}
													mL/d
												</strong>
											</div>

											<div className="result-row highlight">
												<span>
													{result.pn_phase
														? "Total SPN: "
														: "Total Fluid: "}
												</span>
												<strong>
													{result.pn_phase
														? result.target_total_weight
														: Number(form.tfi) *
														  Number(
																form.weight
														  )}{" "}
													mL/d
												</strong>
											</div>
										</div>
									</>
								)}
							</div>
						)}
						<p className="warning-text">
							Aim to provide target SPN volumes. Min SPN volumes
							meet lower end of nutrition recommendations. Do not
							exceed max SPN volumes.
						</p>
						<button
							onClick={handlePopUpOpen}
							className="fluid-button"
						>
							Fluid allowance less than SPN?
						</button>
					</div>
				</div>
			</div>
			<PopUp
				isOpen={popUpOpen}
				onClose={() => setPopUpOpen(false)}
				message={
					<ol className="popup-list">
						<li>
							Liberalise the daily fluid allowance as clinically
							acceptable
						</li>
						<li>Provide target lipid volume</li>
						<li>
							Reduce the Aqueous volume within the total fluid
							allowance.
						</li>
						<li>
							Example: 120 (Total SPN) - 40 (EN) - 18 (lipid) = 62
							(Aqueous)
						</li>
					</ol>
				}
				option1={"Cancel"}
			/>
		</div>
	);
}
