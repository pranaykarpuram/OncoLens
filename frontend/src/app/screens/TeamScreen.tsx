import { UserPlus, Mail, Shield } from 'lucide-react';

const teamMembers = [
  { name: 'Dr. Alex Morgan', role: 'Doctor', department: 'Oncology', access: 'Full clinical access', email: 'a.morgan@hospital.com', lastActive: '2 hours ago', initials: 'AM', color: 'from-blue-600 to-purple-600' },
  { name: 'Jamie Lee', role: 'Nurse', department: 'Oncology', access: 'Upload + notes', email: 'j.lee@hospital.com', lastActive: '5 hours ago', initials: 'JL', color: 'from-green-600 to-teal-600' },
  { name: 'Priya Shah', role: 'Admin', department: 'Operations', access: 'Patient management', email: 'p.shah@hospital.com', lastActive: '1 day ago', initials: 'PS', color: 'from-purple-600 to-pink-600' },
  { name: 'Dr. Sarah Chen', role: 'Doctor', department: 'Oncology', access: 'Full clinical access', email: 's.chen@hospital.com', lastActive: '3 hours ago', initials: 'SC', color: 'from-cyan-600 to-blue-600' },
  { name: 'Marcus Williams', role: 'Nurse', department: 'Oncology', access: 'Upload + notes', email: 'm.williams@hospital.com', lastActive: '6 hours ago', initials: 'MW', color: 'from-amber-600 to-orange-600' },
];

export function TeamScreen() {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-3xl p-6 border border-[#E2E8F0]">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="font-semibold text-[#0F172A]">Team Members</h3>
            <p className="text-sm text-[#64748B]">{teamMembers.length} active users</p>
          </div>
          <button className="px-4 py-2 bg-[#2563EB] text-white rounded-xl font-medium hover:bg-[#1d4ed8] transition-colors flex items-center gap-2">
            <UserPlus className="w-4 h-4" />
            Add member
          </button>
        </div>

        <div className="space-y-3">
          {teamMembers.map((member) => (
            <div key={member.email} className="p-5 rounded-3xl border border-[#E2E8F0] hover:border-[#2563EB] hover:bg-[#F6FAFF] transition-all">
              <div className="flex items-center gap-4">
                <div className={`w-14 h-14 rounded-full bg-gradient-to-br ${member.color} flex items-center justify-center text-white font-semibold text-lg flex-shrink-0`}>
                  {member.initials}
                </div>

                <div className="flex-1 grid grid-cols-5 gap-4 items-center">
                  <div>
                    <p className="font-semibold text-[#0F172A]">{member.name}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <Mail className="w-3 h-3 text-[#94A3B8]" />
                      <p className="text-xs text-[#64748B]">{member.email}</p>
                    </div>
                  </div>

                  <div>
                    <p className="text-xs uppercase text-[#94A3B8] mb-1">Role</p>
                    <p className="text-sm font-medium text-[#0F172A]">{member.role}</p>
                  </div>

                  <div>
                    <p className="text-xs uppercase text-[#94A3B8] mb-1">Department</p>
                    <p className="text-sm text-[#0F172A]">{member.department}</p>
                  </div>

                  <div>
                    <p className="text-xs uppercase text-[#94A3B8] mb-1">Access Level</p>
                    <div className="flex items-center gap-2">
                      <Shield className={`w-4 h-4 ${member.access.includes('Full') ? 'text-green-600' : 'text-blue-600'}`} />
                      <p className="text-sm text-[#0F172A]">{member.access}</p>
                    </div>
                  </div>

                  <div className="text-right">
                    <p className="text-xs uppercase text-[#94A3B8] mb-1">Last Active</p>
                    <p className="text-sm text-[#0F172A]">{member.lastActive}</p>
                  </div>
                </div>

                <div className="flex gap-2 flex-shrink-0">
                  <button className="px-4 py-2 text-sm font-medium text-[#2563EB] hover:bg-[#EAF4FF] rounded-xl transition-colors">
                    Edit
                  </button>
                  <button className="px-4 py-2 text-sm font-medium text-[#64748B] hover:bg-[#F6FAFF] rounded-xl transition-colors">
                    Remove
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        <div className="bg-white rounded-3xl p-6 border border-[#E2E8F0]">
          <h4 className="font-semibold text-[#0F172A] mb-4">Team Stats</h4>
          <div className="space-y-3">
            <div className="p-4 rounded-2xl bg-[#F6FAFF]">
              <p className="text-xs uppercase text-[#94A3B8] mb-1">Total Members</p>
              <p className="text-2xl font-semibold text-[#0F172A]">{teamMembers.length}</p>
            </div>
            <div className="p-4 rounded-2xl bg-blue-50">
              <p className="text-xs uppercase text-[#94A3B8] mb-1">Doctors</p>
              <p className="text-2xl font-semibold text-blue-600">{teamMembers.filter(m => m.role === 'Doctor').length}</p>
            </div>
            <div className="p-4 rounded-2xl bg-green-50">
              <p className="text-xs uppercase text-[#94A3B8] mb-1">Nurses</p>
              <p className="text-2xl font-semibold text-green-600">{teamMembers.filter(m => m.role === 'Nurse').length}</p>
            </div>
            <div className="p-4 rounded-2xl bg-purple-50">
              <p className="text-xs uppercase text-[#94A3B8] mb-1">Admins</p>
              <p className="text-2xl font-semibold text-purple-600">{teamMembers.filter(m => m.role === 'Admin').length}</p>
            </div>
          </div>
        </div>

        <div className="col-span-2 bg-white rounded-3xl p-6 border border-[#E2E8F0]">
          <h4 className="font-semibold text-[#0F172A] mb-4">Access Levels</h4>

          <div className="space-y-4">
            <div className="p-5 rounded-2xl bg-green-50 border border-green-100">
              <div className="flex items-start gap-3 mb-2">
                <Shield className="w-5 h-5 text-green-600 mt-0.5" />
                <div className="flex-1">
                  <p className="font-semibold text-green-700 mb-1">Full Clinical Access</p>
                  <p className="text-sm text-green-600">
                    View all patient data, upload reports, add clinical notes, export summaries, manage insight flags
                  </p>
                </div>
              </div>
              <p className="text-xs text-green-600 mt-3">{teamMembers.filter(m => m.access.includes('Full')).length} users with this access</p>
            </div>

            <div className="p-5 rounded-2xl bg-blue-50 border border-blue-100">
              <div className="flex items-start gap-3 mb-2">
                <Shield className="w-5 h-5 text-blue-600 mt-0.5" />
                <div className="flex-1">
                  <p className="font-semibold text-blue-700 mb-1">Upload + Notes</p>
                  <p className="text-sm text-blue-600">
                    Upload reports, add clinical notes, view assigned patients
                  </p>
                </div>
              </div>
              <p className="text-xs text-blue-600 mt-3">{teamMembers.filter(m => m.access.includes('Upload')).length} users with this access</p>
            </div>

            <div className="p-5 rounded-2xl bg-purple-50 border border-purple-100">
              <div className="flex items-start gap-3 mb-2">
                <Shield className="w-5 h-5 text-purple-600 mt-0.5" />
                <div className="flex-1">
                  <p className="font-semibold text-purple-700 mb-1">Patient Management</p>
                  <p className="text-sm text-purple-600">
                    Manage patient records, team members, system settings
                  </p>
                </div>
              </div>
              <p className="text-xs text-purple-600 mt-3">{teamMembers.filter(m => m.access.includes('Patient management')).length} user with this access</p>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-blue-50 rounded-3xl p-6 border border-blue-100">
        <h4 className="font-semibold text-[#0F172A] mb-3">Security Note</h4>
        <p className="text-sm text-blue-700">
          All team member actions are logged for compliance and audit purposes. Access changes take effect immediately.
        </p>
      </div>
    </div>
  );
}
