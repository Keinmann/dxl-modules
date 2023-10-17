import React from "react";
import { useEffect, useState } from "react";
import "./App.scss";
import Device from "./components/Device/Device";

function App() {
	const [data, setData] = useState(null);

	async function getData() {
		try {
			const response = await fetch(`http://192.168.42.17:8117/`, {
				method: "GET",
				headers: {
					"Content-Type": "application/json",
				},
			});
			const json = await response.json();
			console.log(json);
			setData(json.devices);
		} catch (err) {
			console.log(JSON.stringify(err));
		}
	}
	useEffect(() => {
		getData();
	}, []);
	return (
		<div className="app">
			<div className="app_header">
				<h1>DxlModules</h1>
			</div>
			<div className="app_content"></div>
			{data?.map((device, key) => (
				<Device key={key} device={device} />
			))}
		</div>
	);
}

export default App;
