import React from "react";
import "./PaymentSummary.scss";
import { Box } from "@mui/material";

import phone from "../../assets/Phone.svg";
import email from "../../assets/email.svg";
import location from "../../assets/location.svg";

export default function Info() {
	const userIcons = [phone, email, location];
	const userDetails = {
		phone: "+91 - 987654321",
		email: "john.baker@siemens.com",
		location: "L14 -177 Pacific Hwy North Sydney, Australia",
	};

	const paymentDetails = [1, 2, 3, 4]

	return (
		<Box className="info-wrap">
			<Box className="user-details d-flex">
				{Object.keys(userDetails).map((key, index) => (
					<Box key={index} className="user-detail-tile d-flex align-c justify-c">
						<img src={userIcons[index]} alt="phone icon"></img>
						<span>{userDetails[key]}</span>
					</Box>
				))}
			</Box>
			<Box className="payment-details">
				<h3 className="payment-heading">Deal summary</h3>
				{paymentDetails.map((payment, index) => {
					return (
						<Box key={index} className="payment-tile">
							<Box className="d-flex">
								<Box className="side-indicator"></Box>
								<Box className="tx-details">
									<p>Initial Contract Payment</p>
									<span>Qualification | </span>
									<span>22 May 2023 </span>
								</Box>
							</Box>
							<span className="tx-amount">$ 35,000,000</span>
						</Box>
					)
				})}
			</Box>
		</Box>
	);
}
