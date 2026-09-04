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

export default function ReliabilityPanel() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function loadData() {
      try {
        const response = await apiClient.get('/service_calls/reliability');
        setRows(response.data);
      } catch {
        setError('Could not load service reliability metrics.');
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
        ATM Reliability by Model
      </Typography>

      {rows.length === 0 ? (
        <Typography color="text.secondary">No reliability data reported yet.</Typography>
      ) : (
        <Stack spacing={1.5}>
          {rows.map((row) => (
            <Box key={row.model} sx={{ border: 1, borderColor: 'divider', borderRadius: 1, p: 1.5 }}>
              <Typography fontWeight={700}>{row.model}</Typography>
              <Typography variant="body2" color="text.secondary">
                {row.total_calls} service calls · {row.completed_calls} completed · {row.failed_calls} failed
              </Typography>
              <Typography variant="body2" color="success.main">
                Completion rate: {Number(row.completion_rate).toFixed(1)}%
              </Typography>
              <Typography variant="body2" color="error.main">
                Failure rate: {Number(row.failure_rate).toFixed(1)}%
              </Typography>
            </Box>
          ))}
        </Stack>
      )}
    </Paper>
  );
}
