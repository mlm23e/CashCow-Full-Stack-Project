import { useEffect, useState } from 'react';
import {
  Alert,
  Box,
  CircularProgress,
  Paper,
  Stack,
  Typography,
} from '@mui/material';
import apiClient from '../../api/client.js';

export default function LowCashPanel() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function loadData() {
      try {
        const low_cash = 20;
        const response = await apiClient.get(`/atms/?max_cash=${low_cash.toString()}`);
        setRows(response.data);
      } catch {
        setError('Could not load ATMs with cash level < 20%.');
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  if (loading) return <CircularProgress />;
  if (error) return <Alert severity="error">{error}</Alert>;

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6" sx={{ mb: 2 }}>
        Low-Cash ATMs
      </Typography>

      {rows.length === 0 ? (
        <Typography color="text.secondary">No ATMs with &lt; 20% found.</Typography>
      ) : (
        <Stack spacing={1.5}>
          {rows.map((row) => (
            <Box key={row.id} sx={{ border: 1, borderColor: 'divider', borderRadius: 1, p: 1.5 }}>
              <Typography fontWeight={500}>{row.model} @ Branch {row.branch_id}</Typography>
              <Typography variant="body2" color="text.secondary">
                Serial Number '{row.serial_number}' : {row.cash_level}% Cash 
              </Typography>
            </Box>
          ))}
        </Stack>
      )}
    </Paper>
  );
}
