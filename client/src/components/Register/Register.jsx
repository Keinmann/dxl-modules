import "./Register.scss";
import { ReactPropTypes, useState } from "react";

function Register({ device, register }) {
	const [value, setValue] = useState(register.value ? register.value : 0);
	const valueElement = (
		<input
			type={register.subtype === "range" ? register.subtype : "text"}
			min={register.min ? register.min : 0}
			max={register.max ? register.max : 0}
			value={value}
			onChange={(e) => {
				handleChange(e);
			}}
		/>
	);

	const handleChange = (e) => {
		setValue(e.target.value);
		writeRegister();
	};

	async function writeRegister() {
		try {
			const response = await fetch(`http://192.168.42.17:8117/`, {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify({
					device: device,
					value: value,
					register: register,
				}),
			});
			const json = await response.json();
			if (json.status === "200") {
				console.log("ok");
				register.value = value;
			}
		} catch (err) {
			console.log(err);
		}
	}

	return (
		<div className="register">
			<div className="register-info">
				<div className="register-info_title">{register.name}</div>
				<div className="register-info_value">
					{register.value}
					{register.si}
				</div>
			</div>
			{register.type === "w" && (
				<div className="register-control">{valueElement}</div>
			)}
		</div>
	);
}

Register.propTypes = ReactPropTypes;

export default Register;
