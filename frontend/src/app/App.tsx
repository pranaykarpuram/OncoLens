import { BrowserRouter, Routes, Route, Navigate } from 'react-router';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { LoginScreen } from './screens/LoginScreen';
import { ReviewQueueScreen } from './screens/ReviewQueueScreen';
import { PatientsScreen } from './screens/PatientsScreen';
import { PatientWorkspaceScreen } from './screens/PatientWorkspaceScreen';
import { ReportUploadScreen } from './screens/ReportUploadScreen';
import { SearchScreen } from './screens/SearchScreen';
import { TumorBoardScreen } from './screens/TumorBoardScreen';
import { AdminScreen } from './screens/AdminScreen';

function DashboardLayout({ title, subtitle, children }: { title: string; subtitle?: string; children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen bg-[#F8FAFC]">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header title={title} subtitle={subtitle} />
        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LoginScreen />} />
        <Route path="/queue" element={
          <DashboardLayout title="Review Queue" subtitle="Patients with new reports, changed trends, or missing follow-up data">
            <ReviewQueueScreen />
          </DashboardLayout>
        } />
        <Route path="/patients" element={
          <DashboardLayout title="Patients" subtitle="Search and review patient charts">
            <PatientsScreen />
          </DashboardLayout>
        } />
        <Route path="/patient/:id" element={
          <DashboardLayout title="Patient Review Workspace" subtitle="Evidence-first chart review">
            <PatientWorkspaceScreen />
          </DashboardLayout>
        } />
        <Route path="/intake" element={
          <DashboardLayout title="Report Intake" subtitle="Upload and extract clinical data">
            <ReportUploadScreen />
          </DashboardLayout>
        } />
        <Route path="/search" element={
          <DashboardLayout title="Evidence Search" subtitle="Search across all patients and documents">
            <SearchScreen />
          </DashboardLayout>
        } />
        <Route path="/tumor-board" element={
          <DashboardLayout title="Tumor Board" subtitle="Generate case briefs for tumor board meetings">
            <TumorBoardScreen />
          </DashboardLayout>
        } />
        <Route path="/admin" element={
          <DashboardLayout title="Admin" subtitle="System operations and team management">
            <AdminScreen />
          </DashboardLayout>
        } />
        <Route path="*" element={<Navigate to="/queue" replace />} />
      </Routes>
    </BrowserRouter>
  );
}