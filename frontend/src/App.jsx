import { Routes, Route } from "react-router-dom";
import React, { useState, useEffect } from 'react';

import NotFound from "./pages/not-found/NotFound";
import Home from "./pages/home/Home";
import ActionList from "./pages/action-list/ActionList";
import Playbook from "./pages/playbook/Playbook";
import Accelerate from "./pages/accelerate/Accelerate";
import Sentiment from "./pages/sentiment/Sentiment";
import Learning from "./pages/learning/Learning";
import ProgressDeal from "./pages/progress-deal/ProgressDeal";

import "./App.scss";
import Header from "./components/header/Header";
import PainPointList from "./pages/pain-point-list/PainPointList";
import Info from "./components/payment-summary/Info";
import Timeline from "./components/payment-summary/Timeline";
import Conversations from "./components/payment-summary/Conversations";

function App() {
	return (
		<>
			<Header />
			<Routes>
				<Route path="*" element={<NotFound />} />
				<Route path="/" element={<Home />} />
				<Route path="/action-list" element={<ActionList />} />
				<Route path="/playbook" element={<Playbook />} />
				<Route path="/accelerate" element={<Accelerate />} />
				<Route path="/accelerate/pain-point-list" element={<PainPointList />}>
					<Route index activeClassName="acc" element={<Info />} />
					<Route path="info" activeClassName="acc" element={<Info />} />
					<Route path="timeline" element={<Timeline />} />
					<Route path="conversations" element={<Conversations />} />
				</Route>
				<Route path="/sentiment" element={<Sentiment />} />
				<Route path="/learning" element={<Learning />} />
				<Route path="/progress-deal" element={<ProgressDeal />} />
			</Routes>
		</>
	);
};

export default App;
