import { Box, Button, Checkbox, Drawer, List, ListItem, ListItemButton, ListItemIcon, ListItemText } from "@mui/material";
import React, { useState } from 'react';
import './SuggestedActions.scss';

import ai from "../../assets/ai.svg";
import close from "../../assets/close.svg";
import listCircle from "../../assets/listing-circle.svg";
import userIcon from "../../assets/user-icon-1.jpg";
import phone from "../../assets/Phone.svg";
import email from "../../assets/email.svg";

export default function SuggestedActions() {
  const [open, setOpen] = useState(false);

  const toggleDrawer = (isOpen) => () => {
    setOpen(isOpen);
  };

  const GetSuggActionList = () => {
    return (
      <List>
        {sampleSuggActionList?.map((value) => {
          return (
            <ListItem key={value} disablePadding>
              <ListItemButton className="list-icon-button-wrap">
                <ListItemIcon className="list-icon-wrap">
                  <img src={listCircle} alt="list icon" />
                </ListItemIcon>
                <ListItemText className="point-text" primary={value} />
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>
    );
  };

  const GetAdditionalContactList = () => {
    return (
      <>
        {sampleAdditionalContactList?.map((value) => {
          return (
            <Box key={value} className="contact-tile">
              <Box className="cont-detail-wrap d-flex justify-sb align-c">
                <Box className="cont-detail d-flex align-c">
                  <img src={userIcon} alt="list icon" />
                  <Box>
                    <p>Binta Susan</p>
                    <p>CEO, Siemens</p>
                  </Box>
                </Box>
                <Box>
                  <Button>Schedule meeting</Button>
                  <Button>Sent Email</Button>
                </Box>
              </Box>
              <Box className="cont-method-wrap d-flex align-c">
                <Box>
                  <img src={phone} alt="list icon" />
                  <span>+121 95605 56789</span>
                </Box>
                <Box>
                  <img src={email} alt="list icon" />
                  <span>Binta.Susan@Siemens.Com</span>
                </Box>
              </Box>
            </Box>
          );
        })}
      </>
    );
  };

  return (
    <div>
      <Button className="ai-button btn" onClick={toggleDrawer(true)}>
        <img src={ai} alt="ai icon" />
      </Button>
      <Drawer anchor="right" open={open} onClose={toggleDrawer(false)}>
        <Box className="sa-wrap">
          <Box className="sa-header d-flex justify-sb align-c">
            <h4>Suggested Actions</h4>
            <Button className="btn">
              <img src={close} alt="close icon"></img>
            </Button>
          </Box>
          <Box className="sa-content">
            <GetSuggActionList />
            {/* <h3>Here are some additional contacts:</h3> */}
            {/* <GetAdditionalContactList /> */}
          </Box>
        </Box>
      </Drawer>
    </div>
  );
}

const sampleSuggActionList = [
  "Identify additional influencers and connect with them to ascertain situation",
  "Click here to see ideal reference customers",
  "Click here to download success stories",
  "Click here to build a Mutual Activity Plan for Siemens",
];

const
  sampleAdditionalContactList = [
    1, 2, 3
  ];

