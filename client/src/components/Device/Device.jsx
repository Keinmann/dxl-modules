import Register from "../Register/Register";
import "./Device.scss";
import { ReactPropTypes, useEffect, useState } from "react";

function Device({ device }) {
	return (
		<div className="device">
			<div className="device__header">
				<h4>
					{device.title}({device.id})
				</h4>
			</div>
			<div className="device__body">
				{device.registers?.map((register, key) => (
					<Register key={key} device={device.id} register={register} />
				))}
			</div>
		</div>
	);
}

Device.propTypes = ReactPropTypes;

export default Device;
