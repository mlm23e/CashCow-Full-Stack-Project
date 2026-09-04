import { useEffect, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import apiClient from '../../api/client.js';

export default function DiagnosticReportPanel() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [formValues, setFormValues] = useState({
    service_call_id: '',
    file_url: '',
    notes: '',
  });

  async function fetchReports() {
    try {
      const response = await apiClient.get('/diagnostic_reports');
      setReports(response.data);
      setError('');
    } catch {
      setError('Could not load diagnostic reports.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchReports();
  }, []);

  const handleFieldChange = (field) => (event) => {
    setFormValues((prev) => ({ ...prev, [field]: event.target.value }));
  };

  const handleSubmit = async () => {
    try {
      await apiClient.post('/diagnostic_reports', {
        ...formValues,
        service_call_id: Number(formValues.service_call_id),
      });

      setFormValues({
        service_call_id: '',
        file_url: '',
        notes: '',
      });
      await fetchReports();
    } catch (submitError) {
      const message = submitError.response?.data?.detail || 'Could not upload diagnostic report.';
      setError(message);
    }
  };

  if (loading) return <CircularProgress />;

  return (
    <Box sx={{ display: 'grid', gap: 2 }}>
      <Card variant="outlined">
        <CardContent>
          <Stack spacing={2}>
            <Typography variant="h6">Upload diagnostic report</Typography>
            {error && <Alert severity="error">{error}</Alert>}
            <TextField
              label="Service Call ID"
              type="number"
              value={formValues.service_call_id}
              onChange={handleFieldChange('service_call_id')}
            />
            <TextField
              label="File URL"
              value={formValues.file_url}
              onChange={handleFieldChange('file_url')}
            />
            <TextField
              label="Notes"
              multiline
              minRows={3}
              value={formValues.notes}
              onChange={handleFieldChange('notes')}
            />
            <Button variant="contained" onClick={handleSubmit}>Save report</Button>
          </Stack>
        </CardContent>
      </Card>

      <Box sx={{ display: 'grid', gap: 1 }}>
        <Typography variant="h6">Recent attachments</Typography>
        {reports.length === 0 ? (
          <Alert severity="info">No diagnostic reports have been uploaded yet.</Alert>
        ) : (
          reports.map((report) => (
            <Card key={report.id} variant="outlined">
              <CardContent>
                <Typography variant="subtitle2">Service Call #{report.service_call_id}</Typography>
                <Typography variant="body2" color="text.secondary">{report.file_url}</Typography>
                <Typography variant="body2" sx={{ mt: 1 }}>{report.notes || 'No notes provided.'}</Typography>
              </CardContent>
            </Card>
          ))
        )}
      </Box>
    </Box>
  );
}
