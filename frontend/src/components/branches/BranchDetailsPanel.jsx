import { useEffect, useMemo, useState } from 'react';
import {
  Alert,
  Box,
  Card,
  CardContent,
  CircularProgress,
  Divider,
  Grid,
  List,
  ListItem,
  ListItemText,
  MenuItem,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import apiClient from '../../api/client.js';

export default function BranchDetailsPanel() {
  const [branches, setBranches] = useState([]);
  const [atms, setAtms] = useState([]);
  const [selectedBranchId, setSelectedBranchId] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function loadBranchData() {
      try {
        const [branchesRes, atmsRes] = await Promise.all([
          apiClient.get('/branches'),
          apiClient.get('/atms'),
        ]);

        const fetchedBranches = branchesRes.data;
        setBranches(fetchedBranches);
        setAtms(atmsRes.data);

        if (fetchedBranches.length > 0) {
          setSelectedBranchId(String(fetchedBranches[0].id));
        }
      } catch {
        setError('Could not load branch details.');
      } finally {
        setLoading(false);
      }
    }

    loadBranchData();
  }, []);

  const selectedBranch = useMemo(
    () => branches.find((branch) => String(branch.id) === selectedBranchId) || branches[0],
    [branches, selectedBranchId],
  );

  const branchAtms = useMemo(
    () => atms.filter((atm) => atm.branch_id === Number(selectedBranch?.id)),
    [atms, selectedBranch],
  );

  if (loading) return <CircularProgress />;
  if (error) return <Alert severity="error">{error}</Alert>;

  return (
    <Box sx={{ display: 'grid', gap: 2 }}>
      <TextField
        select
        label="Branch"
        value={selectedBranchId}
        onChange={(event) => setSelectedBranchId(event.target.value)}
        fullWidth
      >
        {branches.map((branch) => (
          <MenuItem key={branch.id} value={String(branch.id)}>
            {branch.name}
          </MenuItem>
        ))}
      </TextField>

      {selectedBranch ? (
        <Card>
          <CardContent>
            <Stack spacing={2}>
              <Typography variant="h5">{selectedBranch.name}</Typography>
              <Divider />
              
              <Grid container spacing={2}>
                <Grid item xs={12} sm={4}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="caption" color="text.secondary">Branch ID</Typography>
                      <Typography variant="h5">{selectedBranch.id}</Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="caption" color="text.secondary">Supervisor ID</Typography>
                      <Typography variant="h6">{selectedBranch.supervisor_id ?? 'N/A'}</Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="caption" color="text.secondary">Total ATMs</Typography>
                      <Typography variant="h5">{branchAtms.length}</Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="caption" color="text.secondary">ATM Capacity</Typography>
                      <Typography variant="h5">{selectedBranch.capacity}</Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Card variant="outlined">
                    <CardContent>
                       <Typography variant="caption" color="text.secondary">Location</Typography>
                       <Typography variant="h5">{selectedBranch.location_region}</Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="caption" color="text.secondary">ATMs in Maintenance</Typography>
                      <Typography variant="h5">
                        {branchAtms.filter((atm) => atm.status === 'Maintenance').length}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                
              </Grid>

              <Typography variant="subtitle1" fontWeight={700}>Tracked ATM inventory</Typography>
              <List dense>
                {branchAtms.length === 0 ? (
                  <ListItem>
                    <ListItemText primary="No ATMs assigned to this branch yet." />
                  </ListItem>
                ) : (
                  branchAtms.map((atm) => (
                    <ListItem key={atm.id} divider>
                      <ListItemText
                        primary={`${atm.serial_number} · ${atm.model}`}
                        secondary={`Cash ${atm.cash_level}% · ${atm.status}`}
                      />
                    </ListItem>
                  ))
                )}
              </List>
            </Stack>
          </CardContent>
        </Card>
      ) : null}
    </Box>
  );
}
