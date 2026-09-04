import { useEffect, useState } from 'react';
import { DataGrid } from '@mui/x-data-grid';
import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  MenuItem,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutlined';
import EditOutlinedIcon from '@mui/icons-material/EditOutlined';
import apiClient from '../../api/client.js';
import { useAuth } from '../../context/AuthContext.jsx';

const columns = [
  { field: 'id', headerName: 'ID', width: 80 },
  { field: 'title', headerName: 'Title', flex: 1.8, minWidth: 200 },
  {
    field: 'priority',
    headerName: 'Priority',
    width: 130,
    renderCell: (params) => {
      const color =
        params.value === 'Critical'
          ? 'error'
          : params.value === 'Medium'
            ? 'warning'
            : 'success';

      return <Chip label={params.value} color={color} size="small" />;
    },
  },
  {
    field: 'status',
    headerName: 'Status',
    width: 160,
    renderCell: (params) => (
      <Typography
        variant="body2"
        sx={{
          color:
            params.value === 'Completed'
              ? 'success.main'
              : params.value === 'Failed'
                ? 'error.main'
                : params.value === 'In-Progress'
                  ? 'info.main'
                  : 'text.primary',
          fontWeight: 600,
        }}
      >
        {params.value}
      </Typography>
    ),
  },
  { field: 'atm_id', headerName: 'ATM', width: 100, type: 'number' },
  { field: 'technician_id', headerName: 'Technician', width: 130, type: 'number' },
];

export default function ServiceCallGrid() {
  const { user } = useAuth();
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedCall, setSelectedCall] = useState(null);
  const [formValues, setFormValues] = useState({
    title: '',
    priority: 'Medium',
    status: 'Pending',
    atm_id: '',
    technician_id: '',
  });

  const canManage = user?.role === 'Operations Admin' || user?.role === 'Field Technician';

  const resetForm = () => {
    setSelectedCall(null);
    setFormValues({
      title: '',
      priority: 'Medium',
      status: 'Pending',
      atm_id: '',
      technician_id: '',
    });
  };

  const openCreateDialog = () => {
    resetForm();
    setDialogOpen(true);
  };

  const openEditDialog = (row) => {
    setSelectedCall(row);
    setFormValues({
      title: row.title,
      priority: row.priority,
      status: row.status,
      atm_id: row.atm_id,
      technician_id: row.technician_id ?? '',
    });
    setDialogOpen(true);
  };

  const handleFieldChange = (field) => (event) => {
    setFormValues((prev) => ({ ...prev, [field]: event.target.value }));
  };

  const handleSubmit = async () => {
    try {
      const payload = {
        ...formValues,
        atm_id: Number(formValues.atm_id),
        technician_id: formValues.technician_id === '' ? null : Number(formValues.technician_id),
      };

      if (selectedCall) {
        await apiClient.patch(`/service_calls/${selectedCall.id}`, payload);
      } else {
        await apiClient.post('/service_calls', payload);
      }

      setDialogOpen(false);
      resetForm();
      await loadCalls();
    } catch (submitError) {
      const detail = submitError.response?.data?.detail || 'Could not save service call.';
      setError(detail);
    }
  };

  const handleDelete = async (serviceCall) => {
    if (!window.confirm(`Delete service call #${serviceCall.id}? This cannot be undone.`)) return;

    try {
      await apiClient.delete(`/service_calls/${serviceCall.id}`);
      await loadCalls();
    } catch (deleteError) {
      const detail = deleteError.response?.data?.detail || 'Could not delete service call.';
      setError(detail);
    }
  };

  useEffect(() => {
    loadCalls();
  }, []);

  async function loadCalls() {
    try {
      const response = await apiClient.get('/service_calls');
      setRows(response.data);
    } catch {
      setError('Could not load service calls.');
    } finally {
      setLoading(false);
    }
  }

  if (loading) return <CircularProgress />;
  if (error) return <Alert severity="error">{error}</Alert>;

  return (
    <Box sx={{ display: 'grid', gap: 2 }}>
      {canManage && (
        <Button variant="contained" onClick={openCreateDialog} sx={{ justifySelf: 'flex-end' }}>
          Add Service Call
        </Button>
      )}

      <Box sx={{ height: 420, width: '100%' }}>
        <DataGrid
          rows={rows}
          columns={[
            ...columns,
            ...(canManage
              ? [{
                  field: 'actions',
                  headerName: 'Actions',
                  width: 110,
                  sortable: false,
                  filterable: false,
                  renderCell: (params) => (
                    <Stack direction="row">
                      <IconButton aria-label={`Edit service call ${params.row.id}`} size="small" onClick={() => openEditDialog(params.row)}>
                        <EditOutlinedIcon fontSize="small" />
                      </IconButton>
                      <IconButton aria-label={`Delete service call ${params.row.id}`} size="small" color="error" onClick={() => handleDelete(params.row)}>
                        <DeleteOutlineIcon fontSize="small" />
                      </IconButton>
                    </Stack>
                  ),
                }]
              : []),
          ]}
          getRowId={(row) => row.id}
          pageSizeOptions={[5, 10, 25]}
          initialState={{ pagination: { paginationModel: { page: 0, pageSize: 10 } } }}
          onRowDoubleClick={(params) => canManage && openEditDialog(params.row)}
          disableRowSelectionOnClick
        />
      </Box>

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>{selectedCall ? 'Edit Service Call' : 'Add Service Call'}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField label="Title" value={formValues.title} onChange={handleFieldChange('title')} />
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              <TextField select label="Priority" value={formValues.priority} onChange={handleFieldChange('priority')} fullWidth>
                {['Low', 'Medium', 'Critical'].map((value) => (
                  <MenuItem key={value} value={value}>{value}</MenuItem>
                ))}
              </TextField>
              <TextField select label="Status" value={formValues.status} onChange={handleFieldChange('status')} fullWidth>
                {['Pending', 'In-Progress', 'Completed', 'Failed'].map((value) => (
                  <MenuItem key={value} value={value}>{value}</MenuItem>
                ))}
              </TextField>
            </Stack>
            <TextField label="ATM ID" type="number" value={formValues.atm_id} onChange={handleFieldChange('atm_id')} />
            <TextField label="Technician ID" type="number" value={formValues.technician_id} onChange={handleFieldChange('technician_id')} />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSubmit}>{selectedCall ? 'Save' : 'Create'}</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
