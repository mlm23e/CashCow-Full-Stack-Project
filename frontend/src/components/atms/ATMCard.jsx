import { Card, CardContent, Typography, Chip, Stack } from '@mui/material';

const LOW_CASH_THRESHOLD = 20;

function ATMCard({ atm }) {
  const isLowCash = atm.cash_level < LOW_CASH_THRESHOLD;

  return (
    <Card variant="outlined" sx={{ minWidth: 240 }}>
      <CardContent>
        {/* The Typography component lets us display text with different styles.*/}
        <Typography variant="h6" component="div">
          {atm.serial_number}
        </Typography>
        <Typography color="text.secondary" gutterBottom>
          {atm.model}
        </Typography>
        {/* The Stack component is a layout component that arranges its children in a row or column.*/}
        <Stack direction="row" spacing={1} alignItems="center">
        {/* The Chip component is a small, interactive element that can display information or trigger actions.*/}
          <Chip
            label={`${atm.cash_level}% cash`}
            color={isLowCash ? 'error' : 'success'}
            size="small"
          />
          <Chip label={atm.status} variant="outlined" size="small" />
        </Stack>
      </CardContent>
    </Card>
  );
}

export default ATMCard;