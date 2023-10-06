import React from "react";
import { Box, Typography } from "@mui/material";
import { Link, NavLink, Outlet, useLocation } from "react-router-dom";

import "./PaymentSummary.scss";
import Propic from "../../assets/user-icon.png";
import RoleIcon from "../../assets/user-role.svg";
import CompanyIcon from "../../assets/company.svg";
import user1 from "../../assets/user-icon-1.jpg";
import user2 from "../../assets/user-icon-2.jpg";
import user3 from "../../assets/user-icon-3.jpg";

const Colors = {
	PlaceHolderGrey: "#CACDCD",
};

const PainNavbar = () => {
	const location = useLocation();
	return (
		<nav className="user-navbar d-flex align-c">
			<NavLink
				className={
					location.pathname === "/accelerate/pain-point-list" ||
						location.pathname === "/accelerate/pain-point-list/info"
						? "user-nav-icon active"
						: "user-nav-icon"
				}
				to="info"
			>
				INFO
			</NavLink>
			<NavLink className="user-nav-icon" to="timeline">
				TIMELINE
			</NavLink>
			<NavLink className="user-nav-icon" to="conversations">
				CONVERSATONS
			</NavLink>
		</nav>
	);
};

function PaymentSummary() {
	const UserName = "John Baker";
	const UserRole = "Marketing Manager";
	const Company = "Siemens";

	return (
		<Box className="ps-wrapper box-b">
			<Box className="ps-header">
				<Box className="d-flex justify-sb">
					<Box className="d-flex">
						<img className="pro-pic" src={Propic} alt="pro pic"></img>
						<Box className="d-flex" sx={{ flexDirection: "column", justifyContent: "space-evenly" }}>
							<h4 className="user-name">{UserName}</h4>
							<Box className="d-flex">
								<Box
									className="d-flex align-c"
									sx={{ paddingRight: ".75rem", borderRight: `1px solid ${Colors.PlaceHolderGrey}` }}
								>
									<img className="pro-detail-icon" src={RoleIcon} alt="pro pic"></img>
									<span className="pro-detail-text">{UserRole}</span>
								</Box>
								<Box className="d-flex align-c" sx={{ paddingLeft: ".75rem" }}>
									<img className="pro-detail-icon" src={CompanyIcon} alt="pro pic"></img>
									<span className="pro-detail-text">{Company}</span>
								</Box>
							</Box>
						</Box>
					</Box>
					<Box className="employee-wrap d-flex">
						{CompanyEmployeeList?.map((employee, index) => {
							return (
								<Box
									className="employee-tile"
									key={index}
									sx={{
										position: "relative",
										// left: `-${index * 0.5}rem`,
										backgroundImage: `url(${employee.profile})`,
										backgroundPosition: "center",
										backgroundSize: "cover",
										backgroundRepeat: "no-repeat",
										zIndex: index + 1,
									}}
								></Box>
							);
						})}
					</Box>
				</Box>
			</Box>
			<PainNavbar />
			<Outlet></Outlet>
		</Box>
	);
}

export default PaymentSummary;

const CompanyEmployeeList = [
	{ name: "Martin", profile: user1 },
	{ name: "Zakariya", profile: user2 },
	{ name: "Stieve", profile: user3 },
];
