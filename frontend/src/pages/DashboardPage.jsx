import { useEffect, useState } from 'react';
import {
  Alert,
  Box,
  CircularProgress,
  Container,
  Grid,
  Stack,
  Tab,
  Tabs,
  Typography,
} from '@mui/material';

import AppHeader from '../components/layout/AppHeader.jsx';
import ATMDataGrid from '../components/atms/ATMDataGrid.jsx';
import ServiceCallGrid from '../components/service-calls/ServiceCallGrid.jsx';
import BranchHealthPanel from '../components/analytics/BranchHealthPanel.jsx';
import ReliabilityPanel from '../components/analytics/ReliabilityPanel.jsx';
import DiscrepancyPanel from '../components/analytics/DiscrepancyPanel.jsx';
import SupervisorLoadPanel from '../components/analytics/SupervisorLoadPanel.jsx';
import LowCashPanel from '../components/analytics/LowCashPanel.jsx';
import MetricCard from '../components/dashboard/MetricCard.jsx';
import BranchDetailsPanel from '../components/branches/BranchDetailsPanel.jsx';
import UserManagementPanel from '../components/users/UserManagementPanel.jsx';
import DiagnosticReportPanel from '../components/diagnostics/DiagnosticReportPanel.jsx';
import apiClient from '../api/client.js';
import { useAuth } from '../context/AuthContext.jsx';

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const [metrics, setMetrics] = useState({
    lowCash: 0,
    totalAtms: 0,
    maintenance: 0,
    serviceCalls: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [tab, setTab] = useState(0);
  const [secondaryTab, setSecondaryTab] = useState(0);

  useEffect(() => {
    async function loadDashboardMetrics() {
      try {
        const [allAtmsRes, lowCashRes, serviceCallsRes] = await Promise.all([
          apiClient.get('/atms'),
          apiClient.get('/atms?max_cash=20'),
          apiClient.get('/service_calls'),
        ]);

        const allAtms = allAtmsRes.data;
        setMetrics({
          lowCash: lowCashRes.data.length,
          totalAtms: allAtms.length,
          maintenance: allAtms.filter((atm) => atm.status === 'Maintenance').length,
          serviceCalls: serviceCallsRes.data.length,
        });
      } catch {
        setError('Could not load CashCow dashboard metrics.');
      } finally {
        setLoading(false);
      }
    }

    loadDashboardMetrics();
  }, []);

  const roleLabel = user?.role || 'Operations Admin';
  const canManage = roleLabel === 'Operations Admin';

  return (
    <>
      <AppHeader
        username={user?.username || 'CashCow Operator'}
        role={roleLabel}
        onLogout={logout}
      />

      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Stack spacing={3}>
          <Box>
            <Typography variant="h4" fontWeight={700}>
              Branch Operations Dashboard
            </Typography>
            <Typography variant="body1" color="text.secondary">
              {roleLabel} View
            </Typography>
          </Box>

          {error && <Alert severity="error">{error}</Alert>}

          {loading ? (
            <Box display="flex" justifyContent="center" py={4}>
              <CircularProgress />
            </Box>
          ) : (
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6} md={3}>
                <MetricCard title="Low Cash ATMs" value={metrics.lowCash} tone="warning" subtitle="Below 20% cash threshold" />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <MetricCard title="Total ATMs" value={metrics.totalAtms} tone="primary" subtitle="Active inventory" />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <MetricCard title="Maintenance" value={metrics.maintenance} tone="error" subtitle="ATMs flagged for service" />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <MetricCard title="Service Calls" value={metrics.serviceCalls} tone="info" subtitle="Across the network" />
              </Grid>
            </Grid>
          )}

          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs value={tab} onChange={(_, newValue) => setTab(newValue)}>
              <Tab label="ATMs" />
              <Tab label="Service Calls" />
              <Tab label="Branches" />
              <Tab label="Users" />
              <Tab label="Reports" />
            </Tabs>
          </Box>

          {tab === 0 && (
            <Box>
              <Typography variant="h5" sx={{ mb: 2 }}>
                ATM Inventory
              </Typography>
              <ATMDataGrid onSuccess={canManage ? (message) => console.log(message) : undefined} />
            </Box>
          )}

          {tab === 1 && (
            <Box>
              <Typography variant="h5" sx={{ mb: 2 }}>
                Service Call Queue
              </Typography>
              <ServiceCallGrid />
            </Box>
          )}

          {tab === 2 && (
            <Box>
              <Typography variant="h5" sx={{ mb: 2 }}>
                Branch Details
              </Typography>
              <BranchDetailsPanel />
            </Box>
          )}

          {tab === 3 && (
            <Box>
              <Typography variant="h5" sx={{ mb: 2 }}>
                User Management
              </Typography>
              <UserManagementPanel />
            </Box>
          )}

          {tab === 4 && (
            <Box>
              <Typography variant="h5" sx={{ mb: 2 }}>
                Diagnostic Reports
              </Typography>
              <DiagnosticReportPanel />
            </Box>
          )}

          <Box sx={{ mt: 4 }}>
            <Typography variant="h5" sx={{ mb: 2 }}>
              Operations Overview
            </Typography>
            <Grid container spacing={3} alignItems="stretch">
              <Grid item xs={12} md={6} sx={{ display: 'flex' }}>
                <Box sx={{ width: '100%', display: 'flex', flexDirection: 'row', maxHeight: 450, overflowY: 'auto', pr: 1 }}>
                  <LowCashPanel />
                </Box>
              </Grid>
              <Grid item xs={12} md={6} sx={{ display: 'flex' }}>
                <Box sx={{ width: '100%', display: 'flex', flexDirection: 'row', maxHeight: 450, overflowY: 'auto', pr: 1 }}>
                  <BranchHealthPanel />
                </Box>
              </Grid>
              <Grid item xs={12} md={6} sx={{ display: 'flex' }}>
                <Box sx={{ width: '100%', display: 'flex', flexDirection: 'row', maxHeight: 450, overflowY: 'auto', pr: 1 }}>
                  <ReliabilityPanel />
                </Box>
              </Grid>
              <Grid item xs={12} md={6} sx={{ display: 'flex' }}>
                <Box sx={{ width: '100%', display: 'flex', flexDirection: 'row', maxHeight: 450, overflowY: 'auto', pr: 1 }}>
                  <DiscrepancyPanel />
                </Box>
              </Grid>
              <Grid item xs={12} md={6} sx={{ display: 'flex' }}>
                <Box sx={{ width: '100%', display: 'flex', flexDirection: 'row', maxHeight: 450, overflowY: 'auto', pr: 1 }}>
                  <SupervisorLoadPanel supervisorId={1} />
                </Box>
              </Grid>
            </Grid>
          </Box>
        </Stack>
      </Container>
    </>
  );
}
