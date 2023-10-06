import { NavLink } from "react-router-dom";

export const Navbar = () => {
	return (
		<nav className="navbar">
			<NavLink className="nav-icon" to='/'>Home</NavLink>
			<NavLink className="nav-icon" to='/action-list'>Action List</NavLink>
			<NavLink className="nav-icon" to='/playbook'>Playbook</NavLink>
			<NavLink className="nav-icon" to='/accelerate'>Accelerate</NavLink>
			<NavLink className="nav-icon" to='/sentiment'>Sentiment</NavLink>
			<NavLink className="nav-icon" to='/learning'>Learning</NavLink>
			<NavLink className="nav-icon" to='/progress-deal'>Progress Deal</NavLink>
		</nav>
	);
};
