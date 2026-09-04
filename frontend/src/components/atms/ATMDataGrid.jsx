import { useEffect, useMemo, useState } from 'react';
import { DataGrid } from '@mui/x-data-grid';
import {
  Alert,
  Box,
  Button,
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
  { field: 'serial_number', headerName: 'Serial Number', flex: 1.3, minWidth: 150 },
  { field: 'model', headerName: 'Model', flex: 1, minWidth: 150 },
  { field: 'cash_level', headerName: 'Cash %', width: 110, type: 'number' },
  {
    field: 'status',
    headerName: 'Status',
    width: 140,
    renderCell: (params) => (
      <Typography
        variant="body2"
        sx={{
          color:
            params.value === 'Operational'
              ? 'success.main'
              : params.value === 'Maintenance'
                ? 'warning.main'
                : 'error.main',
          fontWeight: 600,
        }}
      >
        {params.value}
      </Typography>
    ),
  },
  { field: 'branch_id', headerName: 'Branch ID', width: 120, type: 'number' },
];

const STATUS_OPTIONS = ['Operational', 'Maintenance', 'Offline'];

function ATMDataGrid({ onSuccess }) {
  const { user } = useAuth();
  const [atms, setATMs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedAtm, setSelectedAtm] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  const [formValues, setFormValues] = useState({
    serial_number: '',
    model: '',
    cash_level: '',
    branch_id: '',
    status: 'Operational',
  });

  async function fetchATMs() {
    setLoading(true);
    try {
      const response = await apiClient.get('/atms');
      setATMs(response.data);
      setError(null);
    } catch {
      setError('Could not load ATM data.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchATMs();
  }, []);

  const filteredATMs = useMemo(() => {
    const term = searchTerm.trim().toLowerCase();

    return atms.filter((atm) => {
      const matchesSearch =
        !term ||
        atm.serial_number?.toLowerCase().includes(term) ||
        atm.model?.toLowerCase().includes(term) ||
        String(atm.branch_id).includes(term);

      const matchesStatus = statusFilter === 'All' || atm.status === statusFilter;
      return matchesSearch && matchesStatus;
    });
  }, [atms, searchTerm, statusFilter]);

  const canManage = user?.role === 'Operations Admin';

  const handleDelete = async (atm) => {
    if (!window.confirm(`Delete ATM ${atm.serial_number}? This cannot be undone.`)) return;

    try {
      await apiClient.delete(`/atms/${atm.id}`);
      if (onSuccess) onSuccess(`ATM ${atm.serial_number} deleted.`);
      await fetchATMs();
    } catch (deleteError) {
      const detail = deleteError.response?.data?.detail || 'Could not delete ATM.';
      setError(detail);
    }
  };

  const resetForm = () => {
    setSelectedAtm(null);
    setFormValues({
      serial_number: '',
      model: '',
      cash_level: '',
      branch_id: '',
      status: 'Operational',
    });
  };

  const openCreateDialog = () => {
    resetForm();
    setDialogOpen(true);
  };

  const openEditDialog = (atm) => {
    setSelectedAtm(atm);
    setFormValues({
      serial_number: atm.serial_number,
      model: atm.model,
      cash_level: atm.cash_level,
      branch_id: atm.branch_id,
      status: atm.status,
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
        cash_level: Number(formValues.cash_level),
        branch_id: Number(formValues.branch_id),
      };

      if (selectedAtm) {
        await apiClient.patch(`/atms/${selectedAtm.id}`, payload);
        if (onSuccess) {
          onSuccess(`ATM ${payload.serial_number} updated.`);
        }
      } else {
        await apiClient.post('/atms', payload);
        if (onSuccess) {
          onSuccess(`ATM ${payload.serial_number} created.`);
        }
      }

      setDialogOpen(false);
      resetForm();

      await fetchATMs();
    } catch (submitError) {
      const detail = submitError.response?.data?.detail || 'Could not save ATM.';
      setError(detail);
    }
  };

  if (loading) return <CircularProgress />;
  if (error) return <Alert severity="error">{error}</Alert>;

  return (
    <Box>
      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ mb: 2 }}>
        <TextField
          size="small"
          label="Search ATMs"
          value={searchTerm}
          onChange={(event) => setSearchTerm(event.target.value)}
          sx={{ minWidth: 220 }}
        />
        <TextField
          select
          size="small"
          label="Status"
          value={statusFilter}
          onChange={(event) => setStatusFilter(event.target.value)}
          sx={{ minWidth: 180 }}
        >
          <MenuItem value="All">All</MenuItem>
          {STATUS_OPTIONS.map((option) => (
            <MenuItem key={option} value={option}>
              {option}
            </MenuItem>
          ))}
        </TextField>
        {canManage && (
          <Button variant="contained" onClick={openCreateDialog} sx={{ ml: 'auto' }}>
            Add ATM
          </Button>
        )}
      </Stack>

      <Box sx={{ height: 440, width: '100%' }}>
        <DataGrid
          rows={filteredATMs}
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
                      <IconButton aria-label={`Edit ATM ${params.row.id}`} size="small" onClick={() => openEditDialog(params.row)}>
                        <EditOutlinedIcon fontSize="small" />
                      </IconButton>
                      <IconButton aria-label={`Delete ATM ${params.row.id}`} size="small" color="error" onClick={() => handleDelete(params.row)}>
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

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
        <DialogTitle>{selectedAtm ? 'Edit ATM' : 'Add New ATM'}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1, minWidth: 320 }}>
            <TextField
              label="Serial Number"
              value={formValues.serial_number}
              onChange={handleFieldChange('serial_number')}
            />
            <TextField label="Model" value={formValues.model} onChange={handleFieldChange('model')} />
            <TextField
              label="Cash Level"
              type="number"
              value={formValues.cash_level}
              onChange={handleFieldChange('cash_level')}
            />
            <TextField
              label="Branch ID"
              type="number"
              value={formValues.branch_id}
              onChange={handleFieldChange('branch_id')}
            />
            <TextField
              select
              label="Status"
              value={formValues.status}
              onChange={handleFieldChange('status')}
            >
              {STATUS_OPTIONS.map((option) => (
                <MenuItem key={option} value={option}>
                  {option}
                </MenuItem>
              ))}
            </TextField>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSubmit}>{selectedAtm ? 'Save' : 'Create'}</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default ATMDataGrid;