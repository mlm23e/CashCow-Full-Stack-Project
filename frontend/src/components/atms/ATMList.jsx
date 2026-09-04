import {Grid} from '@mui/material';
import ATMCard from './ATMCard.jsx'

function ATMList({atms}) {
    return (
        <Grid container spacing = {2}>
            {/**
             * The map function is used to iterate over the 'atms' array and render
             * a ATMCard component for each ATM
             */}
             {atms.map((atm)=> (
            <Grid item key={atm.id}>
                <ATMCard atm={atm} />
            </Grid>
        ))}
        </Grid>
    );
}

export default ATMList;