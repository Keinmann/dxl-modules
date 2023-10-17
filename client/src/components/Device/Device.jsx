import "./Device.scss";
import { ReactPropTypes, useEffect, useState } from "react";

function Device({ device }) {
	const [registers, setRegisters] = useState({ registe: "value" });

	return (
		<div className="device">
			<div className="device__header">
				<h4>
					{device.title}({device.id})
				</h4>
			</div>
			<div className="device__body">
				{device.registers?.map((register, index) => (
					<div className="device__body_register" key={index}>
						<div className="device__body_register_title">{register.name}</div>
						<div className="device__body_register_value">
							{register.value}
							{register.si}
						</div>
					</div>
				))}
			</div>
			<div className="device__footer"></div>
		</div>
	);
}

Device.propTypes = ReactPropTypes;

export default Device;
