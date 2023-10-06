import { Box, Button, Checkbox, List, ListItem, ListItemButton, ListItemIcon, ListItemText, Typography } from "@mui/material";
import { useNavigate, useLocation } from "react-router-dom";
import React, { useEffect, useState } from "react";
import axios from "axios";
import "./PainPointList.scss";

import BackButton from "../../assets/Back.svg";
import ViewMore from "../../assets/View more.svg";
import AddButton from "../../assets/Add.svg";
import ai from "../../assets/ai.svg";

import PaymentSummary from "../../components/payment-summary/PaymentSummary";
import SuggestedActions from "../../components/suggested-actions/SuggestedActions";
import Prompt from '../../prompt-config.json'

const colors = {
	primaryBlue: "#0062A6",
	backgroundBlue4: "#E5E8EE",
};

function PainPointList() {
	const relationName = "Binta Susan";
	const leadStage = "In progress";

	const location = useLocation();
	const accountName = location?.state;
	const opportunity = `${accountName} opportunity`;

	const backNav = useNavigate();

	const [PainList, setNewList] = useState([]);
	const [Checked, setChecked] = useState([]);
	const [SolutionList, setSolutionList] = useState([]);

	useEffect(() => {
		fetchProblemPoints().then((res) => {
			let updatedPainList = [];
			res && (updatedPainList = JSON.parse(res));
			setNewList(updatedPainList);
		});
	}, []);

	useEffect(() => {
		const list = updateCheckList();
		Checked.length &&
			fetchSuggestedSolutions(list).then((res) => {
				let updatedPainList = [];
				res && (updatedPainList = JSON.parse(res));
				setSolutionList(updatedPainList);
			});
	}, [Checked]);

	const updateCheckList = () => {
		let newCheckList = [];
		Checked.map((value) => {
			newCheckList = [...newCheckList, PainList[value]];
		});
		return newCheckList;
	};

	const handleToggle = (value) => () => {
		const currentIndex = Checked.indexOf(value);
		const newChecked = [...Checked];
		if (currentIndex === -1) {
			newChecked.push(value);
		} else {
			newChecked.splice(currentIndex, 1);
		}
		setChecked(newChecked);
	};

	const GetPainList = () => {
		return (
			<List>
				{PainList?.map((value, index) => {
					const labelId = `checkbox-list-label-${value}`;
					return (
						<ListItem key={value} disablePadding>
							<ListItemButton role={undefined} onClick={handleToggle(index)}>
								<ListItemIcon>
									<Checkbox
										edge="start"
										checked={Checked.indexOf(index) !== -1}
										tabIndex={-1}
										disableRipple
										inputProps={{ "aria-labelledby": labelId }}
										sx={{
											color: colors.backgroundBlue4,
											"&.Mui-checked": {
												color: colors.primaryBlue,
											},
										}}
									/>
								</ListItemIcon>
								<ListItemText className="point-text" id={labelId} primary={value} />
							</ListItemButton>
						</ListItem>
					);
				})}
			</List>
		);
	};

	const SuggestedSolutions = () => {
		return (
			<>
				<Box className="d-flex align-c solution-heading-wrap">
					<img src={AddButton} alt="add button"></img>
					<span>SUGGESTED SOLUTIONS</span>
				</Box>
				{Checked.length ? (
					<Box className="solution-list">
						{SolutionList?.map((solution, index) => {
							return (
								<Box key={index} className="solution-tile d-flex align-c justify-sb">
									<span>{solution}</span>
									{/* <img src={ai} alt="ai button"></img> */}
									<SuggestedActions />
								</Box>
							);
						})}
					</Box>
				) : (
					<Box className="empty-box">
						<span>Select the problem points</span>
					</Box>
				)}
			</>
		);
	};

	const fetchProblemPoints = async () => {
		console.log(Prompt, "prompt config");
		const painPointPrompt = Prompt.LIST_PAIN_POINTS_PROMPT;
		console.log(painPointPrompt, "hiyaaa")

		const apiUrl = "http://34.74.45.36:5000/api/prompt";
		const apiKey = "wer3@#fNrtq10o";
		const requestBody = {
			messages: [
				{
					role: "system",
					content:
						"You are a bot helping a sales officer to execute his daily tasks. Provide response on the specific questions asked. If the answer is not available, respond with 'Information not available'.",
				},
				{
					role: "user",
					content: "What are the pain points in " + opportunity + ' discussions, provide maximum 5 points in short sentence in json array with the following format ```["Value 1", "Value 2",...]```',
				},
			],
		};
		const headers = {
			"Content-Type": "application/json", // Set the content type of the request body
			"X-API-Key": apiKey, // Set the x-api-key header with your API key
		};

		try {
			const response = await axios.post(apiUrl, requestBody, { headers });
			return response.data.answer;
		} catch (error) {
			console.log(error);
		}
	};

	const fetchSuggestedSolutions = async (checkList) => {
		const s = checkList.length === 1 ? " " : "s ";
		const apiUrl = "http://34.74.45.36:5000/api/prompt";
		const apiKey = "wer3@#fNrtq10o";
		const requestBody = {
			model_name: "ft:gpt-3.5-turbo-0613:dealstreamai::84DEtAYU",
			messages: [
				{
					role: "system",
					content:
						"You are a bot helping a sales officer to execute his daily tasks. Provide response on the specific questions asked. If the answer is not available, respond with 'Information not available'.",
				},
				{
					role: "user",
					content:
						"List the suggested solutions for the pain point" +
						s +
						checkList +
						" in " +
						opportunity +
						' in short sentence in json array with the following format ```["Value 1", "Value 2",...]```',
				},
			],
		};
		const headers = {
			"Content-Type": "application/json", // Set the content type of the request body
			"X-API-Key": apiKey, // Set the x-api-key header with your API key
		};

		try {
			const response = await axios.post(apiUrl, requestBody, { headers });
			return response.data.answer;
		} catch (error) {
			console.log(error);
		}
	};

	return (
		<Box className="d-flex pain-list-page">
			<Box className="col-8 pain-list-wrap box-b">
				<Box className="d-flex align-c proj-name-wrap">
					<img onClick={() => backNav(-1)} src={BackButton}></img>
					<span>{opportunity}</span>
				</Box>
				<Box className="d-flex proj-detail-wrap">
					<Box className="d-flex col-9">
						<Box className="proj-detail col-4">
							<label className="proj-detail-label">Account Name</label>
							<Typography className="proj-detail-cont">{accountName}</Typography>
						</Box>
						<Box className="proj-detail col-4">
							<label className="proj-detail-label">Related to</label>
							<Typography className="proj-detail-cont">{relationName}</Typography>
						</Box>
						<Box className="proj-detail col-4">
							<label className="proj-detail-label">Lead Stage</label>
							<Typography className="proj-detail-cont">{leadStage}</Typography>
						</Box>
					</Box>
					<Button className="CRM-button">
						<img src={ViewMore}></img>
						<span>View in CRM</span>
					</Button>
				</Box>
				<Box className="d-flex pain-point-wrap">
					<Box className="col-6 point-wrap">
						<h4>Problem Points</h4>
						<GetPainList />
					</Box>
					<Box className="col-6 solution-wrap">
						<SuggestedSolutions />
					</Box>
				</Box>
			</Box>
			<Box className="col-4">
				<PaymentSummary />
			</Box>
		</Box>
	);
}

export default PainPointList;

const samplePainList = [
	"Stalled Opportunity",
	"No response from the stakeholders",
	"Need pricing estimates",
	"Legal document conflict",
	"No compelling events",
	"Timeline mismatch",
];

const sampleSolutionList = [
	"Identify the key stakeholders",
	"Reconnect and build relationships",
	"Address concerns and objections",
	"Modify your approach",
	"Offer your limited time promotion",
	"Share success story",
	"Offer a reference call",
	"Refer a Mutual Activity Plan",

	"Identify the key stakeholders",
	"Reconnect and build relationships",
	"Address concerns and objections",
];

const answer1 = "['Limited budget for IT investments', 'Complex decision-making process involving multiple stakeholders', 'Concerns about data security and privacy', 'Need for seamless integration with existing systems', 'Desire for a solution that can scale and adapt to future needs']"

const answer2 = "[\"Competition from other providers\", \"Price sensitivity of customers\", \"Challenges in network coverage\", \"Complexity of service offerings\", \"Customer dissatisfaction with existing providers\"]"

const answer3 = '["Limited budget for IT investments", "Complex decision-making process involving multiple stakeholders", "Concerns about data security and privacy", "Need for seamless integration with existing systems", "Desire for a solution that can scale and adapt to future needs"]'