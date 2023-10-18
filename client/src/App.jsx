import React from "react";
import { useEffect, useState } from "react";
import "./App.scss";
import Device from "./components/Device/Device";

function App() {
	const [data, setData] = useState(null);
	const [error, setError] = useState("");
	async function getData() {
		try {
			const response = await fetch(`http://192.168.42.17:8117/`, {
				method: "GET",
				headers: {
					"Content-Type": "application/json",
				},
			});
			const json = await response.json();
			setData(json.devices);
			setError("");
		} catch (err) {
			setError("Connection Error Detected");
		}
	}

	useEffect(() => {
		const interval = setInterval(() => {
			getData();
		}, 500);

		return () => clearInterval(interval);
	}, []);

	return (
		<div className="app">
			<div className="app_header">
				<h1>DxlModules</h1>
				<p className="app_header-error">{error}</p>
			</div>
			<div className="app_content">
				{data?.map((device, key) => (
					<Device key={key} device={device} />
				))}
			</div>
		</div>
	);
}

export default App;
