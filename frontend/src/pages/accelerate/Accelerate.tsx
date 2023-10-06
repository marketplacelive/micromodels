import { Box } from "@mui/material";
import React, { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper } from "@mui/material";

import "./Accelerate.scss";
import { SubHeader } from "../../components/sub-header/SubHeader";
import Footer from "../../components/footer/Footer";

function Accelerate() {
	const [newProjectList, setNewList] = useState([]);
	const navigate = useNavigate();

	const navToPainPointList = (projName: any) => {
    navigate('pain-point-list', {
      state: projName,
    });
  };

	useEffect(() => {
		fetchdata().then((res) => {
			let updatedProjectList = [];
			res && (updatedProjectList = JSON.parse(res));
			setNewList(updatedProjectList);
		});
	}, []);

	return (
		<>
			<SubHeader />
			<Box className="page-container accelerate">
				<Box className="record-count-wrap">
					Total Records:{" "}
					<span className="record-count">
						<b>10</b>
					</span>
				</Box>
				{/* <Box className="project-table-container"> */}
				<Box className="project-table-wrap">
					<TableContainer className="project-table-container" component={Paper}>
						<Table className="project-table" aria-label="simple table">
							<TableHead className="project-table-head">
								<TableRow>
									<TableCell className="proj-table-first-head">PROJECT</TableCell>
									<TableCell align="left">ACCOUNT</TableCell>
									<TableCell align="left">DEAL STAGE</TableCell>
									<TableCell align="left">ENGAGEMENT SCORE</TableCell>
									<TableCell align="left">CONVERSION PROBABILITY</TableCell>
									<TableCell align="left">LAST ACTIVE</TableCell>
									<TableCell align="left">LAST ACTION</TableCell>
								</TableRow>
							</TableHead>
							<TableBody>
								{newProjectList?.map((row, index) => (
									<TableRow
										key={index}
										onClick={() => {
											navToPainPointList(row);
										}}
									>
										{/* <TableCell
											className="proj-table-first-col"
											scope="row"
											onClick={() => {
												navToPainPointList("pain-point-list");
											}}
										>
											{row["Name"]}
										</TableCell>
										<TableCell align="left">{row["Id"]}</TableCell>
										<TableCell align="left">{row["StageName"]}</TableCell>
										<TableCell align="left">{row["Meddpic__c"]}/100</TableCell>
										<TableCell align="left">{row["Probability"]}%</TableCell>
										<TableCell align="left">{formatDate(row["CloseDate"])}</TableCell>
										<TableCell align="left">{row["StageName"]}</TableCell> */}

										<TableCell className="proj-table-first-col" scope="row">
											{row}
										</TableCell>
										<TableCell align="left">{"006Hs00001DHMVBIA5"}</TableCell>
										<TableCell align="left">{"Prospecting"}</TableCell>
										<TableCell align="left">{10}/100</TableCell>
										<TableCell align="left">{20}%</TableCell>
										<TableCell align="left">{"20 Dec 2023"}</TableCell>
										<TableCell align="left">{"Prospecting"}</TableCell>
									</TableRow>
								))}
							</TableBody>
						</Table>
					</TableContainer>
				</Box>
				{/* </Box> */}
			</Box>
			<Footer />
		</>
	);
}

export const fetchdata = async () => {
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
					'List the name of all under performing opportunities in json array with the following format ["Value 1", "Value 2",...]',
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

const formatDate = (inputDate: any) => {
	const options = { year: "numeric", month: "long", day: "numeric" };
	return new Date(inputDate).toDateString();
};

export default Accelerate;

const sampleProjectList = [
	{
		attributes: {
			type: "Opportunity",
			url: "/services/data/v58.0/sobjects/Opportunity/006Hs00001DHMVBIA5",
		},
		Id: "006Hs00001DHMVBIA5",
		Name: "American A_product x",
		StageName: "Prospecting",
		Probability: 10,
		CloseDate: "2023-12-01",
		Meddpic__c: 10,
		CreatedDate: "2023-08-30T11:21:21.000+0000",
	},
	{
		attributes: {
			type: "Opportunity",
			url: "/services/data/v58.0/sobjects/Opportunity/006Hs00001DHMYmIAP",
		},
		Id: "006Hs00001DHMYmIAP",
		Name: "Ericson_Product D",
		StageName: "Prospecting",
		Probability: 10,
		CloseDate: "2023-12-01",
		Meddpic__c: 11,
		CreatedDate: "2023-08-30T11:17:21.000+0000",
	},
	{
		attributes: {
			type: "Opportunity",
			url: "/services/data/v58.0/sobjects/Opportunity/006Hs00001DHMXyIAP",
		},
		Id: "006Hs00001DHMXyIAP",
		Name: "Walmart_product x",
		StageName: "Prospecting",
		Probability: 10,
		CloseDate: "2023-12-01",
		Meddpic__c: 11,
		CreatedDate: "2023-08-30T11:13:12.000+0000",
	},
	{
		attributes: {
			type: "Opportunity",
			url: "/services/data/v58.0/sobjects/Opportunity/006Hs00001DHMVAIA5",
		},
		Id: "006Hs00001DHMVAIA5",
		Name: "Vodafone_Product H",
		StageName: "Prospecting",
		Probability: 10,
		CloseDate: "2023-12-01",
		Meddpic__c: 14,
		CreatedDate: "2023-08-30T11:07:19.000+0000",
	},
	{
		attributes: {
			type: "Opportunity",
			url: "/services/data/v58.0/sobjects/Opportunity/006Hs00001DHMV9IAP",
		},
		Id: "006Hs00001DHMV9IAP",
		Name: "Siemens_product x",
		StageName: "Prospecting",
		Probability: 10,
		CloseDate: "2023-12-01",
		Meddpic__c: 12,
		CreatedDate: "2023-08-30T11:00:46.000+0000",
	},
	{
		attributes: {
			type: "Opportunity",
			url: "/services/data/v58.0/sobjects/Opportunity/006Hs00001DHMTrIAP",
		},
		Id: "006Hs00001DHMTrIAP",
		Name: "RolssRoyce_Product H",
		StageName: "Closed Won",
		Probability: 100,
		CloseDate: "2023-12-01",
		Meddpic__c: 20,
		CreatedDate: "2023-08-30T10:55:30.000+0000",
	},
	{
		attributes: {
			type: "Opportunity",
			url: "/services/data/v58.0/sobjects/Opportunity/006Hs00001DHM2FIAX",
		},
		Id: "006Hs00001DHM2FIAX",
		Name: "Oracle_Product Z",
		StageName: "Closed Won",
		Probability: 100,
		CloseDate: "2023-12-01",
		Meddpic__c: 20,
		CreatedDate: "2023-08-30T10:48:10.000+0000",
	},
	{
		attributes: {
			type: "Opportunity",
			url: "/services/data/v58.0/sobjects/Opportunity/006Hs00001DHLY8IAP",
		},
		Id: "006Hs00001DHLY8IAP",
		Name: "Tesco_Product Z",
		StageName: "Closed Won",
		Probability: 100,
		CloseDate: "2023-12-01",
		Meddpic__c: 20,
		CreatedDate: "2023-08-30T10:43:32.000+0000",
	},
	{
		attributes: {
			type: "Opportunity",
			url: "/services/data/v58.0/sobjects/Opportunity/006Hs00001DHLC6IAP",
		},
		Id: "006Hs00001DHLC6IAP",
		Name: "Pfizer_Product Y",
		StageName: "Closed Won",
		Probability: 100,
		CloseDate: "2023-12-01",
		CreatedDate: "2023-08-30T10:14:01.000+0000",
	},
	{
		attributes: {
			type: "Opportunity",
			url: "/services/data/v58.0/sobjects/Opportunity/006Hs00001DHLBcIAP",
		},
		Id: "006Hs00001DHLBcIAP",
		Name: "Dell_Product",
		StageName: "Closed Lost",
		Probability: 0,
		CloseDate: "2023-12-01",
		CreatedDate: "2023-08-30T10:10:25.000+0000",
	},
];
