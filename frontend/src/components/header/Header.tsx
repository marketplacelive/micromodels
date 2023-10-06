import { Box } from "@mui/material";

import "./header.scss";

import logoImg from "../../assets/Logo.svg";
import hamburgerImg from "../../assets/Hamburger.svg";
import BellIcon from "../../assets/Bell.svg";
import Propic from "../../assets/user-icon.png";

import { Navbar } from "../navbar/Navbar";

function Header() {
	return (
		<>
			<Box className="d-flex header-wrapper">
				<Box className="logo-wrapper">
					<img className="hamburger-icon" src={hamburgerImg}></img>
					<img src={logoImg}></img>
				</Box>
				<Box className="d-flex">
					<Navbar />
					<Box className="d-flex align-c">
						<Box className="bell-wrapper">
							<img className="bellicon" src={BellIcon}></img>
						</Box>
						<Box className="propic-wrapper"><img className="propic" src={Propic}></img></Box>
					</Box>
				</Box>
			</Box>
		</>
	);
}

export default Header;
