import React from "react";

import DownArrow from "../../assets/down-arrow.svg";
import Search from "../../assets/Search.svg";
import Mic from "../../assets/mic.svg";
import Filter from "../../assets/Hamburger.svg";
import Refresh from "../../assets/Refresh.svg";

export const SubHeader = () => {
	return (
		<div className="sub-header-wrapper">
			<div className="searchbar-container">
				<div className="drop-search search-wrapper">
					<span className="drop-search-text">Under Performing Opportunities</span>
					<img src={DownArrow}></img>
				</div>
				<div className="search-wrapper">
					<img src={Search}></img>
					<span className="search-text">Search</span>
					<img src={Mic}></img>
				</div>
			</div>
			<div className="filterbar-container">
				<div className="refresh-wrapper">
					<img src={Refresh}></img>
				</div>
				<div className="refresh-wrapper filter-wrapper">
					<img src={Filter}></img>
					<span className="filter-text">Filter</span>
				</div>
			</div>
		</div>
	);
};
