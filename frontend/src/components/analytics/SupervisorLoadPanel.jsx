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

export default function SupervisorLoadPanel({ supervisorId = 1 }) {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function loadData() {
      try {
        const response = await apiClient.get(`/users/active-calls/${supervisorId}`);
        setRows(response.data);
      } catch {
        setError('Could not load active technician assignments.');
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, [supervisorId]);

  if (loading) return <CircularProgress />;
  if (error) return <Alert severity="error">{error}</Alert>;

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h7" sx={{ mb: 2 }}>
        Technicians with Active Service Calls
      </Typography>

      {rows.length === 0 ? (
        <Typography color="text.secondary">No active assignments for this supervisor.</Typography>
      ) : (
        <Stack spacing={1.5}>
          {rows.map((row) => (
            <Box key={row.technician_id} sx={{ border: 1, borderColor: 'divider', borderRadius: 1, p: 1.5 }}>
              <Typography fontWeight={700}>
                {row.first_name} {row.last_name}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Active calls: {row.active_call_count}
              </Typography>
            </Box>
          ))}
        </Stack>
      )}
    </Paper>
  );
}
