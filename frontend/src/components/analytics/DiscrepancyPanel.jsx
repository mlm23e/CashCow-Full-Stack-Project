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

export default function DiscrepancyPanel() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function loadData() {
      try {
        const response = await apiClient.get('/service_calls/discrepancies');
        setRows(response.data);
      } catch {
        setError('Could not load service-call discrepancies.');
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
        Co-location Discrepancies
      </Typography>

      {rows.length === 0 ? (
        <Typography color="text.secondary">No ATM/technician branch mismatches found.</Typography>
      ) : (
        <Stack spacing={1.5}>
          {rows.map((row) => (
            <Box key={row.service_id} sx={{ border: 1, borderColor: 'divider', borderRadius: 1, p: 1.5 }}>
              <Typography fontWeight={700}>{row.title}</Typography>
              <Typography variant="body2" color="text.secondary">
                ATM '{row.atm_id}' branch: {row.atm_branch_id} · Technician '{row.technician_id}' branch: {row.technician_branch_id}
              </Typography>
            </Box>
          ))}
        </Stack>
      )}
    </Paper>
  );
}
