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

export default function BranchHealthPanel() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function loadData() {
      try {
        const response = await apiClient.get('/branches/maintenance-flags');
        setRows(response.data);
      } catch {
        setError('Could not load branch maintenance flags.');
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
        Branch Maintenance Flags
      </Typography>

      {rows.length === 0 ? (
        <Typography color="text.secondary">No branches currently exceed the 30% maintenance threshold.</Typography>
      ) : (
        <Stack spacing={1.5}>
          {rows.map((row) => (
            <Box key={row.id} sx={{ border: 1, borderColor: 'divider', borderRadius: 1, p: 1.5 }}>
              <Typography fontWeight={700}>{row.name}</Typography>
              <Typography variant="body2" color="text.secondary">
                {row.location_region} · {row.maintenance_atms}/{row.atm_total} ATMs flagged
              </Typography>
              <Typography variant="body2" color="warning.main">
                Maintenance rate: {Number(row.maintenance_rate).toFixed(1)}%
              </Typography>
            </Box>
          ))}
        </Stack>
      )}
    </Paper>
  );
}
