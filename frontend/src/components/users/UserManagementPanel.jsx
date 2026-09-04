import { useEffect, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  MenuItem,
  Stack,
  TextField,
} from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import { useAuth } from '../../context/AuthContext.jsx';
import apiClient from '../../api/client.js';

const ROLE_OPTIONS = ['Operations Admin', 'Field Technician', 'Auditor'];

export default function UserManagementPanel() {
  const { user } = useAuth();
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [formValues, setFormValues] = useState({
    username: '',
    first_name: '',
    last_name: '',
    role: 'Field Technician',
    branch_id: '',
    password: '',
  });

  const canManage = user?.role === 'Operations Admin';

  async function fetchUsers() {
    try {
      const response = await apiClient.get('/users');
      setRows(response.data);
      setError('');
    } catch {
      setError('Could not load users.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (canManage) {
      fetchUsers();
      return;
    }
    setLoading(false);
  }, [canManage]);

  const handleFieldChange = (field) => (event) => {
    setFormValues((prev) => ({ ...prev, [field]: event.target.value }));
  };

  const resetForm = () => {
    setFormValues({
      username: '',
      first_name: '',
      last_name: '',
      role: 'Field Technician',
      branch_id: '',
      password: '',
    });
    setEditingUser(null);
  };

  const openCreateDialog = () => {
    resetForm();
    setDialogOpen(true);
  };

  const openEditDialog = (row) => {
    setEditingUser(row);
    setFormValues({
      username: row.username,
      first_name: row.first_name,
      last_name: row.last_name,
      role: row.role,
      branch_id: row.branch_id ?? '',
      password: '',
    });
    setDialogOpen(true);
  };

  const submitUser = async () => {
    if (!canManage) return;

    const payload = {
      ...formValues,
      branch_id: formValues.branch_id === '' ? null : Number(formValues.branch_id),
    };

    try {
      if (editingUser) {
        await apiClient.patch(`/users/${editingUser.id}`, payload);
      } else {
        await apiClient.post('/users', payload);
      }

      setDialogOpen(false);
      resetForm();
      await fetchUsers();
    } catch (submitError) {
      const message = submitError.response?.data?.detail || 'Could not save user.';
      setError(message);
    }
  };

  if (!canManage) {
    return <Alert severity="info">User management is restricted to Operations Admin accounts.</Alert>;
  }

  if (loading) return <CircularProgress />;

  const columns = [
    { field: 'id', headerName: 'ID', width: 80 },
    { field: 'username', headerName: 'Username', flex: 1, minWidth: 140 },
    { field: 'first_name', headerName: 'First Name', flex: 1, minWidth: 120 },
    { field: 'last_name', headerName: 'Last Name', flex: 1, minWidth: 120 },
    { field: 'role', headerName: 'Role', width: 180 },
    { field: 'branch_id', headerName: 'Branch', width: 100, type: 'number' },
  ];

  return (
    <Box sx={{ display: 'grid', gap: 2 }}>
      <Button variant="contained" onClick={openCreateDialog} sx={{ justifySelf: 'flex-end' }}>
        Add User
      </Button>

      {error && <Alert severity="error">{error}</Alert>}

      <Box sx={{ height: 440, width: '100%' }}>
        <DataGrid
          rows={rows}
          columns={columns}
          getRowId={(row) => row.id}
          pageSizeOptions={[5, 10, 25]}
          onRowDoubleClick={(params) => openEditDialog(params.row)}
          disableRowSelectionOnClick
        />
      </Box>

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>{editingUser ? 'Edit User' : 'Create User'}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField label="Username" value={formValues.username} onChange={handleFieldChange('username')} />
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              <TextField label="First Name" value={formValues.first_name} onChange={handleFieldChange('first_name')} fullWidth />
              <TextField label="Last Name" value={formValues.last_name} onChange={handleFieldChange('last_name')} fullWidth />
            </Stack>
            <TextField select label="Role" value={formValues.role} onChange={handleFieldChange('role')}>
              {ROLE_OPTIONS.map((role) => (
                <MenuItem key={role} value={role}>{role}</MenuItem>
              ))}
            </TextField>
            <TextField
              label="Branch ID"
              type="number"
              value={formValues.branch_id}
              onChange={handleFieldChange('branch_id')}
            />
            {!editingUser && (
              <TextField
                label="Password"
                type="password"
                value={formValues.password}
                onChange={handleFieldChange('password')}
              />
            )}
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={submitUser}>{editingUser ? 'Save Changes' : 'Create User'}</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
